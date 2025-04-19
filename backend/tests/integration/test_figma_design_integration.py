import pytest
import os
import time
import requests
from app.services.figma_client import FigmaClient
from app.services.figma_to_html import FigmaToHTMLConverter
from app.core.config import settings
from app.core.exceptions import FigmaAPIError, FigmaValidationError, FigmaConversionError

# Test configuration
TEST_FIGMA_FILE_KEY = "5dizNnH3l97v7YJN2dgaFl"
TEST_NODE_ID = "13874:3894"
REQUEST_TIMEOUT = 30  # seconds

@pytest.fixture
def figma_client():
    """Create a Figma client with the configured access token."""
    access_token = os.getenv("FIGMA_ACCESS_TOKEN")
    if not access_token:
        pytest.skip("FIGMA_ACCESS_TOKEN environment variable not set")
    
    print(f"Using Figma access token: {access_token[:10]}...")  # Show first 10 chars for security
    
    # Test token validity first
    try:
        response = requests.get(
            "https://api.figma.com/v1/me",
            headers={"X-Figma-Token": access_token},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print("Figma access token is valid")
    except requests.exceptions.RequestException as e:
        print(f"Token validation error: {str(e)}")
        pytest.skip(f"Invalid Figma access token: {str(e)}")
    
    return FigmaClient(access_token=access_token)

@pytest.fixture
def figma_to_html(figma_client):
    """Create a Figma to HTML converter with the Figma client."""
    return FigmaToHTMLConverter(figma_client=figma_client)

def find_node_by_name(nodes, name):
    """Recursively find a node by its name."""
    for node in nodes.values():
        if node.name == name:
            return node
        if node.children:
            found = find_node_by_name({child.id: child for child in node.children}, name)
            if found:
                return found
    return None

def get_target_node(figma_client):
    """Get the target node (Email Template) from the Figma file."""
    print("Getting Figma file...")
    start_time = time.time()
    
    # Get the file first
    file = figma_client.get_file(TEST_FIGMA_FILE_KEY)
    if not file:
        pytest.skip("Failed to get Figma file")
    print(f"Got file in {time.time() - start_time:.2f}s: {file.name}")
    
    # Get the root node
    print("Getting root node...")
    start_time = time.time()
    nodes = figma_client.get_file_nodes(TEST_FIGMA_FILE_KEY, node_ids=["0:0"])
    if not nodes:
        pytest.skip("Failed to get root node")
    print(f"Got root node in {time.time() - start_time:.2f}s")
    
    # Find the Email Template node
    print("Finding Email Template node...")
    target_node = find_node_by_name(nodes, "Email Template")
    if not target_node:
        pytest.skip("Email Template node not found in the file")
    print(f"Found target node: {target_node.name} (id: {target_node.id})")
    
    return target_node

@pytest.mark.integration
def test_figma_design_access(figma_client):
    """Test accessing the specific Figma design node."""
    try:
        # Test file access
        print(f"Testing access to Figma file: {TEST_FIGMA_FILE_KEY}")
        start_time = time.time()
        file = figma_client.get_file(TEST_FIGMA_FILE_KEY)
        assert file is not None, "Failed to get Figma file"
        print(f"Successfully accessed file in {time.time() - start_time:.2f}s: {file.name}")
        
        assert file.key == TEST_FIGMA_FILE_KEY, f"File key mismatch: expected {TEST_FIGMA_FILE_KEY}, got {file.key}"
        assert file.name, "File name is empty"
        assert file.version, "File version is empty"
        
        # Print file details for debugging
        print(f"File details:")
        print(f"- Name: {file.name}")
        print(f"- Version: {file.version}")
        print(f"- Last Modified: {file.last_modified}")
        if file.thumbnail_url:
            print(f"- Thumbnail URL: {file.thumbnail_url}")
        
        # Respect rate limits
        time.sleep(1)  # Wait between API calls
        
    except FigmaAPIError as e:
        if "429" in str(e):
            pytest.skip("Rate limit exceeded, waiting before retrying")
        pytest.fail(f"Figma API error: {str(e)}")
    except FigmaValidationError as e:
        pytest.fail(f"Figma validation error: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

@pytest.mark.integration
def test_figma_design_to_html(figma_to_html, figma_client):
    """Test converting the Figma design to HTML."""
    try:
        # Get the target node
        target_node = get_target_node(figma_client)
        
        print("Converting Figma design to HTML")
        html = figma_to_html.convert_to_html(TEST_FIGMA_FILE_KEY, target_node.id)
        assert html, "HTML conversion failed"
        print("Successfully generated HTML")
        
        # Basic HTML validation
        assert "<html" in html, "Missing HTML tag"
        assert "<head" in html, "Missing head tag"
        assert "<body" in html, "Missing body tag"
        
        # Check for common email-specific elements
        assert "meta" in html, "Missing meta tags"
        assert "style" in html, "Missing style tags"
        assert "table" in html, "Missing table elements"
        
        # Respect rate limits
        time.sleep(1)
        
    except FigmaConversionError as e:
        pytest.fail(f"HTML conversion error: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

@pytest.mark.integration
def test_figma_design_images(figma_client):
    """Test retrieving images from the Figma design."""
    try:
        # Get the target node
        target_node = get_target_node(figma_client)
        
        print("Retrieving Figma nodes for image testing")
        nodes = figma_client.get_file_nodes(TEST_FIGMA_FILE_KEY, [target_node.id])
        
        if not nodes or target_node.id not in nodes:
            pytest.skip(f"Node {target_node.id} not found in the file")
        
        # Find all image nodes
        image_nodes = []
        def find_image_nodes(node):
            if node.type == "IMAGE":
                image_nodes.append(node.id)
            if node.children:
                for child in node.children:
                    find_image_nodes(child)
        
        find_image_nodes(nodes[target_node.id])
        print(f"Found {len(image_nodes)} image nodes")
        
        if not image_nodes:
            pytest.skip("No image nodes found in the design")
        
        print("Testing image URL retrieval")
        image_urls = figma_client.get_image_urls(TEST_FIGMA_FILE_KEY, image_nodes)
        assert image_urls, "Failed to get image URLs"
        print(f"Retrieved {len(image_urls)} image URLs")
        
        for node_id, url in image_urls.items():
            assert url.startswith("http"), f"Invalid URL for node {node_id}: {url}"
        
        # Respect rate limits
        time.sleep(1)
        
    except FigmaAPIError as e:
        if "429" in str(e):
            pytest.skip("Rate limit exceeded, waiting before retrying")
        pytest.fail(f"Figma API error: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")

@pytest.mark.integration
def test_figma_design_validation(figma_client):
    """Test validation of the Figma design structure."""
    try:
        # Get the target node
        target_node = get_target_node(figma_client)
        
        print("Testing Figma design validation")
        nodes = figma_client.get_file_nodes(TEST_FIGMA_FILE_KEY, [target_node.id])
        
        if not nodes or target_node.id not in nodes:
            pytest.skip(f"Node {target_node.id} not found in the file")
        
        node = nodes[target_node.id]
        print(f"Validating node: {node.name} ({node.type})")
        
        # Validate node structure
        assert node.id == target_node.id, "Node ID mismatch"
        assert node.name, "Node name is empty"
        assert node.type in {"FRAME", "COMPONENT", "INSTANCE", "GROUP"}, f"Invalid node type: {node.type}"
        
        # Validate styles if present
        if node.style:
            assert isinstance(node.style, dict), "Invalid style format"
            print("Node has valid styles")
        
        # Validate bounding box if present
        if node.absoluteBoundingBox:
            assert isinstance(node.absoluteBoundingBox, dict), "Invalid bounding box format"
            assert all(key in node.absoluteBoundingBox for key in ["x", "y", "width", "height"]), "Missing bounding box properties"
            print("Node has valid bounding box")
        
        # Respect rate limits
        time.sleep(1)
        
    except FigmaValidationError as e:
        pytest.fail(f"Validation error: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}") 