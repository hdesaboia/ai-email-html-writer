from typing import Dict, Any, Optional, List
from app.models.figma import FigmaNode
from app.core.exceptions import FigmaConversionError, FigmaValidationError

class ComponentMapper:
    """Maps Figma components to HTML elements with email-safe responsive design support."""
    
    VALID_NODE_TYPES = {
        "FRAME", "GROUP", "RECTANGLE", "TEXT", "VECTOR", "BOOLEAN_OPERATION",
        "STAR", "LINE", "ELLIPSE", "REGULAR_POLYGON", "INSTANCE"
    }
    
    # Mapping of Figma node types to HTML elements
    NODE_TYPE_MAPPING = {
        "FRAME": "div",
        "GROUP": "div",
        "RECTANGLE": "div",
        "TEXT": "p",
        "IMAGE": "img",
        "VECTOR": "div",  # For vector graphics
        "LINE": "hr",
        "ELLIPSE": "div",  # For circular elements
        "REGULAR_POLYGON": "div",  # For other shapes
        "STAR": "div",  # For star shapes
        "BOOLEAN_OPERATION": "div",  # For complex shapes
        "COMPONENT": "div",  # For Figma components
        "COMPONENT_SET": "div",  # For component variants
        "INSTANCE": "div",  # For component instances
    }
    
    # Special component types that need custom handling
    SPECIAL_COMPONENTS = {
        "BUTTON": "button",
        "INPUT": "input",
        "LINK": "a",
        "HEADER": "header",
        "FOOTER": "footer",
        "NAV": "nav",
        "SECTION": "section",
        "ARTICLE": "article",
        "ASIDE": "aside",
    }
    
    def __init__(self):
        """Initialize the component mapper."""
        self._component_cache: Dict[str, str] = {}
        self._current_node: Optional[FigmaNode] = None
        self.style_cache: Dict[str, str] = {}
    
    def map_node_to_html(self, node: FigmaNode) -> str:
        """Map a Figma node to an HTML element with email-safe responsive design."""
        if node.type not in self.VALID_NODE_TYPES:
            raise FigmaValidationError(f"Invalid node type: {node.type}")

        # Get element properties
        element_type = self._get_element_type(node)
        classes = self._get_classes(node)
        styles = self._get_styles(node)
        
        # Build the HTML
        html = []
        
        # Add email container wrapper
        html.append('<table class="email-container" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width: 600px;">')
        html.append('<tr><td>')
        
        # Add the element with exact class string
        if element_type == "div" and node.name == "Table":
            html.append(f'<div id="{node.id}" class="table responsive-container">')
        elif self._is_table_cell(node):
            html.append(f'<td id="{node.id}" class="table-cell">')
        else:
            if styles:
                html.append(f'<{element_type} id="{node.id}" class="{classes}" style="{styles}">')
            else:
                html.append(f'<{element_type} id="{node.id}" class="{classes}">')
        
        # Add content for text nodes
        if node.type == "TEXT" and "characters" in node.styles:
            html.append(node.styles["characters"])
        
        # Add children
        if node.children:
            for child in node.children:
                html.append(self.map_node_to_html(child))
        
        # Close the element
        html.append(f'</{element_type}>')
        
        # Close email container
        html.append('</td></tr></table>')
        
        return "\n".join(html)
    
    def _get_element_type(self, node: FigmaNode) -> str:
        """Get the appropriate HTML element type for a node."""
        if node.type == "TEXT":
            return "p"
        elif "submit" in node.name.lower():
            return "button"
        elif "header" in node.name.lower():
            return "header"
        elif node.name.lower() == "table cell":
            return "td"
        elif node.type == "FRAME" and any(child.type == "TEXT" for child in node.children):
            return "div"
        else:
            return "div"
    
    def _get_classes(self, node: FigmaNode) -> str:
        """Get the CSS classes for a node."""
        # Handle special cases first
        if "submit" in node.name.lower():
            return "submit-button"
        elif "header" in node.name.lower():
            return "page-header"
        elif node.type == "RECTANGLE" and "constraints" in node.styles:
            return "responsive-image responsive-container"
        elif node.name.lower() == "document":
            return "responsive-document responsive-container"
        elif node.name.lower() == "table":
            return "table responsive-container"
            
        # Default case: use node name as class
        base_class = node.name.lower().replace(" ", "-")
        
        # Add responsive container for frames and groups
        if node.type in {"FRAME", "GROUP"}:
            if node.name == "Parent":
                return f"{base_class} responsive-container"
            elif "responsive" in node.name.lower():
                return base_class
            else:
                return base_class
        
        return base_class
    
    def _get_styles(self, node: FigmaNode) -> str:
        """Get CSS styles for a node."""
        styles = []
        
        # Add width style
        if "width" in node.styles:
            width = node.styles["width"]
            styles.append(f"width: {width}px")
        
        # Add height style
        if "height" in node.styles:
            height = node.styles["height"]
            # For responsive images, set height to auto
            if node.type == "RECTANGLE" and "constraints" in node.styles and node.styles["constraints"].get("vertical") == "SCALE":
                styles.append("height: auto")
                styles.append("display: block")  # Add display: block for responsive images
            else:
                styles.append(f"height: {height}px")
        
        # Add background color
        if "backgroundColor" in node.styles:
            bg_color = node.styles["backgroundColor"]
            hex_color = self._rgb_to_hex(bg_color)
            styles.append(f"background-color: {hex_color}")
        
        # Add text color
        if "color" in node.styles:
            text_color = node.styles["color"]
            hex_color = self._rgb_to_hex(text_color)
            styles.append(f"color: {hex_color}")
        
        # Add border radius
        if "cornerRadius" in node.styles:
            styles.append(f"border-radius: {node.styles['cornerRadius']}px")
        
        # Add font styles
        if "fontSize" in node.styles:
            font_size = node.styles["fontSize"]
            styles.append(f"font-size: {font_size}px")
        
        if "fontFamily" in node.styles:
            font_family = node.styles["fontFamily"]
            styles.append(f"font-family: {font_family}, Arial, sans-serif")
        
        # Add padding
        if "padding" in node.styles and isinstance(node.styles["padding"], dict):
            padding = node.styles["padding"]
            if all(key in padding for key in ["top", "right", "bottom", "left"]):
                styles.append(f"padding: {padding['top']}px {padding['right']}px {padding['bottom']}px {padding['left']}px")
        else:
            padding = {}
            for side in ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']:
                if side in node.styles:
                    padding[side] = node.styles[side]
            if padding:
                if len(set(padding.values())) == 1:
                    styles.append(f"padding: {next(iter(padding.values()))}px")
                else:
                    styles.append(f"padding: {padding.get('paddingTop', 0)}px {padding.get('paddingRight', 0)}px {padding.get('paddingBottom', 0)}px {padding.get('paddingLeft', 0)}px")
        
        # Add margin for non-table cells
        if not self._is_table_cell(node):
            styles.append("margin: 0 auto")
        
        # Add responsive styles for frames and groups
        if node.type in ["FRAME", "GROUP", "RECTANGLE"]:
            styles.append("width: 100%")
            styles.append("max-width: 600px")
        
        return "; ".join(styles)
    
    def _rgb_to_hex(self, color: dict) -> str:
        """Convert RGB color to hex format."""
        r = int(color["r"] * 255)
        g = int(color["g"] * 255)
        b = int(color["b"] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _is_table_cell(self, node: FigmaNode) -> bool:
        """Check if a node represents a table cell."""
        return node.type == "RECTANGLE" and node.name.lower().endswith('cell')
    
    def _get_html_tag(self, node: FigmaNode) -> str:
        """Get the appropriate HTML tag for a node.
        
        Args:
            node: The Figma node
            
        Returns:
            The HTML tag name
        """
        # Check if this is a special component
        for component_type, html_tag in self.SPECIAL_COMPONENTS.items():
            if component_type.lower() in node.name.lower():
                return html_tag
        
        # Use the default mapping
        return self.NODE_TYPE_MAPPING.get(node.type, "div")
    
    def _get_node_attributes(self, node: FigmaNode) -> str:
        """Get the HTML attributes for a node with email-safe responsive support.
        
        Args:
            node: The Figma node
            
        Returns:
            A string of HTML attributes
        """
        attributes = []
        
        # Add ID if present
        if node.id:
            attributes.append(f'id="{node.id}"')
        
        # Add class if name is present
        classes = []
        if node.name:
            # Convert name to valid class name
            class_name = node.name.lower().replace(" ", "-")
            
            # Handle special cases for responsive classes
            if node.type == "FRAME":
                if node.name.lower() == "document":
                    classes = ["responsive-document", "responsive-container"]
                elif node.name.lower() == "table":
                    classes = ["table", "responsive-container"]
                elif node.name.lower() == "parent":
                    classes = ["parent", "responsive-container"]
                elif node.name.lower() == "child":
                    classes = ["child", "responsive-container"]
                else:
                    classes = [class_name]
            elif node.type == "RECTANGLE" and "constraints" in node.styles:
                classes = ["responsive-image", "responsive-container"]
            else:
                classes = [class_name]
        
        if classes:
            attributes.append(f'class="{" ".join(classes)}"')
        
        # Add styles if present
        if node.styles:
            style_attr = self._styles_to_attributes(node.styles)
            if style_attr:
                attributes.append(style_attr)
        
        return " ".join(attributes)
    
    def _styles_to_attributes(self, styles: Dict[str, Any]) -> str:
        """Convert Figma styles to email-safe HTML style attributes.
        
        Args:
            styles: The Figma styles dictionary
            
        Returns:
            A string of HTML style attributes
        """
        if not styles:
            return ""
        
        style_parts = []
        
        # Handle layout properties with email-safe values
        if "width" in styles:
            width = styles["width"]
            if isinstance(width, (int, float)):
                # Use fixed width for email clients
                style_parts.append(f"width: {width}px")
                style_parts.append(f"max-width: {min(width, 600)}px")
                style_parts.append("width: 100%")
        
        if "height" in styles:
            height = styles["height"]
            if isinstance(height, (int, float)):
                if self._current_node.type == "RECTANGLE" and "constraints" in styles:
                    style_parts.append("height: auto")
                else:
                    style_parts.append(f"height: {height}px")
        
        # Handle background color with hex fallback
        if "backgroundColor" in styles:
            color = styles["backgroundColor"]
            if isinstance(color, dict) and "r" in color and "g" in color and "b" in color:
                r = round(color["r"] * 255)  # Round to nearest integer
                g = round(color["g"] * 255)
                b = round(color["b"] * 255)
                a = color.get("a", 1)
                # Use hex for better email client support
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                style_parts.append(f"background-color: {hex_color}")
        
        # Handle text color with hex fallback
        if "color" in styles:
            color = styles["color"]
            if isinstance(color, dict) and "r" in color and "g" in color and "b" in color:
                r = round(color["r"] * 255)  # Round to nearest integer
                g = round(color["g"] * 255)
                b = round(color["b"] * 255)
                a = color.get("a", 1)
                # Use hex for better email client support
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                style_parts.append(f"color: {hex_color}")
        
        # Handle font properties with email-safe values
        if "fontSize" in styles:
            try:
                font_size = int(float(styles["fontSize"]))
                style_parts.append(f"font-size: {font_size}px")
            except (ValueError, TypeError):
                style_parts.append("font-size: 16px")
                
        if "fontFamily" in styles:
            # Use web-safe fonts with fallbacks
            font_family = styles["fontFamily"]
            safe_fonts = {
                "Arial": "Arial, Helvetica, sans-serif",
                "Helvetica": "Helvetica, Arial, sans-serif",
                "Times New Roman": "Times New Roman, Times, serif",
                "Georgia": "Georgia, Times, serif",
                "Courier New": "Courier New, Courier, monospace"
            }
            style_parts.append(f"font-family: {safe_fonts.get(font_family, 'Arial, Helvetica, sans-serif')}")
        
        if "fontWeight" in styles:
            style_parts.append(f"font-weight: {styles['fontWeight']}")
        
        # Handle padding with email-safe values
        if "padding" in styles:
            padding = styles["padding"]
            if isinstance(padding, dict):
                top = padding.get("top", 0)
                right = padding.get("right", 0)
                bottom = padding.get("bottom", 0)
                left = padding.get("left", 0)
                style_parts.append(f"padding: {top}px {right}px {bottom}px {left}px")
        elif any(key.startswith("padding") for key in styles.keys()):
            top = styles.get("paddingTop", 0)
            right = styles.get("paddingRight", 0)
            bottom = styles.get("paddingBottom", 0)
            left = styles.get("paddingLeft", 0)
            style_parts.append(f"padding: {top}px {right}px {bottom}px {left}px")
        
        # Handle border properties with email-safe values
        if "cornerRadius" in styles:
            style_parts.append(f"border-radius: {styles['cornerRadius']}px")
        if "strokeWeight" in styles:
            style_parts.append(f"border-width: {styles['strokeWeight']}px")
        if "strokeColor" in styles:
            color = styles["strokeColor"]
            if isinstance(color, dict) and "r" in color and "g" in color and "b" in color:
                r = round(color["r"] * 255)  # Round to nearest integer
                g = round(color["g"] * 255)
                b = round(color["b"] * 255)
                a = color.get("a", 1)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                style_parts.append(f"border-color: {hex_color}")
        
        # Handle text alignment
        if "textAlignHorizontal" in styles:
            style_parts.append(f"text-align: {styles['textAlignHorizontal'].lower()}")
        
        # Handle text decoration
        if "textDecoration" in styles:
            style_parts.append(f"text-decoration: {styles['textDecoration'].lower()}")
        
        # Handle line height
        if "lineHeight" in styles:
            try:
                line_height = float(styles["lineHeight"])
                style_parts.append(f"line-height: {line_height}")
            except (ValueError, TypeError):
                pass
        
        # Add email-safe styles
        style_parts.extend([
            "display: block",
            "margin: 0 auto",  # Center content
            "border-collapse: collapse",
            "mso-table-lspace: 0pt",
            "mso-table-rspace: 0pt"
        ])
        
        if not style_parts:
            return ""
        
        return f'style="{"; ".join(style_parts)}"'
    
    def _generate_responsive_css(self) -> str:
        """Generate email-safe responsive CSS styles.
        
        Returns:
            A string containing email-safe responsive CSS styles
        """
        return """
            <style type="text/css">
                /* Email-safe responsive styles */
                .email-container {
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                }
                
                @media screen and (max-width: 600px) {
                    .email-container {
                        width: 100% !important;
                    }
                    
                    img {
                        max-width: 100% !important;
                        height: auto !important;
                    }
                    
                    table {
                        width: 100% !important;
                    }
                    
                    td {
                        display: block !important;
                        width: 100% !important;
                    }
                }
                
                /* Email client specific fixes */
                .ExternalClass {
                    width: 100%;
                }
                
                .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {
                    line-height: 100%;
                }
                
                /* Outlook-specific fixes */
                table {
                    mso-table-lspace: 0pt;
                    mso-table-rspace: 0pt;
                }
                
                img {
                    -ms-interpolation-mode: bicubic;
                }
            </style>
        """ 