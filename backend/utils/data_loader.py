import pandas as pd
from fastapi import HTTPException, status

from core.database import SessionLocal
from models.statement_upload import StatementUpload
from models.transaction import Transaction


EXPECTED_COLUMNS = [
    "Date",
    "Category",
    "Description",
    "Debit",
    "Credit",
    "Balance",
    "User",
    "Bank",
]


def load_user_dataframe(user_name: str) -> pd.DataFrame:
    db = SessionLocal()
    try:
        upload = (
            db.query(StatementUpload)
            .filter(StatementUpload.user_name == user_name, StatementUpload.is_current.is_(True))
            .order_by(StatementUpload.uploaded_at.desc(), StatementUpload.id.desc())
            .first()
        )
        if upload is None:
            upload = (
                db.query(StatementUpload)
                .filter(StatementUpload.user_name == user_name)
                .order_by(StatementUpload.uploaded_at.desc(), StatementUpload.id.desc())
                .first()
            )

        if upload is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No preprocessed dataset found for user '{user_name}'.",
            )

        rows = (
            db.query(Transaction)
            .filter(Transaction.upload_id == upload.id)
            .order_by(Transaction.date.asc(), Transaction.id.asc())
            .all()
        )
    finally:
        db.close()

    df = pd.DataFrame(
        [
            {
                "Date": row.date,
                "Category": row.category,
                "Description": row.description,
                "Debit": row.debit,
                "Credit": row.credit,
                "Balance": row.balance,
                "User": row.statement_user,
                "Bank": row.bank,
            }
            for row in rows
        ],
        columns=EXPECTED_COLUMNS,
    )

    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dataset is missing required columns: {', '.join(missing)}",
        )

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0)
    df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0)
    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce").fillna(0)
    df = df.dropna(subset=["Date"]).sort_values("Date")

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dataset for user '{user_name}' contains no valid dated rows.",
        )

    return df
