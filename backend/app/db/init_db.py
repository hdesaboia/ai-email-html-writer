from sqlalchemy import create_engine
from app.db.base import Base
from app.db.session import SQLALCHEMY_DATABASE_URL
from app.models.user import User  # Import the User model
from app.models.email_template import EmailTemplate  # Import the EmailTemplate model

def init_db() -> None:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db() 