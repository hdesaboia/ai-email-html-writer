from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schemas.user import UserCreate
from app.main import app
from app.core.security import create_access_token
from app.api import deps

client = TestClient(app)

def get_test_db(test_db: Session):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    return override_get_db

def test_create_user(db: Session) -> None:
    email = "test@example.com"
    password = "testpass123"
    user_in = UserCreate(email=email, password=password)
    user = crud_user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")

def test_authenticate_user(db: Session) -> None:
    email = "test@example.com"
    password = "testpass123"
    # Create user first
    user_in = UserCreate(email=email, password=password)
    crud_user.create(db, obj_in=user_in)
    # Then try to authenticate
    user = crud_user.authenticate(db, email=email, password=password)
    assert user
    assert user.email == email

def test_not_authenticate_user(db: Session) -> None:
    email = "test@example.com"
    password = "wrongpass"
    # Create user first
    user_in = UserCreate(email=email, password="testpass123")  # Different password
    crud_user.create(db, obj_in=user_in)
    # Then try to authenticate with wrong password
    user = crud_user.authenticate(db, email=email, password=password)
    assert user is None

def test_get_current_user(db: Session) -> None:
    # Override the database dependency
    app.dependency_overrides[deps.get_db] = get_test_db(db)
    
    try:
        email = "test@example.com"
        password = "testpass123"
        # Create user first
        user_in = UserCreate(email=email, password=password)
        user = crud_user.create(db, obj_in=user_in)
        # Then try to authenticate
        authenticated_user = crud_user.authenticate(db, email=email, password=password)
        assert authenticated_user
        # Create access token
        access_token = create_access_token(subject=user.id)
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == email
    finally:
        # Clean up the dependency override
        app.dependency_overrides.clear() 