import pytest
from app.services.component_mapper import ComponentMapper
from app.models.figma import FigmaNode
from app.core.exceptions import FigmaConversionError, FigmaValidationError

@pytest.fixture
def component_mapper():
    return ComponentMapper()

@pytest.fixture
def sample_node():
    return FigmaNode(
        id="1:2",
        name="Test Node",
        type="FRAME",
        children=[],
        styles={
            "backgroundColor": {"r": 1, "g": 0, "b": 0, "a": 1},
            "width": 100,
            "height": 50,
            "cornerRadius": 5
        }
    )

@pytest.fixture
def text_node():
    return FigmaNode(
        id="1:3",
        name="Test Text",
        type="TEXT",
        children=[],
        styles={
            "color": {"r": 0, "g": 0, "b": 0, "a": 1},
            "fontSize": 16,
            "fontFamily": "Arial",
            "fontWeight": 400
        }
    )

@pytest.fixture
def button_node():
    return FigmaNode(
        id="1:4",
        name="Submit Button",
        type="FRAME",
        children=[],
        styles={
            "backgroundColor": {"r": 0, "g": 0.5, "b": 1, "a": 1},
            "padding": {"top": 10, "right": 20, "bottom": 10, "left": 20},
            "cornerRadius": 4
        }
    )

def test_map_node_to_html_basic(component_mapper, sample_node):
    """Test basic node mapping to HTML."""
    html = component_mapper.map_node_to_html(sample_node)
    assert '<table class="email-container"' in html
    assert 'cellpadding="0"' in html
    assert 'cellspacing="0"' in html
    assert 'border="0"' in html
    assert 'id="1:2"' in html
    assert 'class="test-node"' in html
    assert 'width: 100px' in html
    assert 'height: 50px' in html
    assert 'background-color: #ff0000' in html
    assert 'border-radius: 5px' in html

def test_map_node_to_html_text(component_mapper):
    """Test text node mapping to HTML."""
    text = FigmaNode(
        id="1:3",
        name="Text",
        type="TEXT",
        children=[],
        styles={"characters": "Hello World", "color": {"r": 0, "g": 0, "b": 0, "a": 1}}
    )
    html = component_mapper.map_node_to_html(text)
    assert '<p id="1:3"' in html
    assert 'class="text"' in html
    assert 'Hello World' in html

def test_map_node_to_html_button(component_mapper, button_node):
    """Test button node mapping to HTML."""
    html = component_mapper.map_node_to_html(button_node)
    assert '<table class="email-container"' in html
    assert 'id="1:4"' in html
    assert 'class="submit-button"' in html
    assert 'background-color: #007fff' in html
    assert 'border-radius: 4px' in html
    assert 'padding: 10px 20px 10px 20px' in html

def test_map_node_to_html_with_children(component_mapper):
    """Test node mapping with children."""
    parent = FigmaNode(
        id="1:1",
        name="Parent",
        type="FRAME",
        children=[
            FigmaNode(
                id="1:2",
                name="Child",
                type="TEXT",
                children=[],
                styles={"color": {"r": 0, "g": 0, "b": 0, "a": 1}}
            )
        ],
        styles={}
    )

    html = component_mapper.map_node_to_html(parent)
    assert '<table class="email-container"' in html
    assert 'id="1:1"' in html
    assert 'class="parent responsive-container"' in html
    assert '<p id="1:2"' in html
    assert 'class="child"' in html
    assert 'color: #000000' in html

def test_map_node_to_html_special_components(component_mapper):
    """Test mapping of special component types."""
    # Test header
    header = FigmaNode(
        id="1:5",
        name="Page Header",
        type="FRAME",
        children=[],
        styles={}
    )
    html = component_mapper.map_node_to_html(header)
    assert '<table class="email-container"' in html
    assert 'id="1:5"' in html
    assert 'class="page-header"' in html

def test_map_node_to_html_invalid_node(component_mapper):
    """Test handling of invalid node types."""
    invalid_node = FigmaNode(
        id="1:5",
        name="Invalid Node",
        type="INVALID_TYPE",
        children=[],
        styles={}
    )
    with pytest.raises(FigmaValidationError):
        component_mapper.map_node_to_html(invalid_node)

def test_map_node_to_html_error_handling(component_mapper):
    """Test error handling for invalid styles."""
    node = FigmaNode(
        id="1:6",
        name="Error Node",
        type="FRAME",
        children=[],
        styles={"invalid": "style"}
    )
    html = component_mapper.map_node_to_html(node)
    assert '<table class="email-container"' in html
    assert 'id="1:6"' in html
    assert 'class="error-node"' in html

def test_map_node_to_html_responsive_layout(component_mapper):
    """Test responsive layout mapping to HTML."""
    layout = FigmaNode(
        id="1:8",
        name="Responsive Layout",
        type="FRAME",
        children=[],
        styles={
            "layoutMode": "VERTICAL",
            "itemSpacing": 20,
            "paddingLeft": 10,
            "paddingRight": 10,
            "paddingTop": 10,
            "paddingBottom": 10
        }
    )

    html = component_mapper.map_node_to_html(layout)
    assert '<table class="email-container"' in html
    assert 'id="1:8"' in html
    assert 'class="responsive-layout"' in html
    assert 'width: 100%' in html
    assert 'max-width: 600px' in html
    assert 'padding: 10px' in html
    assert 'margin: 0 auto' in html

def test_map_node_to_html_responsive_image(component_mapper):
    """Test responsive image mapping to HTML."""
    image = FigmaNode(
        id="1:9",
        name="Responsive Image",
        type="RECTANGLE",
        children=[],
        styles={
            "width": 600,
            "height": 400,
            "constraints": {
                "horizontal": "SCALE",
                "vertical": "SCALE"
            }
        }
    )

    html = component_mapper.map_node_to_html(image)
    assert '<table class="email-container"' in html
    assert 'id="1:9"' in html
    assert 'class="responsive-image responsive-container"' in html
    assert 'width: 100%' in html
    assert 'max-width: 600px' in html
    assert 'height: auto' in html
    assert 'display: block' in html

def test_map_node_to_html_responsive_fonts(component_mapper):
    """Test responsive font handling."""
    text = FigmaNode(
        id="1:10",
        name="Responsive Text",
        type="TEXT",
        children=[],
        styles={
            "fontSize": 16,
            "fontFamily": "Inter",
            "characters": "Hello World"
        }
    )

    html = component_mapper.map_node_to_html(text)
    assert 'font-size: 16px' in html
    assert 'font-family: Inter, Arial, sans-serif' in html

def test_map_node_to_html_responsive_colors(component_mapper):
    """Test color handling."""
    colored = FigmaNode(
        id="1:11",
        name="Colored Node",
        type="RECTANGLE",
        children=[],
        styles={
            "backgroundColor": {"r": 1, "g": 0, "b": 0, "a": 1},
            "color": {"r": 0, "g": 0, "b": 0, "a": 1}
        }
    )

    html = component_mapper.map_node_to_html(colored)
    assert 'background-color: #ff0000' in html
    assert 'color: #000000' in html

def test_map_node_to_html_responsive_document(component_mapper):
    """Test responsive document mapping to HTML."""
    document = FigmaNode(
        id="1:10",
        name="Document",
        type="FRAME",
        children=[
            FigmaNode(
                id="1:11",
                name="Header",
                type="FRAME",
                children=[],
                styles={
                    "width": 600,
                    "height": 100,
                    "layoutMode": "VERTICAL",
                    "itemSpacing": 20,
                    "paddingLeft": 20,
                    "paddingRight": 20,
                    "paddingTop": 20,
                    "paddingBottom": 20
                }
            ),
            FigmaNode(
                id="1:12",
                name="Content",
                type="FRAME",
                children=[],
                styles={
                    "width": 600,
                    "height": 400,
                    "layoutMode": "VERTICAL",
                    "itemSpacing": 20,
                    "paddingLeft": 20,
                    "paddingRight": 20,
                    "paddingTop": 20,
                    "paddingBottom": 20
                }
            )
        ],
        styles={
            "width": 600,
            "height": 600,
            "layoutMode": "VERTICAL",
            "itemSpacing": 20,
            "paddingLeft": 20,
            "paddingRight": 20,
            "paddingTop": 20,
            "paddingBottom": 20
        }
    )

    html = component_mapper.map_node_to_html(document)
    assert '<table class="email-container"' in html
    assert 'id="1:10"' in html
    assert 'class="responsive-document responsive-container"' in html
    assert 'width: 100%' in html
    assert 'max-width: 600px' in html
    assert 'margin: 0 auto' in html
    assert 'padding: 20px' in html
    assert 'id="1:11"' in html
    assert 'id="1:12"' in html

def test_map_node_to_html_responsive_table(component_mapper):
    """Test responsive table handling."""
    # Create a table node
    table_node = FigmaNode(
        id="1:12",
        name="Table",
        type="FRAME",
        children=[
            FigmaNode(
                id="1:13",
                name="Table Cell",
                type="RECTANGLE",
                children=[],
                styles={}
            )
        ],
        styles={}
    )

    html = component_mapper.map_node_to_html(table_node)
    assert '<div id="1:12" class="table responsive-container">' in html
    assert '<td id="1:13" class="table-cell">' in html

def test_map_node_to_html_responsive_nested(component_mapper):
    """Test nested responsive containers."""
    nested = FigmaNode(
        id="1:14",
        name="Parent",
        type="FRAME",
        children=[
            FigmaNode(
                id="1:15",
                name="Child",
                type="FRAME",
                children=[],
                styles={"width": 300}
            )
        ],
        styles={"width": 600}
    )

    html = component_mapper.map_node_to_html(nested)
    assert '<table class="email-container"' in html
    assert 'width: 600px' in html
    assert 'width: 300px' in html 