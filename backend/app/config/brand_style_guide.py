from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class BrandColor(BaseModel):
    name: str
    hex: str
    rgb: Dict[str, int]
    usage: List[str]  # e.g., ["primary", "accent", "background"]

class BrandTypography(BaseModel):
    font_family: str
    weights: List[int]
    sizes: Dict[str, int]  # e.g., {"h1": 32, "h2": 24, "body": 16}
    line_heights: Dict[str, float]

class BrandSpacing(BaseModel):
    desktop: Dict[str, Dict[str, Any]]
    mobile: Dict[str, Dict[str, Any]]
    usage_guidelines: Dict[str, Any]

class BrandLayout(BaseModel):
    desktop: Dict[str, Any]
    mobile: Dict[str, Any]

class BrandImageGuidelines(BaseModel):
    static_images: Dict[str, Any]
    animated_gifs: Dict[str, Any]

class BrandStyleGuide(BaseModel):
    colors: Dict[str, BrandColor]
    typography: BrandTypography
    spacing: BrandSpacing
    layout: BrandLayout
    max_width: int
    border_radius: Dict[str, int]
    shadows: Optional[Dict[str, str]] = None
    image_guidelines: BrandImageGuidelines

# Example brand style guide configuration
BRAND_STYLE_GUIDE = BrandStyleGuide(
    colors={
        "background-white": BrandColor(
            name="White",
            hex="#FFFFFF",
            rgb={"r": 255, "g": 255, "b": 255},
            usage=["email-logo-header", "background-1", "social-icons"]
        ),
        "background-evergreen": BrandColor(
            name="Evergreen",
            hex="#007B34",
            rgb={"r": 0, "g": 123, "b": 52},
            usage=["buttons", "icons", "social-icons"]
        ),
        "background-oat": BrandColor(
            name="Oat",
            hex="#FFFBED",
            rgb={"r": 255, "g": 251, "b": 237},
            usage=["background-2"]
        ),
        "background-light-grey": BrandColor(
            name="Light grey",
            hex="#EDEDED",
            rgb={"r": 237, "g": 237, "b": 237},
            usage=["background-3"]
        ),
        "background-lime-30": BrandColor(
            name="Lime 30%",
            hex="#EDEDED",
            rgb={"r": 237, "g": 237, "b": 237},
            usage=["background-4", "bullets"]
        ),
        "text-dark-grey": BrandColor(
            name="Dark grey",
            hex="#373938",
            rgb={"r": 55, "g": 57, "b": 56},
            usage=["headlines", "subheads", "small-numbers"]
        ),
        "text-mid-grey": BrandColor(
            name="Mid grey",
            hex="#848484",
            rgb={"r": 132, "g": 132, "b": 132},
            usage=["legal-copy"]
        ),
        "text-white": BrandColor(
            name="White",
            hex="#FFFFFF",
            rgb={"r": 255, "g": 255, "b": 255},
            usage=["cta-copy"]
        ),
        "text-evergreen": BrandColor(
            name="Evergreen",
            hex="#007B34",
            rgb={"r": 0, "g": 123, "b": 52},
            usage=["headlines", "subheads", "cta-copy", "hyperlink"]
        )
    },
    typography=BrandTypography(
        font_family="Roboto",
        weights=[300, 400, 500, 700],
        sizes={
            "h1": 32,
            "h2": 24,
            "h3": 20,
            "body": 16,
            "small": 14
        },
        line_heights={
            "h1": 1.2,
            "h2": 1.3,
            "h3": 1.3,
            "body": 1.5,
            "small": 1.4
        }
    ),
    spacing=BrandSpacing(
        desktop={
            "padding_components": {
                "padding_1": {"value": 8, "unit": "px"},
                "padding_2": {"value": 16, "unit": "px"},
                "padding_3": {"value": 24, "unit": "px"},
                "padding_4": {"value": 32, "unit": "px"},
                "padding_5": {"value": 40, "unit": "px"}
            }
        },
        mobile={
            "padding_components": {
                "padding_1": {"value": 8, "unit": "px"},
                "padding_2": {"value": 16, "unit": "px"},
                "padding_3": {"value": 24, "unit": "px"},
                "padding_4": {"value": 32, "unit": "px"},
                "padding_5": {"value": 40, "unit": "px"}
            }
        },
        usage_guidelines={
            "section_separation": {
                "description": "Between sections with background color changes",
                "padding": "padding_6",
                "value": 40,
                "unit": "px"
            },
            "component_spacing": {
                "headline_to_body": {
                    "description": "Between headline and body copy",
                    "padding": "padding_3",
                    "value": 16,
                    "unit": "px"
                },
                "headline_to_image": {
                    "description": "Between headline and image",
                    "padding": "padding_4",
                    "value": 24,
                    "unit": "px"
                },
                "body_to_cta": {
                    "description": "Between body copy and CTA",
                    "padding": "padding_4",
                    "value": 24,
                    "unit": "px"
                },
                "image_to_body": {
                    "description": "Between image and body copy",
                    "padding": "padding_3",
                    "value": 16,
                    "unit": "px"
                }
            },
            "components_with_built_in_padding": [
                "incentives",
                "spanish_header_footer",
                "questions"
            ]
        }
    ),
    layout=BrandLayout(
        desktop={
            "width": 600,
            "unit": "px",
            "layout_options": {
                "preferred": "single_column",
                "supported": ["single_column", "two_column"]
            },
            "guidelines": [
                "Single-column layout is preferred",
                "Two-column layout is supported when necessary"
            ]
        },
        mobile={
            "width": {
                "minimum": 320,
                "standard": 420,
                "unit": "px"
            },
            "layout_requirements": {
                "must_use_single_column": True,
                "reasons": [
                    "Ensures seamless content adjustment between different sizes",
                    "Maintains design quality",
                    "Prevents layout issues"
                ]
            },
            "guidelines": [
                "All components must use single-column layout",
                "Design quality diminishes if single-column is not used",
                "Content should adjust seamlessly between different mobile sizes"
            ]
        }
    ),
    max_width=600,
    border_radius={
        "sm": 4,
        "md": 8,
        "lg": 12
    },
    shadows={
        "sm": "0 1px 2px rgba(0,0,0,0.1)",
        "md": "0 2px 4px rgba(0,0,0,0.1)",
        "lg": "0 4px 8px rgba(0,0,0,0.1)"
    },
    image_guidelines=BrandImageGuidelines(
        static_images={
            "approach": "single_image",
            "quality_guidelines": {
                "use_larger_size": True,
                "responsive_handling": True
            },
            "accessibility": {
                "alt_text_required": True,
                "alt_text_source": "creative_team",
                "alt_text_guidelines": [
                    "Must be provided with final deliverables",
                    "Should be descriptive and meaningful",
                    "Should accurately represent image content"
                ]
            },
            "implementation": {
                "html_template": "<img src='{{image_url}}' alt='{{alt_text}}' class='responsive-image' style='max-width: 100%; height: auto;' />",
                "css_properties": {
                    "max-width": "100%",
                    "height": "auto",
                    "display": "block"
                }
            }
        },
        animated_gifs={
            "file_size": {
                "ideal": 250000,
                "maximum": 1000000
            },
            "requirements": {
                "static_fallback": True,
                "fallback_guidelines": {
                    "match_dimensions": True,
                    "represent_key_frame": True
                }
            },
            "accessibility": {
                "alt_text_required": True,
                "alt_text_source": "creative_team",
                "alt_text_guidelines": [
                    "Must be provided with final deliverables",
                    "Should describe the animation content",
                    "Should include key elements of the animation"
                ]
            },
            "implementation": {
                "html_template": "<img src='{{gif_url}}' alt='{{alt_text}}' class='animated-gif' style='max-width: 100%; height: auto;' onerror='this.src=\"{{fallback_url}}\"' />",
                "css_properties": {
                    "max-width": "100%",
                    "height": "auto",
                    "display": "block"
                }
            }
        }
    )
) 