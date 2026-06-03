from core.database import Base, engine
from models.user import User
from models.upload_history import UploadHistory
from models.statement_upload import StatementUpload
from models.transaction import Transaction


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_db()
