from datetime import date
from pathlib import Path
import tempfile

from fastapi import HTTPException, UploadFile, status
import pandas as pd
from sqlalchemy.orm import Session

from models.statement_upload import StatementUpload
from models.transaction import Transaction
from models.upload_history import UploadHistory
from models.user import User
from preprocessing.opay import opay_preprocessing
from preprocessing.gtbank import gtbank_preprocessing
from preprocessing.moniepoint import moniepoint_preprocessing
from preprocessing.ecobank import ecobank_preprocessing
from preprocessing.zenithbank import zenithbank_preprocessing

BANK_PROCESSORS = {
    "OPay": opay_preprocessing,
    "GTBank": gtbank_preprocessing,
    "Moniepoint": moniepoint_preprocessing,
    "Ecobank": ecobank_preprocessing,
    "Zenith Bank": zenithbank_preprocessing,
}

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf"}


def _validate_file_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return suffix


async def _write_upload_to_tempfile(file: UploadFile, suffix: str) -> Path:
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="transacai_raw_")
    temp_path = Path(temp.name)
    try:
        with temp:
            content = await file.read()
            temp.write(content)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    return temp_path


def _normalise_processed_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["Date", "Category", "Description", "Debit", "Credit", "Balance", "User", "Bank"]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Processed data is missing required columns: {', '.join(missing)}")

    cleaned = df[required_columns].copy()
    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce").dt.date
    cleaned["Debit"] = pd.to_numeric(cleaned["Debit"], errors="coerce").fillna(0).astype(float)
    cleaned["Credit"] = pd.to_numeric(cleaned["Credit"], errors="coerce").fillna(0).astype(float)
    cleaned["Balance"] = pd.to_numeric(cleaned["Balance"], errors="coerce").fillna(0).astype(float)
    cleaned["Category"] = cleaned["Category"].fillna("Uncategorized").astype(str)
    cleaned["Description"] = cleaned["Description"].fillna("").astype(str)
    cleaned["User"] = cleaned["User"].where(cleaned["User"].notna(), None)
    cleaned["Bank"] = cleaned["Bank"].fillna("").astype(str)
    cleaned = cleaned.dropna(subset=["Date"])

    if cleaned.empty:
        raise ValueError("Processed data contains no valid dated transactions.")

    return cleaned


def _find_app_user_id(db: Session, user_name: str) -> int | None:
    user = db.query(User).filter(User.first_name == user_name).first()
    return user.id if user else None


def _save_processed_dataframe(
    db: Session,
    df: pd.DataFrame,
    user_name: str,
    bank_name: str,
    original_filename: str,
) -> tuple[StatementUpload, UploadHistory]:
    cleaned = _normalise_processed_dataframe(df)
    user_id = _find_app_user_id(db, user_name)
    statement_user_name = None
    if not cleaned["User"].dropna().empty:
        statement_user_name = str(cleaned["User"].dropna().iloc[0]).strip() or None
    min_date = cleaned["Date"].min()
    max_date = cleaned["Date"].max()
    date_range = f"{min_date} to {max_date}"

    db.query(StatementUpload).filter(
        StatementUpload.user_name == user_name,
        StatementUpload.is_current.is_(True),
    ).update({"is_current": False}, synchronize_session=False)
    db.query(UploadHistory).filter(
        UploadHistory.user_name == user_name,
        UploadHistory.is_active.is_(True),
    ).update({"is_active": False}, synchronize_session=False)

    upload = StatementUpload(
        user_id=user_id,
        user_name=user_name,
        bank_name=bank_name,
        original_filename=original_filename,
        statement_user_name=statement_user_name,
        row_count=len(cleaned),
        is_current=True,
    )
    db.add(upload)
    db.flush()

    history = UploadHistory(
        user_id=user_id,
        user_name=user_name,
        original_filename=original_filename,
        processed_filename=str(upload.id),
        processed_file_path=f"db://statement_uploads/{upload.id}",
        bank_name=bank_name,
        row_count=len(cleaned),
        date_range=date_range,
        is_active=True,
    )
    db.add(history)

    transactions = [
        Transaction(
            upload_id=upload.id,
            user_id=user_id,
            user_name=user_name,
            date=row["Date"],
            category=row["Category"],
            description=row["Description"],
            debit=row["Debit"],
            credit=row["Credit"],
            balance=row["Balance"],
            statement_user=None if pd.isna(row["User"]) else str(row["User"]),
            bank=row["Bank"] or bank_name,
        )
        for _, row in cleaned.iterrows()
    ]
    db.add_all(transactions)
    db.commit()
    db.refresh(upload)
    db.refresh(history)
    return upload, history


async def process_bank_statement(
    file: UploadFile,
    user_name: str,
    bank_name: str,
    db: Session,
) -> dict:
    # Validate bank
    processor = BANK_PROCESSORS.get(bank_name)
    if processor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported bank '{bank_name}'. Supported: {', '.join(BANK_PROCESSORS.keys())}"
        )

    # Validate file extension
    ext = _validate_file_extension(file.filename or "")

    # Save uploaded file to an OS-managed temporary path because the bank parsers expect file paths.
    temp_path = await _write_upload_to_tempfile(file, ext)

    try:
        # Run the bank-specific preprocessing
        df = processor(str(temp_path), user_name, bank_name)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process {bank_name} statement: {str(e)}"
        )

    try:
        upload, history = _save_processed_dataframe(
            db=db,
            df=df,
            user_name=user_name,
            bank_name=bank_name,
            original_filename=file.filename or "statement",
        )
    except Exception as e:
        db.rollback()
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to save processed transactions: {str(e)}"
        )

    # Clean up temp file
    if temp_path.exists():
        temp_path.unlink()

    # Build response
    cleaned = _normalise_processed_dataframe(df)
    min_date: date | str = cleaned["Date"].min() if not cleaned.empty else "N/A"
    max_date: date | str = cleaned["Date"].max() if not cleaned.empty else "N/A"
    categories = sorted(cleaned["Category"].dropna().unique().tolist())

    return {
        "message": f"Successfully processed {bank_name} statement",
        "user_name": user_name,
        "statement_user_name": upload.statement_user_name,
        "bank_name": bank_name,
        "file_path": history.processed_file_path,
        "row_count": upload.row_count,
        "date_range": f"{min_date} to {max_date}",
        "categories": categories,
        "original_filename": file.filename or "statement",
        "processed_filename": str(history.id),
        "processed_file_path": history.processed_file_path,
    }
