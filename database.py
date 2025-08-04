# Update database.py with better error handling
import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_engine():
    try:
        return create_engine(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

def execute_query(query: str):
    try:
        if not query.strip():
            return []
            
        engine = get_db_engine()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            return [dict(row) for row in result.mappings()]
    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []