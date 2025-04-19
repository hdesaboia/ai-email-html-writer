import pytest
from app.services.figma_client import FigmaClient
from app.services.figma_to_html import FigmaToHTMLConverter
from app.core.config import settings


@pytest.fixture
def figma_client():
    return FigmaClient(access_token=settings.FIGMA_ACCESS_TOKEN)


@pytest.fixture
def figma_to_html(figma_client):
    return FigmaToHTMLConverter(figma_client=figma_client)


@pytest.mark.integration
def test_figma_client_integration(figma_client):
    """Test the Figma client with real API calls."""
    # Test file access
    file = figma_client.get_file("test_file_key")  # Replace with a real test file key
    assert file is not None
    assert file.name
    assert file.version
    
    # Test node retrieval
    nodes = figma_client.get_file_nodes("test_file_key")
    assert nodes
    assert len(nodes) > 0
    
    # Test image URL retrieval
    node_ids = list(nodes.keys())[:2]  # Get first two nodes
    image_urls = figma_client.get_image_urls("test_file_key", node_ids)
    assert image_urls
    assert all(url.startswith("http") for url in image_urls.values())


@pytest.mark.integration
def test_figma_to_html_integration(figma_to_html):
    """Test the Figma to HTML conversion with real API calls."""
    # Convert a Figma file to HTML
    html = figma_to_html.convert_to_html("test_file_key")  # Replace with a real test file key
    
    # Basic HTML validation
    assert "<html" in html
    assert "<head" in html
    assert "<body" in html
    assert "<style" in html
    
    # Check for email-specific elements
    assert "viewport" in html
    assert "email-specific styles" in html
    
    # Check for converted Figma elements
    assert "figma-frame" in html
    assert "figma-text" in html


@pytest.mark.integration
def test_figma_component_sets(figma_client):
    """Test component set retrieval with real API calls."""
    component_sets = figma_client.get_component_sets("test_file_key")  # Replace with a real test file key
    assert isinstance(component_sets, dict)
    
    # If the file has component sets, verify their structure
    if component_sets:
        for component_id, component in component_sets.items():
            assert component.type == "COMPONENT_SET"
            assert component.id == component_id
            assert component.name


@pytest.mark.integration
def test_figma_style_conversion(figma_to_html):
    """Test style conversion with real Figma data."""
    # Get nodes from a real file
    nodes = figma_to_html.figma_client.get_file_nodes("test_file_key")  # Replace with a real test file key
    
    # Find a node with styles
    styled_node = None
    for node in nodes.values():
        if node.style:
            styled_node = node
            break
    
    if styled_node:
        # Test style conversion
        css = figma_to_html._convert_styles_to_css(styled_node.style)
        assert css
        assert ";" in css  # Should have multiple properties
        
        # Check for common style properties
        if "color" in styled_node.style:
            assert "background-color" in css
        if "fontSize" in styled_node.style:
            assert "font-size" in css
        if "fontFamily" in styled_node.style:
            assert "font-family" in css 