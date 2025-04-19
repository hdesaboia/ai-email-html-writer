import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from app.services.figma_to_html import FigmaToHTMLConverter
from app.services.figma_client import FigmaNode


@pytest.fixture
def figma_to_html():
    return FigmaToHTMLConverter()


@pytest.fixture
def mock_figma_node():
    return FigmaNode(
        id="1:1",
        name="Test Frame",
        type="FRAME",
        children=[
            FigmaNode(
                id="1:2",
                name="Test Text",
                type="TEXT",
                style={
                    "color": {"r": 0, "g": 0, "b": 0, "a": 1},
                    "fontSize": 16,
                    "fontFamily": "Arial",
                    "textAlign": "left"
                }
            ),
            FigmaNode(
                id="1:3",
                name="Test Image",
                type="IMAGE",
                absoluteBoundingBox={"x": 0, "y": 0, "width": 100, "height": 100}
            )
        ]
    )


@pytest.fixture
def mock_image_urls():
    return {"1:3": "https://example.com/image.png"}


def test_convert_to_html(figma_to_html, mock_figma_node, mock_image_urls):
    with patch.object(figma_to_html.figma_client, 'get_file_nodes') as mock_get_nodes, \
         patch.object(figma_to_html.figma_client, 'get_image_urls') as mock_get_images:
        
        mock_get_nodes.return_value = {"1:1": mock_figma_node}
        mock_get_images.return_value = mock_image_urls
        
        html = figma_to_html.convert_to_html("test_key")
        
        # Parse the HTML to verify its structure
        soup = BeautifulSoup(html, "html.parser")
        
        # Check basic structure
        assert soup.html is not None
        assert soup.head is not None
        assert soup.body is not None
        
        # Check viewport meta tag
        viewport = soup.find("meta", attrs={"name": "viewport"})
        assert viewport is not None
        assert viewport["content"] == "width=device-width, initial-scale=1.0"
        
        # Check email-specific styles
        style = soup.find("style")
        assert style is not None
        assert "email-specific styles" in style.string
        
        # Check converted nodes
        frame = soup.find("div", class_="figma-frame")
        assert frame is not None
        assert frame["id"] == "1:1"
        
        text = soup.find("p", class_="figma-text")
        assert text is not None
        assert text["id"] == "1:2"
        assert "font-size: 16px" in text["style"]
        assert "font-family: Arial" in text["style"]
        
        image = soup.find("img", class_="figma-image")
        assert image is not None
        assert image["id"] == "1:3"
        assert image["src"] == "https://example.com/image.png"
        assert "width: 100px" in image["style"]
        assert "height: 100px" in image["style"]


def test_convert_node_to_html(figma_to_html, mock_figma_node, mock_image_urls):
    with patch.object(figma_to_html.figma_client, 'get_image_urls') as mock_get_images:
        mock_get_images.return_value = mock_image_urls
        
        soup = BeautifulSoup("", "html.parser")
        body = soup.new_tag("body")
        
        figma_to_html._convert_node_to_html(mock_figma_node, body, "test_key")
        
        # Check the converted node
        frame = body.find("div", class_="figma-frame")
        assert frame is not None
        assert frame["id"] == "1:1"
        
        # Check children
        text = frame.find("p", class_="figma-text")
        assert text is not None
        assert text["id"] == "1:2"
        
        image = frame.find("img", class_="figma-image")
        assert image is not None
        assert image["id"] == "1:3"


def test_convert_styles_to_css(figma_to_html):
    styles = {
        "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 0.5},
        "fontSize": 16,
        "fontFamily": "Arial",
        "textAlign": "center"
    }
    
    css = figma_to_html._convert_styles_to_css(styles)
    
    assert "background-color: rgba(128, 128, 128, 0.5)" in css
    assert "font-size: 16px" in css
    assert "font-family: Arial" in css
    assert "text-align: center" in css


def test_convert_to_html_with_specific_node(figma_to_html, mock_figma_node):
    with patch.object(figma_to_html.figma_client, 'get_file_nodes') as mock_get_nodes:
        mock_get_nodes.return_value = {"1:1": mock_figma_node}
        
        html = figma_to_html.convert_to_html("test_key", "1:1")
        
        soup = BeautifulSoup(html, "html.parser")
        frame = soup.find("div", class_="figma-frame")
        assert frame is not None
        assert frame["id"] == "1:1"


def test_convert_to_html_node_not_found(figma_to_html):
    with patch.object(figma_to_html.figma_client, 'get_file_nodes') as mock_get_nodes:
        mock_get_nodes.return_value = {}
        
        with pytest.raises(ValueError):
            figma_to_html.convert_to_html("test_key", "nonexistent") 