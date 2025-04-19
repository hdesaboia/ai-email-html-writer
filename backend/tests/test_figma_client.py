import pytest
from unittest.mock import patch, MagicMock
from app.services.figma_client import FigmaClient, FigmaFile, FigmaNode


@pytest.fixture
def figma_client():
    return FigmaClient(access_token="test_token")


@pytest.fixture
def mock_figma_response():
    return {
        "name": "Test File",
        "lastModified": "2023-01-01T00:00:00Z",
        "thumbnailUrl": "https://example.com/thumbnail.png",
        "version": "1.0"
    }


@pytest.fixture
def mock_nodes_response():
    return {
        "nodes": {
            "1:1": {
                "id": "1:1",
                "name": "Frame 1",
                "type": "FRAME",
                "children": [
                    {
                        "id": "1:2",
                        "name": "Component 1",
                        "type": "COMPONENT",
                        "style": {"color": "#000000"},
                        "absoluteBoundingBox": {"x": 0, "y": 0, "width": 100, "height": 100}
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_images_response():
    return {
        "images": {
            "1:1": "https://example.com/image1.png",
            "1:2": "https://example.com/image2.png"
        }
    }


def test_get_file(figma_client, mock_figma_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_figma_response
        )
        
        file = figma_client.get_file("test_key")
        
        assert isinstance(file, FigmaFile)
        assert file.name == "Test File"
        assert file.last_modified == "2023-01-01T00:00:00Z"
        assert file.thumbnail_url == "https://example.com/thumbnail.png"
        assert file.version == "1.0"


def test_get_file_nodes(figma_client, mock_nodes_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_nodes_response
        )
        
        nodes = figma_client.get_file_nodes("test_key")
        
        assert isinstance(nodes, dict)
        assert "1:1" in nodes
        assert isinstance(nodes["1:1"], FigmaNode)
        assert nodes["1:1"].name == "Frame 1"
        assert nodes["1:1"].type == "FRAME"
        assert len(nodes["1:1"].children) == 1
        assert nodes["1:1"].children[0].name == "Component 1"


def test_get_image_urls(figma_client, mock_images_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_images_response
        )
        
        image_urls = figma_client.get_image_urls("test_key", ["1:1", "1:2"])
        
        assert isinstance(image_urls, dict)
        assert image_urls["1:1"] == "https://example.com/image1.png"
        assert image_urls["1:2"] == "https://example.com/image2.png"


def test_get_component_sets(figma_client, mock_nodes_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: mock_nodes_response
        )
        
        component_sets = figma_client.get_component_sets("test_key")
        
        assert isinstance(component_sets, dict)
        # In this case, we don't have any component sets in the mock data
        assert len(component_sets) == 0


def test_get_file_error(figma_client):
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(
            status_code=404,
            raise_for_status=MagicMock(side_effect=Exception("Not Found"))
        )
        
        with pytest.raises(Exception):
            figma_client.get_file("invalid_key") 