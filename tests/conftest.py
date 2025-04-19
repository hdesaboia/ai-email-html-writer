import pytest
import os
from app.clients.figma_client import FigmaClient

@pytest.fixture
def figma_client():
    """Create a FigmaClient instance for testing."""
    access_token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not access_token:
        pytest.skip("FIGMA_ACCESS_TOKEN environment variable not set")
    return FigmaClient(access_token=access_token) 