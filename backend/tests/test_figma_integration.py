import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup

from app.services.figma_client import FigmaClient, FigmaFile, FigmaNode
from app.services.figma_to_html import FigmaToHTMLConverter
from app.services.email_generator import EmailGenerator
from app.core.exceptions import FigmaAPIError, FigmaValidationError, FigmaConversionError

# Test data
MOCK_FILE_KEY = "abc123"
MOCK_NODE_ID = "1:2"
MOCK_FILE_DATA = {
    "name": "Test Design",
    "lastModified": "2024-01-01T00:00:00Z",
    "version": "1",
    "thumbnailUrl": "https://example.com/thumb.png"
}
MOCK_NODE_DATA = {
    "id": MOCK_NODE_ID,
    "name": "Frame 1",
    "type": "FRAME",
    "children": [
        {
            "id": "1:3",
            "name": "Text 1",
            "type": "TEXT",
            "style": {
                "fontSize": 16,
                "fontFamily": "Arial"
            }
        }
    ]
}

@pytest.fixture
def mock_figma_client():
    """Create a mock Figma client."""
    with patch("app.services.figma_client.requests") as mock_requests:
        client = FigmaClient("mock_token")
        mock_requests.get.return_value.json.return_value = MOCK_FILE_DATA
        yield client

@pytest.fixture
def mock_converter(mock_figma_client):
    """Create a mock Figma to HTML converter."""
    return FigmaToHTMLConverter(mock_figma_client)

@pytest.fixture
def mock_email_generator(mock_figma_client):
    """Create a mock email generator."""
    return EmailGenerator()

def test_figma_file_validation():
    """Test FigmaFile validation."""
    # Valid file
    file = FigmaFile(
        key=MOCK_FILE_KEY,
        name="Test",
        last_modified="2024-01-01T00:00:00Z",
        version="1"
    )
    assert file.key == MOCK_FILE_KEY
    
    # Invalid key
    with pytest.raises(FigmaValidationError):
        FigmaFile(
            key="",  # Empty key
            name="Test",
            last_modified="2024-01-01T00:00:00Z",
            version="1"
        )

def test_figma_node_validation():
    """Test FigmaNode validation."""
    # Valid node
    node = FigmaNode(
        id=MOCK_NODE_ID,
        name="Test Node",
        type="FRAME"
    )
    assert node.type == "FRAME"
    
    # Invalid node type
    with pytest.raises(FigmaValidationError):
        FigmaNode(
            id=MOCK_NODE_ID,
            name="Test Node",
            type="INVALID_TYPE"
        )

def test_figma_client_get_file(mock_figma_client):
    """Test getting a Figma file."""
    file = mock_figma_client.get_file(MOCK_FILE_KEY)
    assert isinstance(file, FigmaFile)
    assert file.name == MOCK_FILE_DATA["name"]

def test_figma_client_error_handling(mock_figma_client):
    """Test Figma client error handling."""
    with patch("app.services.figma_client.requests") as mock_requests:
        mock_requests.get.side_effect = Exception("API Error")
        
        with pytest.raises(FigmaAPIError):
            mock_figma_client.get_file(MOCK_FILE_KEY)

def test_converter_basic_conversion(mock_converter):
    """Test basic Figma to HTML conversion."""
    with patch.object(mock_converter.figma_client, "get_file_nodes") as mock_get_nodes:
        mock_get_nodes.return_value = {MOCK_NODE_ID: FigmaNode(**MOCK_NODE_DATA)}
        
        html = mock_converter.convert_to_html(MOCK_FILE_KEY)
        soup = BeautifulSoup(html, "html.parser")
        
        # Check basic structure
        assert soup.find("html") is not None
        assert soup.find("head") is not None
        assert soup.find("body") is not None
        
        # Check responsive design
        assert soup.find("meta", attrs={"name": "viewport"}) is not None
        assert "@media" in soup.find("style").string

def test_converter_variable_replacement(mock_converter):
    """Test Figma variable replacement."""
    node_data = {
        "id": MOCK_NODE_ID,
        "name": "Hello $name",
        "type": "TEXT"
    }
    
    with patch.object(mock_converter.figma_client, "get_file_nodes") as mock_get_nodes:
        mock_get_nodes.return_value = {MOCK_NODE_ID: FigmaNode(**node_data)}
        
        mock_converter.set_variable_values({"name": "World"})
        html = mock_converter.convert_to_html(MOCK_FILE_KEY)
        
        assert "Hello World" in html

def test_email_generator_basic(mock_email_generator):
    """Test basic email generation."""
    template_data = {
        "figma_file_key": MOCK_FILE_KEY,
        "figma_node_id": MOCK_NODE_ID,
        "variables": {"name": "Test"}
    }
    
    with patch.object(mock_email_generator.converter, "convert_to_html") as mock_convert:
        mock_convert.return_value = "<html><body>Test</body></html>"
        
        html = mock_email_generator.generate_email(template_data)
        assert "Test" in html

def test_email_generator_preview(mock_email_generator):
    """Test email preview generation."""
    template_data = {
        "figma_file_key": MOCK_FILE_KEY,
        "figma_node_id": MOCK_NODE_ID
    }
    
    with patch.object(mock_email_generator.converter, "convert_to_html") as mock_convert:
        mock_convert.return_value = "<html><body>Test</body></html>"
        
        html = mock_email_generator.generate_email(template_data, preview=True)
        soup = BeautifulSoup(html, "html.parser")
        
        # Check preview modifications
        preview_header = soup.find("div", string="Email Preview")
        assert preview_header is not None
        assert "border:" in preview_header.parent["style"]

def test_email_generator_validation(mock_email_generator):
    """Test email HTML validation."""
    template_data = {
        "figma_file_key": MOCK_FILE_KEY,
        "figma_node_id": MOCK_NODE_ID
    }
    
    with patch.object(mock_email_generator.converter, "convert_to_html") as mock_convert:
        # Test with invalid HTML (missing body)
        mock_convert.return_value = "<html><div>Invalid</div></html>"
        
        with pytest.raises(FigmaConversionError) as exc:
            mock_email_generator.generate_email(template_data)
        assert "Missing <body> tag" in str(exc.value)
        
        # Test with unsupported elements
        mock_convert.return_value = "<html><body><script>alert(1)</script></body></html>"
        
        with pytest.raises(FigmaConversionError) as exc:
            mock_email_generator.generate_email(template_data)
        assert "unsupported <script> tag" in str(exc.value) 