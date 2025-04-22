import os
import pytest
from app.services.style_guide_importer import StyleGuideImporter
from app.services.figma_client import FigmaClient
from app.models.figma import FigmaNode

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["FIGMA_ACCESS_TOKEN"] = "test_token"
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("FIGMA_ACCESS_TOKEN", None)

@pytest.fixture
def mock_figma_client():
    """Create a mock Figma client."""
    return FigmaClient()

@pytest.fixture
def style_guide_importer(mock_figma_client):
    """Create a StyleGuideImporter instance with mocked client."""
    return StyleGuideImporter(mock_figma_client)

@pytest.mark.asyncio
async def test_extract_colors(style_guide_importer):
    """Test color extraction from style guide."""
    # Create a mock node with color styles
    node = FigmaNode(
        id="1",
        name="Colors",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Primary/Green40 - Evergreen",
                type="RECTANGLE",
                styles={
                    "backgroundColor": {"r": 0, "g": 0.48, "b": 0.2, "a": 1}
                }
            ),
            FigmaNode(
                id="3",
                name="Neutral/Neutral 900",
                type="RECTANGLE",
                styles={
                    "backgroundColor": {"r": 0.15, "g": 0.2, "b": 0.22, "a": 1}
                }
            )
        ]
    )
    
    colors = await style_guide_importer._extract_colors(node)
    
    assert "primary" in colors
    assert colors["primary"].hex == "#007a33"
    assert colors["primary"].rgb == {"r": 0, "g": 122, "b": 51}
    
    assert "neutral-900" in colors
    assert colors["neutral-900"].hex == "#263338"
    assert colors["neutral-900"].rgb == {"r": 38, "g": 51, "b": 56}

@pytest.mark.asyncio
async def test_extract_typography(style_guide_importer):
    """Test typography extraction from style guide."""
    # Create a mock node with typography styles
    node = FigmaNode(
        id="1",
        name="Typography",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Mobile/Headline Small",
                type="TEXT",
                styles={
                    "fontSize": 24,
                    "lineHeight": 32
                }
            ),
            FigmaNode(
                id="3",
                name="Mobile/Body",
                type="TEXT",
                styles={
                    "fontSize": 16,
                    "lineHeight": 24
                }
            )
        ]
    )
    
    typography = await style_guide_importer._extract_typography(node)
    
    assert typography.font_family == "Arial, sans-serif"
    assert typography.weights == [400, 700]
    assert typography.sizes["h1"] == 24
    assert typography.sizes["body"] == 16
    assert typography.line_heights["h1"] == 32
    assert typography.line_heights["body"] == 24

@pytest.mark.asyncio
async def test_extract_spacing(style_guide_importer):
    """Test spacing extraction from style guide."""
    node = FigmaNode(
        id="1",
        name="Spacing",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Spacing/XS",
                type="RECTANGLE",
                styles={
                    "width": 4
                }
            ),
            FigmaNode(
                id="3",
                name="Spacing/SM",
                type="RECTANGLE",
                styles={
                    "width": 8
                }
            ),
            FigmaNode(
                id="4",
                name="Spacing/MD",
                type="RECTANGLE",
                styles={
                    "width": 16
                }
            )
        ]
    )
    
    spacing = await style_guide_importer._extract_spacing(node)
    
    assert spacing.scale["xs"] == 4
    assert spacing.scale["sm"] == 8
    assert spacing.scale["md"] == 16
    assert spacing.scale["lg"] == 24  # Default value
    assert spacing.scale["xl"] == 32  # Default value

@pytest.mark.asyncio
async def test_extract_max_width(style_guide_importer):
    """Test max width extraction from style guide."""
    node = FigmaNode(
        id="1",
        name="Layout",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Max Width",
                type="RECTANGLE",
                styles={
                    "width": 800
                }
            )
        ]
    )
    
    max_width = await style_guide_importer._extract_max_width(node)
    assert max_width == 800

@pytest.mark.asyncio
async def test_extract_border_radius(style_guide_importer):
    """Test border radius extraction from style guide."""
    node = FigmaNode(
        id="1",
        name="Border Radius",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Border Radius/Small",
                type="RECTANGLE",
                styles={
                    "cornerRadius": 4
                }
            ),
            FigmaNode(
                id="3",
                name="Border Radius/Medium",
                type="RECTANGLE",
                styles={
                    "cornerRadius": 8
                }
            ),
            FigmaNode(
                id="4",
                name="Border Radius/Large",
                type="RECTANGLE",
                styles={
                    "cornerRadius": 12
                }
            )
        ]
    )
    
    border_radius = await style_guide_importer._extract_border_radius(node)
    
    assert border_radius["sm"] == 4
    assert border_radius["md"] == 8
    assert border_radius["lg"] == 12

@pytest.mark.asyncio
async def test_extract_shadows(style_guide_importer):
    """Test shadow extraction from style guide."""
    node = FigmaNode(
        id="1",
        name="Shadows",
        type="FRAME",
        children=[
            FigmaNode(
                id="2",
                name="Shadow/Small",
                type="RECTANGLE",
                styles={
                    "effects": [
                        {
                            "type": "DROP_SHADOW",
                            "color": {"r": 0, "g": 0, "b": 0, "a": 0.1},
                            "offset": {"x": 0, "y": 2},
                            "radius": 4,
                            "spread": 0
                        }
                    ]
                }
            ),
            FigmaNode(
                id="3",
                name="Shadow/Medium",
                type="RECTANGLE",
                styles={
                    "effects": [
                        {
                            "type": "DROP_SHADOW",
                            "color": {"r": 0, "g": 0, "b": 0, "a": 0.15},
                            "offset": {"x": 0, "y": 4},
                            "radius": 8,
                            "spread": 0
                        }
                    ]
                }
            )
        ]
    )
    
    shadows = await style_guide_importer._extract_shadows(node)
    
    assert shadows["sm"] == "0 2px 4px rgba(0, 0, 0, 0.1)"
    assert shadows["md"] == "0 4px 8px rgba(0, 0, 0, 0.15)" 