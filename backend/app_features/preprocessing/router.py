from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .schemas import PreprocessingResponse, SelectUploadRequest, UploadHistoryResponse
from .service import process_bank_statement
from core.database import get_db
from models.statement_upload import StatementUpload
from models.upload_history import UploadHistory
from utils.data_loader import load_user_dataframe


router = APIRouter(prefix="/api/preprocess", tags=["preprocessing"])

def _format_upload_item(history: UploadHistory) -> dict:
    uploaded_at = history.uploaded_at

    return {
        "filename": str(history.id),
        "display_name": f"{history.bank_name} statement",
        "bank_name": history.bank_name,
        "uploaded_at": uploaded_at.isoformat(),
        "uploaded_date": uploaded_at.strftime("%b %d, %Y"),
        "uploaded_time": uploaded_at.strftime("%I:%M %p").lstrip("0"),
        "is_current": history.is_active,
    }


@router.post("/upload", response_model=PreprocessingResponse)
async def upload_bank_statement(
    file: UploadFile = File(..., description="Bank statement file (CSV, Excel, or PDF)"),
    user_name: str = Form(..., description="Full name of the user"),
    bank_name: str = Form(..., description="Bank name: OPay, GTBank, Moniepoint, Ecobank, Zenith Bank"),
    db: Session = Depends(get_db),
) -> PreprocessingResponse:
    """Upload and preprocess a bank statement."""
    result = await process_bank_statement(file, user_name, bank_name, db)
    return result


@router.get("/supported-banks")
async def get_supported_banks():
    """Return list of supported banks and their file formats."""
    return {
        "banks": [
            {"name": "OPay", "formats": ["csv", "xlsx", "xls"]},
            {"name": "GTBank", "formats": ["csv", "xlsx", "xls", "pdf"]},
            {"name": "Moniepoint", "formats": ["csv", "xlsx", "xls"]},
            {"name": "Ecobank", "formats": ["csv", "xlsx", "xls"]},
            {"name": "Zenith Bank", "formats": ["csv", "xlsx", "xls", "pdf"]}
        ]
    }


@router.get("/uploads", response_model=UploadHistoryResponse)
async def get_upload_history(user_name: str, db: Session = Depends(get_db)) -> UploadHistoryResponse:
    """Return previous processed statement uploads for a user."""
    history_rows = (
        db.query(UploadHistory)
        .filter(UploadHistory.user_name == user_name)
        .order_by(UploadHistory.uploaded_at.desc(), UploadHistory.id.desc())
        .all()
    )
    uploads = [_format_upload_item(history) for history in history_rows]
    return UploadHistoryResponse(uploads=uploads)


@router.post("/uploads/select", response_model=PreprocessingResponse)
async def select_upload(request: SelectUploadRequest, db: Session = Depends(get_db)) -> PreprocessingResponse:
    """Promote a previous upload to the canonical dataset used by the dashboard."""
    try:
        history_id = int(request.filename)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected upload was not found.",
        )

    selected_history = (
        db.query(UploadHistory)
        .filter(UploadHistory.id == history_id, UploadHistory.user_name == request.user_name)
        .first()
    )
    if selected_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected upload was not found.",
        )

    try:
        upload_id = int(selected_history.processed_filename)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selected upload history is not linked to a transaction dataset.",
        )

    selected_upload = (
        db.query(StatementUpload)
        .filter(StatementUpload.id == upload_id, StatementUpload.user_name == request.user_name)
        .first()
    )
    if selected_upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected upload was not found.",
        )

    db.query(StatementUpload).filter(
        StatementUpload.user_name == request.user_name,
        StatementUpload.is_current.is_(True),
    ).update({"is_current": False}, synchronize_session=False)
    db.query(UploadHistory).filter(
        UploadHistory.user_name == request.user_name,
        UploadHistory.is_active.is_(True),
    ).update({"is_active": False}, synchronize_session=False)
    selected_upload.is_current = True
    selected_history.is_active = True
    db.commit()
    db.refresh(selected_upload)
    db.refresh(selected_history)

    df = load_user_dataframe(request.user_name)
    min_date = df["Date"].min() if not df.empty and "Date" in df.columns else "N/A"
    max_date = df["Date"].max() if not df.empty and "Date" in df.columns else "N/A"
    categories = sorted(df["Category"].dropna().unique().tolist()) if "Category" in df.columns else []
    bank_name = selected_upload.bank_name

    return PreprocessingResponse(
        message="Selected previous upload successfully",
        user_name=request.user_name,
        statement_user_name=selected_upload.statement_user_name,
        bank_name=bank_name,
        file_path=selected_history.processed_file_path,
        row_count=len(df),
        date_range=f"{min_date} to {max_date}",
        categories=categories,
    )


@router.get("/processed-data/{user_name}")
async def get_processed_data(user_name: str):
    """Get preprocessed transaction data for dashboard."""
    try:
        df = load_user_dataframe(user_name)
        
        # Calculate metrics as per transac_ai_model.py
        total_credit = df["Credit"].sum()
        total_debit = df["Debit"].sum()
        current_balance = df["Balance"].iloc[-1] if not df.empty else 0
        net_position = total_credit - total_debit
        
        # Category spending
        category_spending = df.groupby("Category")["Debit"].sum().reset_index()
        category_spending = category_spending.sort_values("Debit", ascending=False)
        
        # Transaction history - Description, Category, Date, Balance
        transactions = df[["Description", "Category", "Date", "Balance"]].head(50).to_dict("records")
        
        # Highest/Lowest spends
        debit_df = df[df["Debit"] > 0]
        highest_spend = debit_df.nlargest(1, "Debit")
        lowest_spend = debit_df.nsmallest(1, "Debit")
        
        return {
            "user_name": user_name,
            "total_balance": current_balance,
            "net_position": net_position,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "category_spending": category_spending.to_dict("records"),
            "transactions": transactions,
            "highest_spend": {
                "description": highest_spend.iloc[0]["Description"] if not highest_spend.empty else "",
                "category": highest_spend.iloc[0]["Category"] if not highest_spend.empty else "",
                "amount": highest_spend.iloc[0]["Debit"] if not highest_spend.empty else 0,
                "date": highest_spend.iloc[0]["Date"] if not highest_spend.empty else ""
            },
            "lowest_spend": {
                "description": lowest_spend.iloc[0]["Description"] if not lowest_spend.empty else "",
                "category": lowest_spend.iloc[0]["Category"] if not lowest_spend.empty else "",
                "amount": lowest_spend.iloc[0]["Debit"] if not lowest_spend.empty else 0,
                "date": lowest_spend.iloc[0]["Date"] if not lowest_spend.empty else ""
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading processed data: {str(e)}"
        )
