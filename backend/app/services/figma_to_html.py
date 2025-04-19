from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from app.services.figma_client import FigmaClient, FigmaNode
from app.core.exceptions import FigmaConversionError
from app.utils.cache import cache_figma_data


class FigmaToHTMLConverter:
    """Service for converting Figma designs to HTML.
    
    This service handles:
    - Converting Figma nodes to HTML elements
    - Processing styles and layouts
    - Handling responsive design
    - Managing images and assets
    """
    
    def __init__(self, figma_client: Optional[FigmaClient] = None):
        """Initialize the converter.
        
        Args:
            figma_client: Optional FigmaClient instance. If not provided,
                         a new one will be created.
        """
        self.figma_client = figma_client or FigmaClient()
        self._component_cache: Dict[str, str] = {}
        self._variable_values: Dict[str, Any] = {}
    
    def set_variable_values(self, values: Dict[str, Any]) -> None:
        """Set values for Figma variables."""
        self._variable_values = values
    
    @cache_figma_data(expire_seconds=3600)
    def convert_to_html(self, file_key: str, node_id: Optional[str] = None,
                       responsive: bool = True) -> str:
        """Convert a Figma design to HTML with caching."""
        try:
            # Get the nodes from the Figma file
            nodes = self.figma_client.get_file_nodes(file_key, [node_id] if node_id else None)
            
            # If a specific node is requested, use it; otherwise use the root node
            root_node = nodes.get(node_id) if node_id else next(iter(nodes.values()))
            if not root_node:
                raise FigmaConversionError(f"Node {node_id} not found in file {file_key}")
            
            # Create the HTML document
            soup = BeautifulSoup("", "html.parser")
            html = soup.new_tag("html")
            head = soup.new_tag("head")
            body = soup.new_tag("body")
            
            # Add meta tags
            self._add_meta_tags(head)
            
            # Add styles
            self._add_styles(head, responsive)
            
            # Convert the root node to HTML
            self._convert_node_to_html(root_node, body, file_key)
            
            # Add responsive scripts if needed
            if responsive:
                self._add_responsive_scripts(head)
            
            # Assemble the document
            html.append(head)
            html.append(body)
            soup.append(html)
            
            return str(soup)
        except Exception as e:
            raise FigmaConversionError(f"Failed to convert Figma design: {str(e)}")
    
    def _add_meta_tags(self, head: Any) -> None:
        """Add necessary meta tags to the head."""
        # Viewport meta
        viewport = head.new_tag("meta")
        viewport["name"] = "viewport"
        viewport["content"] = "width=device-width, initial-scale=1.0"
        head.append(viewport)
        
        # Character encoding
        charset = head.new_tag("meta")
        charset["charset"] = "UTF-8"
        head.append(charset)

    def _add_styles(self, head: Any, responsive: bool) -> None:
        """Add styles to the head."""
        style = head.new_tag("style")
        style.string = """
            /* Reset styles */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            /* Email client compatibility */
            body { margin: 0; padding: 0; width: 100% !important; }
            table { border-collapse: collapse; }
            img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
            
            /* Component styles */
            .figma-component { display: block; max-width: 100%; }
            .figma-frame { position: relative; }
            .figma-text { font-family: inherit; }
            .figma-image { max-width: 100%; height: auto; }
        """
        
        if responsive:
            style.string += """
                /* Responsive styles */
                @media screen and (max-width: 600px) {
                    .mobile-full-width { width: 100% !important; }
                    .mobile-stack { display: block !important; }
                    .mobile-center { text-align: center !important; }
                    .mobile-hide { display: none !important; }
                }
            """
        
        head.append(style)

    def _add_responsive_scripts(self, head: Any) -> None:
        """Add responsive behavior scripts."""
        script = head.new_tag("script")
        script.string = """
            document.addEventListener('DOMContentLoaded', function() {
                // Add mobile classes based on screen size
                function updateResponsiveClasses() {
                    const isMobile = window.innerWidth <= 600;
                    document.querySelectorAll('.figma-frame').forEach(frame => {
                        frame.classList.toggle('mobile-full-width', isMobile);
                        frame.classList.toggle('mobile-stack', isMobile);
                    });
                }
                
                window.addEventListener('resize', updateResponsiveClasses);
                updateResponsiveClasses();
            });
        """
        head.append(script)

    def _convert_node_to_html(self, node: FigmaNode, parent: Any, file_key: str) -> None:
        """Convert a Figma node to HTML with component reuse."""
        try:
            # Check if this is a component instance and we have it cached
            if node.type == "INSTANCE" and node.id in self._component_cache:
                element = BeautifulSoup(self._component_cache[node.id], "html.parser")
                parent.append(element)
                return
            
            # Create the appropriate HTML element
            element = self._create_element(node, parent, file_key)
            
            # Apply styles and attributes
            self._apply_styles(element, node)
            
            # Process children
            if node.children:
                for child in node.children:
                    self._convert_node_to_html(child, element, file_key)
            
            # Cache component if needed
            if node.type == "COMPONENT":
                self._component_cache[node.id] = str(element)
            
            parent.append(element)
        except Exception as e:
            raise FigmaConversionError(f"Failed to convert node {node.id}: {str(e)}")

    def _create_element(self, node: FigmaNode, parent: Any, file_key: str) -> Any:
        """Create an HTML element based on node type."""
        if node.type == "FRAME":
            element = parent.new_tag("div")
            element["class"] = "figma-frame"
        elif node.type == "TEXT":
            element = parent.new_tag("p")
            element["class"] = "figma-text"
            # Apply any text variables
            text_content = node.name
            for var_name, value in self._variable_values.items():
                text_content = text_content.replace(f"${var_name}", str(value))
            element.string = text_content
        elif node.type == "RECTANGLE":
            element = parent.new_tag("div")
            element["class"] = "figma-rectangle"
        elif node.type == "IMAGE":
            element = parent.new_tag("img")
            element["class"] = "figma-image"
            # Get the image URL
            image_urls = self.figma_client.get_image_urls(file_key, [node.id])
            if node.id in image_urls:
                element["src"] = image_urls[node.id]
                element["alt"] = node.name
        else:
            element = parent.new_tag("div")
            element["class"] = f"figma-{node.type.lower()}"
        
        return element

    def _apply_styles(self, element: Any, node: FigmaNode) -> None:
        """Apply styles to an HTML element."""
        if not node.style:
            return
        
        style_str = ""
        
        # Position and size
        if node.absoluteBoundingBox:
            bbox = node.absoluteBoundingBox
            style_str += f"width: {bbox.get('width', 'auto')}px; "
            style_str += f"height: {bbox.get('height', 'auto')}px; "
        
        # Colors and typography
        if "fill" in node.style:
            style_str += f"background-color: {node.style['fill']}; "
        if "color" in node.style:
            style_str += f"color: {node.style['color']}; "
        if "fontSize" in node.style:
            style_str += f"font-size: {node.style['fontSize']}px; "
        if "fontFamily" in node.style:
            style_str += f"font-family: {node.style['fontFamily']}; "
        
        # Apply the styles
        if style_str:
            element["style"] = style_str
    
    def _convert_styles_to_css(self, styles: Dict[str, Any]) -> str:
        """Convert Figma styles to CSS.
        
        Args:
            styles: Dictionary of Figma styles
            
        Returns:
            CSS string
        """
        css_properties = []
        
        if "color" in styles:
            color = styles["color"]
            if isinstance(color, dict):
                r = int(color.get("r", 0) * 255)
                g = int(color.get("g", 0) * 255)
                b = int(color.get("b", 0) * 255)
                a = color.get("a", 1)
                css_properties.append(f"background-color: rgba({r}, {g}, {b}, {a})")
        
        if "fontSize" in styles:
            css_properties.append(f"font-size: {styles['fontSize']}px")
        
        if "fontFamily" in styles:
            css_properties.append(f"font-family: {styles['fontFamily']}")
        
        if "textAlign" in styles:
            css_properties.append(f"text-align: {styles['textAlign']}")
        
        return "; ".join(css_properties) 