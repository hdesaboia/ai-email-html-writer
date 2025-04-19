import pytest
import requests
import os
from app.clients.figma_client import FigmaClient, FigmaClientError

@pytest.fixture
def figma_client():
    """Create a FigmaClient instance for testing."""
    base_url = "https://api.figma.com"
    session = requests.Session()
    session.headers.update({
        "X-Figma-Token": os.getenv("FIGMA_ACCESS_TOKEN")
    })
    return FigmaClient(base_url=base_url, session=session)

def test_figma_design_access(figma_client):
    """Test accessing a Figma design with a valid node ID."""
    file_key = "5dizNnH3l97v7YJN2dgaFl"
    node_id = "13874:3894"
    
    try:
        node_data = figma_client.get_node(file_key, node_id)
        print(f"Successfully accessed Figma design: {node_data}")
        assert node_data is not None
        assert isinstance(node_data, dict)
    except FigmaClientError as e:
        print(f"Failed to access Figma design: {str(e)}")
        raise

def test_figma_design_invalid_node(figma_client):
    """Test handling of an invalid node ID."""
    file_key = "5dizNnH3l97v7YJN2dgaFl"
    node_id = "invalid:node:id"
    
    with pytest.raises(FigmaClientError):
        figma_client.get_node(file_key, node_id) 