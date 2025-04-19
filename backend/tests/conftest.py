import pytest
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Dict, Any
from app.core.config import settings

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.db.base import Base
from app.models.user import User
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )

@pytest.fixture(scope="session")
def test_figma_file_key() -> str:
    """Return a test Figma file key."""
    return os.getenv("TEST_FIGMA_FILE_KEY", "5dizNnH3l97v7YJN2dgaFl")

@pytest.fixture(scope="session")
def test_figma_node_id() -> str:
    """Return a test Figma node ID."""
    return os.getenv("TEST_FIGMA_NODE_ID", "13874:3894")

@pytest.fixture(scope="session")
def figma_access_token() -> str:
    """Return the Figma access token."""
    token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not token:
        pytest.skip("FIGMA_ACCESS_TOKEN environment variable not set")
    return token

@pytest.fixture
def figma_client(figma_access_token):
    """Create a Figma client with the configured access token."""
    from app.services.figma_client import FigmaClient
    return FigmaClient(access_token=figma_access_token)

@pytest.fixture(scope="session")
def test_figma_node_ids() -> Dict[str, str]:
    """Return a dictionary of test node IDs for different element types.
    
    These should be real node IDs from the test Figma file.
    """
    return {
        "frame": "frame_node_id",
        "text": "text_node_id",
        "image": "image_node_id",
        "component": "component_node_id"
    }

@pytest.fixture(scope="session")
def figma_test_data() -> Dict[str, Any]:
    """Return test data for Figma API responses.
    
    This data should match the structure of real Figma API responses.
    """
    return {
        "file": {
            "name": "Test File",
            "lastModified": "2023-01-01T00:00:00Z",
            "thumbnailUrl": "https://example.com/thumbnail.png",
            "version": "1.0"
        },
        "nodes": {
            "1:1": {
                "id": "1:1",
                "name": "Test Frame",
                "type": "FRAME",
                "children": [
                    {
                        "id": "1:2",
                        "name": "Test Text",
                        "type": "TEXT",
                        "style": {
                            "color": {"r": 0, "g": 0, "b": 0, "a": 1},
                            "fontSize": 16,
                            "fontFamily": "Arial",
                            "textAlign": "left"
                        }
                    },
                    {
                        "id": "1:3",
                        "name": "Test Image",
                        "type": "IMAGE",
                        "absoluteBoundingBox": {
                            "x": 0,
                            "y": 0,
                            "width": 100,
                            "height": 100
                        }
                    }
                ]
            }
        },
        "images": {
            "1:3": "https://example.com/image.png"
        }
    } 