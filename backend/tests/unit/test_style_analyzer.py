import pytest
from app.services.style_analyzer import StyleAnalyzer
from app.models.figma import FigmaNode
from app.core.exceptions import HTMLGenerationError

@pytest.fixture
def style_analyzer():
    return StyleAnalyzer()

@pytest.fixture
def sample_text_node():
    return FigmaNode(
        id="text-1",
        type="TEXT",
        name="Sample Text",
        backgroundColor={"r": 1, "g": 1, "b": 1},
        fills=[{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}],
        fontFamily="Arial",
        fontSize=16,
        fontWeight=400,
        lineHeight=1.5,
        padding={"top": 10, "right": 20, "bottom": 10, "left": 20},
        margin={"top": 10, "right": 0, "bottom": 10, "left": 0},
        width=200,
        height=50,
        cornerRadius=4
    )

@pytest.fixture
def sample_button_node():
    return FigmaNode(
        id="button-1",
        type="RECTANGLE",
        name="Primary Button",
        backgroundColor={"r": 0.2, "g": 0.4, "b": 0.8},
        fills=[{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
        padding=10,
        width=120,
        height=40,
        cornerRadius=8
    )

@pytest.mark.asyncio
async def test_analyze_styles_text_node(style_analyzer, sample_text_node):
    styles = await style_analyzer.analyze_styles(sample_text_node)
    
    # Check color styles
    assert styles["background-color"] == "rgb(255, 255, 255)"
    assert styles["color"] == "rgb(0, 0, 0)"
    
    # Check typography styles
    assert "Arial" in styles["font-family"]
    assert styles["font-size"] == "16px"
    assert styles["font-weight"] == "400"
    assert styles["line-height"] == "1.5"
    
    # Check spacing styles
    assert styles["padding"] == "10px 20px 10px 20px"
    assert styles["margin"] == "10px 0px 10px 0px"
    
    # Check layout styles
    assert styles["width"] == "200px"
    assert styles["height"] == "50px"
    assert styles["border-radius"] == "4px"

@pytest.mark.asyncio
async def test_analyze_styles_button_node(style_analyzer, sample_button_node):
    styles = await style_analyzer.analyze_styles(sample_button_node)
    
    # Check color styles
    assert styles["background-color"] == "rgb(51, 102, 204)"
    assert styles["color"] == "rgb(255, 255, 255)"
    
    # Check spacing styles
    assert styles["padding"] == "10px"
    
    # Check layout styles
    assert styles["width"] == "120px"
    assert styles["height"] == "40px"
    assert styles["border-radius"] == "8px"

@pytest.mark.asyncio
async def test_email_client_compatibility(style_analyzer, sample_text_node):
    styles = await style_analyzer.analyze_styles(sample_text_node)
    
    # Check Outlook-specific styles
    assert "mso-padding-top" in styles
    assert "mso-padding-bottom" in styles
    assert "mso-margin-top" in styles
    assert "mso-margin-bottom" in styles
    
    # Check border-radius handling
    assert "mso-border-radius" in styles
    assert styles["mso-border-radius"] == "0"

def test_font_stack_generation(style_analyzer):
    # Test serif font
    serif_stack = style_analyzer._get_font_stack("Georgia")
    assert "Georgia" in serif_stack
    assert "Times New Roman" in serif_stack
    assert "serif" in serif_stack
    
    # Test sans-serif font
    sans_stack = style_analyzer._get_font_stack("Helvetica")
    assert "Helvetica" in sans_stack
    assert "Arial" in sans_stack
    assert "sans-serif" in sans_stack
    
    # Test monospace font
    mono_stack = style_analyzer._get_font_stack("Courier")
    assert "Courier" in mono_stack
    assert "monospace" in mono_stack

def test_style_guide_collection(style_analyzer, sample_text_node, sample_button_node):
    # Analyze both nodes to populate style guide
    style_analyzer._extract_colors(sample_text_node)
    style_analyzer._extract_colors(sample_button_node)
    style_analyzer._extract_typography(sample_text_node)
    style_analyzer._extract_spacing(sample_text_node)
    style_analyzer._extract_layout(sample_text_node)
    
    style_guide = style_analyzer.get_style_guide()
    
    # Check color scheme
    assert len(style_guide["color_scheme"]) > 0
    assert any("rgb(255, 255, 255)" in color for color in style_guide["color_scheme"].values())
    
    # Check typography
    assert "text-md" in style_guide["typography"]
    assert style_guide["typography"]["text-md"] == "16px"
    
    # Check spacing
    assert len(style_guide["spacing"]) > 0
    assert any("10px 20px 10px 20px" in spacing for spacing in style_guide["spacing"].values())
    
    # Check layout
    assert "wide" in style_guide["layout"]
    assert style_guide["layout"]["wide"]["width"] == "200px"
    assert style_guide["layout"]["wide"]["height"] == "50px"

@pytest.mark.asyncio
async def test_error_handling(style_analyzer):
    invalid_node = FigmaNode(
        id="invalid-1",
        type="UNKNOWN",
        name="Invalid Node"
    )
    
    with pytest.raises(HTMLGenerationError) as exc_info:
        await style_analyzer.analyze_styles(invalid_node)
    assert "Failed to analyze styles" in str(exc_info.value) 