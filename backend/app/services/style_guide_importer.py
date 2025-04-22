from typing import Dict, List, Optional, Any
from app.models.figma import FigmaNode
from app.config.brand_style_guide import BrandStyleGuide, BrandColor, BrandTypography, BrandSpacing
from app.core.exceptions import HTMLGenerationError
from app.core.config import settings

class StyleGuideImporter:
    """Imports and processes the brand style guide from Figma."""

    def __init__(self, figma_client):
        self.figma_client = figma_client
        self.style_guide_file_key = settings.FIGMA_STYLE_GUIDE_FILE_KEY
        self.style_guide_node_id = settings.FIGMA_STYLE_GUIDE_NODE_ID

    async def import_style_guide(self) -> BrandStyleGuide:
        """Import the style guide from Figma and convert it to BrandStyleGuide format."""
        try:
            # Get the style guide node from Figma
            nodes = await self.figma_client.get_file_nodes(
                self.style_guide_file_key,
                [self.style_guide_node_id]
            )
            
            if not nodes or self.style_guide_node_id not in nodes:
                raise HTMLGenerationError("Style guide node not found in Figma file")
            
            style_guide_node = nodes[self.style_guide_node_id]
            
            # Extract colors
            colors = await self._extract_colors(style_guide_node)
            
            # Extract typography
            typography = await self._extract_typography(style_guide_node)
            
            # Extract spacing
            spacing = await self._extract_spacing(style_guide_node)
            
            # Extract layout constraints
            max_width = await self._extract_max_width(style_guide_node)
            border_radius = await self._extract_border_radius(style_guide_node)
            shadows = await self._extract_shadows(style_guide_node)
            
            return BrandStyleGuide(
                colors=colors,
                typography=typography,
                spacing=spacing,
                max_width=max_width,
                border_radius=border_radius,
                shadows=shadows
            )
            
        except Exception as e:
            raise HTMLGenerationError(f"Failed to import style guide: {str(e)}")

    async def _extract_colors(self, node: FigmaNode) -> Dict[str, BrandColor]:
        """Extract color styles from the style guide node."""
        colors = {}
        
        def process_color_node(color_node: FigmaNode):
            if not color_node.styles:
                return
                
            # Extract color properties
            name = color_node.name
            if "backgroundColor" in color_node.styles:
                color = color_node.styles["backgroundColor"]
                r, g, b = int(color["r"] * 255), int(color["g"] * 255), int(color["b"] * 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Map the color names to our brand color names
                color_mapping = {
                    "Primary/Green40 - Evergreen": "primary",
                    "Primary/Green20 - Forest": "forest",
                    "Primary/Green90 - Lime 30%": "lime",
                    "Neutral/Neutral 0 - Black": "black",
                    "Neutral/Neutral 100 - White": "white",
                    "Neutral/Neutral 700": "neutral-700",
                    "Neutral/Neutral 900": "neutral-900"
                }
                
                brand_name = color_mapping.get(name, name.lower())
                colors[brand_name] = BrandColor(
                    name=name,
                    hex=hex_color,
                    rgb={"r": r, "g": g, "b": b},
                    usage=self._infer_color_usage(name)
                )
        
        # Process color nodes
        if node.children:
            for child in node.children:
                if child.name.lower().startswith(("color", "primary", "neutral")):
                    process_color_node(child)
        
        return colors

    async def _extract_typography(self, node: FigmaNode) -> BrandTypography:
        """Extract typography styles from the style guide node."""
        font_family = "Arial, sans-serif"  # Default email-safe font
        weights = [400, 700]  # Default email-safe weights
        sizes = {}
        line_heights = {}
        
        def process_text_node(text_node: FigmaNode):
            if not text_node.styles:
                return
                
            name = text_node.name.lower()
            
            # Extract font size
            if "fontSize" in text_node.styles:
                size = text_node.styles["fontSize"]
                if "headline" in name:
                    sizes["h1"] = size
                elif "subtitle" in name:
                    sizes["h2"] = size
                elif "body" in name:
                    sizes["body"] = size
                elif "caption" in name:
                    sizes["small"] = size
                    
            # Extract line height
            if "lineHeight" in text_node.styles:
                line_height = text_node.styles["lineHeight"]
                if "headline" in name:
                    line_heights["h1"] = line_height
                elif "subtitle" in name:
                    line_heights["h2"] = line_height
                elif "body" in name:
                    line_heights["body"] = line_height
                elif "caption" in name:
                    line_heights["small"] = line_height
        
        # Process text nodes
        if node.children:
            for child in node.children:
                if child.type == "TEXT":
                    process_text_node(child)
        
        return BrandTypography(
            font_family=font_family,
            weights=weights,
            sizes=sizes,
            line_heights=line_heights
        )

    async def _extract_spacing(self, node: FigmaNode) -> BrandSpacing:
        """Extract spacing scale from the style guide node."""
        scale = {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32
        }
        
        def process_spacing_node(spacing_node: FigmaNode):
            if not spacing_node.styles:
                return
                
            name = spacing_node.name.lower()
            if "width" in spacing_node.styles:
                size = spacing_node.styles["width"]
                if "xs" in name:
                    scale["xs"] = size
                elif "sm" in name:
                    scale["sm"] = size
                elif "md" in name:
                    scale["md"] = size
                elif "lg" in name:
                    scale["lg"] = size
                elif "xl" in name:
                    scale["xl"] = size
        
        # Process spacing nodes
        if node.children:
            for child in node.children:
                if child.name.lower().startswith("spacing"):
                    process_spacing_node(child)
        
        return BrandSpacing(scale=scale)

    async def _extract_max_width(self, node: FigmaNode) -> int:
        """Extract maximum width constraint from the style guide node."""
        default_max_width = 600
        
        if node.children:
            for child in node.children:
                if child.name.lower() == "max width":
                    return int(child.styles.get("width", default_max_width))
        
        return default_max_width

    async def _extract_border_radius(self, node: FigmaNode) -> Dict[str, int]:
        """Extract border radius options from the style guide node."""
        border_radius = {
            "sm": 4,
            "md": 8,
            "lg": 12
        }
        
        def process_border_node(border_node: FigmaNode):
            if not border_node.styles:
                return
                
            name = border_node.name.lower()
            if "cornerRadius" in border_node.styles:
                radius = border_node.styles["cornerRadius"]
                if "sm" in name:
                    border_radius["sm"] = radius
                elif "md" in name:
                    border_radius["md"] = radius
                elif "lg" in name:
                    border_radius["lg"] = radius
        
        # Process border radius nodes
        if node.children:
            for child in node.children:
                if child.name.lower().startswith("border"):
                    process_border_node(child)
        
        return border_radius

    async def _extract_shadows(self, node: FigmaNode) -> Dict[str, str]:
        """Extract shadow styles from the style guide node."""
        shadows = {
            "sm": "0 2px 4px rgba(0, 0, 0, 0.1)",
            "md": "0 4px 8px rgba(0, 0, 0, 0.15)",
            "lg": "0 8px 16px rgba(0, 0, 0, 0.2)"
        }
        
        def process_shadow_node(shadow_node: FigmaNode):
            if not shadow_node.styles:
                return
                
            name = shadow_node.name.lower()
            if "effects" in shadow_node.styles:
                effects = shadow_node.styles["effects"]
                for effect in effects:
                    if effect["type"] == "DROP_SHADOW":
                        offset = effect["offset"]
                        color = effect["color"]
                        shadow = f"{offset['x']} {offset['y']}px {effect['radius']}px rgba(0, 0, 0, {color['a']})"
                        
                        if "small" in name:
                            shadows["sm"] = shadow
                        elif "medium" in name:
                            shadows["md"] = shadow
                        elif "large" in name:
                            shadows["lg"] = shadow
        
        # Process shadow nodes
        if node.children:
            for child in node.children:
                if child.name.lower().startswith("shadow"):
                    process_shadow_node(child)
        
        return shadows

    def _infer_color_usage(self, color_name: str) -> List[str]:
        """Infer the usage of a color based on its name."""
        name = color_name.lower()
        usage = []
        
        if "primary" in name:
            usage.extend(["primary", "buttons", "links"])
        elif "secondary" in name:
            usage.extend(["accent", "success"])
        elif "background" in name:
            usage.extend(["background", "cards"])
        elif "text" in name:
            usage.extend(["text", "headings"])
        elif "error" in name:
            usage.extend(["error", "danger"])
        elif "warning" in name:
            usage.extend(["warning", "alert"])
        elif "success" in name:
            usage.extend(["success", "positive"])
        elif "info" in name:
            usage.extend(["info", "neutral"])
        
        return usage 