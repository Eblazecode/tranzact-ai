# create_tables.py
from core.database import Base, engine

# import models
from models.user import *
from models.transaction import *
from models.upload_history import *
from models.statement_upload import *

Base.metadata.create_all(bind=engine)

print("Tables created successfully")