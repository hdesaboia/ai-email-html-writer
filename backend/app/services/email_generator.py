from typing import Dict, Optional, Any
import re
from bs4 import BeautifulSoup
from jinja2 import Template, Environment, select_autoescape
from premailer import transform
from app.services.figma_to_html import FigmaToHTMLConverter
from app.services.figma_client import FigmaClient
from app.core.exceptions import FigmaConversionError
from app.utils.cache import cache_figma_data

from app.models.email_template import EmailTemplate
from app.schemas.email_template import EmailTemplate as EmailTemplateSchema


class EmailGenerator:
    """Service for generating HTML emails from Figma designs."""
    
    def __init__(self):
        """Initialize the email generator."""
        self.env = Environment(
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.email_clients = {
            'outlook': {
                'fixes': {
                    'table': 'mso-table-lspace:0pt;mso-table-rspace:0pt;',
                    'td': 'mso-table-lspace:0pt;mso-table-rspace:0pt;',
                    'img': 'display:block;',
                    'div': 'mso-table-lspace:0pt;mso-table-rspace:0pt;'
                }
            },
            'gmail': {
                'fixes': {
                    'table': 'border-collapse:collapse;border-spacing:0;',
                    'td': 'border-collapse:collapse;',
                    'img': 'display:block;outline:none;text-decoration:none;',
                    'div': 'display:block;'
                }
            }
        }
        self.figma_client = FigmaClient()
        self.converter = FigmaToHTMLConverter(self.figma_client)
    
    @cache_figma_data(expire_seconds=3600)
    def generate_email(self, template_data: Dict[str, Any], preview: bool = False) -> str:
        """Generate an HTML email from a Figma design.
        
        Args:
            template_data: Dictionary containing:
                - figma_file_key: Key of the Figma file
                - figma_node_id: Optional ID of the specific node to use
                - variables: Optional dictionary of variable values
            preview: Whether to generate a preview version
            
        Returns:
            Generated HTML email content
            
        Raises:
            FigmaConversionError: If conversion fails
        """
        try:
            # Extract template data
            file_key = template_data.get("figma_file_key")
            node_id = template_data.get("figma_node_id")
            variables = template_data.get("variables", {})
            
            if not file_key:
                raise FigmaConversionError("Figma file key is required")
            
            # Set variable values for the converter
            self.converter.set_variable_values(variables)
            
            # Convert Figma design to HTML
            html = self.converter.convert_to_html(
                file_key=file_key,
                node_id=node_id,
                responsive=True
            )
            
            # Process the HTML
            processed_html = self._process_html(html, preview)
            
            return processed_html
        except Exception as e:
            raise FigmaConversionError(f"Failed to generate email: {str(e)}")
    
    def _process_html(self, html: str, preview: bool = False) -> str:
        """Process HTML content for email compatibility."""
        try:
            # Parse the HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # Optimize for email clients
            self._optimize_for_email(soup)
            
            # Add preview modifications if needed
            if preview:
                self._add_preview_modifications(soup)
            
            # Convert CSS to inline styles
            html_string = str(soup)
            inlined_html = transform(html_string)
            
            # Validate the HTML
            self._validate_html(inlined_html)
            
            return inlined_html
        except Exception as e:
            raise FigmaConversionError(f"Failed to process HTML: {str(e)}")
    
    def _optimize_for_email(self, soup: BeautifulSoup) -> None:
        """Optimize HTML for email client compatibility."""
        # Convert divs to tables where appropriate
        for div in soup.find_all("div", class_="figma-frame"):
            table = soup.new_tag("table")
            table["cellpadding"] = "0"
            table["cellspacing"] = "0"
            table["border"] = "0"
            table["width"] = "100%"
            
            tr = soup.new_tag("tr")
            td = soup.new_tag("td")
            
            # Move div's contents to td
            td.extend(div.contents)
            # Copy div's attributes to td
            for attr, value in div.attrs.items():
                if attr != "class":
                    td[attr] = value
            
            tr.append(td)
            table.append(tr)
            div.replace_with(table)
        
        # Fix image display
        for img in soup.find_all("img"):
            img["display"] = "block"
            if not img.get("alt"):
                img["alt"] = ""
        
        # Add MSO conditional comments for Outlook
        body = soup.find("body")
        if body:
            outlook_wrapper = soup.new_tag("div")
            outlook_wrapper.string = "<!--[if mso]><table width='100%' cellpadding='0' cellspacing='0' border='0'><tr><td><![endif]-->"
            body.insert(0, outlook_wrapper)
            
            outlook_closer = soup.new_tag("div")
            outlook_closer.string = "<!--[if mso]></td></tr></table><![endif]-->"
            body.append(outlook_closer)

    def _add_preview_modifications(self, soup: BeautifulSoup) -> None:
        """Add preview-specific modifications."""
        # Add preview header
        header = soup.new_tag("div")
        header["style"] = """
            background-color: #f8f9fa;
            color: #6c757d;
            padding: 10px;
            text-align: center;
            font-family: Arial, sans-serif;
            border-bottom: 1px solid #dee2e6;
        """
        header.string = "Email Preview"
        
        body = soup.find("body")
        if body:
            body.insert(0, header)
        
        # Add preview border
        if body:
            body["style"] = (body.get("style", "") + 
                           "border: 1px solid #dee2e6; max-width: 600px; margin: 0 auto;")

    def _validate_html(self, html: str) -> None:
        """Validate HTML content for email compatibility."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Check for required elements
        if not soup.find("html"):
            raise FigmaConversionError("Missing <html> tag")
        if not soup.find("head"):
            raise FigmaConversionError("Missing <head> tag")
        if not soup.find("body"):
            raise FigmaConversionError("Missing <body> tag")
        
        # Check for problematic elements
        problematic_tags = ["script", "iframe", "video", "audio", "canvas"]
        for tag in problematic_tags:
            if soup.find(tag):
                raise FigmaConversionError(f"Email contains unsupported <{tag}> tag")
        
        # Check for external resources
        for img in soup.find_all("img"):
            if not img.get("src", "").startswith(("http://", "https://")):
                raise FigmaConversionError("Image source must be an absolute URL")
        
        # Check for responsive design elements
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            raise FigmaConversionError("Missing viewport meta tag")
        
        # Check for media queries
        styles = soup.find_all("style")
        has_media_query = any("@media" in style.string for style in styles if style.string)
        if not has_media_query:
            raise FigmaConversionError("Missing responsive design media queries")

    def _add_responsive_design(self, soup: BeautifulSoup) -> None:
        """Add responsive design elements to the HTML.
        
        Args:
            soup: BeautifulSoup object containing the HTML
        """
        # Add viewport meta tag if not present
        if not soup.find('meta', attrs={'name': 'viewport'}):
            viewport = soup.new_tag('meta')
            viewport['name'] = 'viewport'
            viewport['content'] = 'width=device-width, initial-scale=1.0'
            soup.head.append(viewport)
        
        # Add responsive styles
        style = soup.new_tag('style')
        style.string = """
            /* Responsive styles */
            @media screen and (max-width: 600px) {
                .container {
                    width: 100% !important;
                    padding: 10px !important;
                }
                .column {
                    display: block !important;
                    width: 100% !important;
                }
                .mobile-padding {
                    padding: 10px !important;
                }
                img {
                    height: auto !important;
                    width: 100% !important;
                }
                .hide-mobile {
                    display: none !important;
                }
            }
        """
        soup.head.append(style)
        
        # Add responsive classes to containers
        for container in soup.find_all(['div', 'table'], class_=True):
            if 'container' in container['class']:
                container['class'].append('mobile-padding')
    
    def _optimize_for_email(self, soup: BeautifulSoup) -> None:
        """Optimize HTML for email clients.
        
        Args:
            soup: BeautifulSoup object containing the HTML
        """
        # Ensure all images have alt text and proper attributes
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = ''
            if not img.get('style'):
                img['style'] = 'display:block;border:0;height:auto;line-height:100%;outline:none;text-decoration:none;'
        
        # Convert relative URLs to absolute
        for tag in soup.find_all(['a', 'img']):
            if tag.get('src') and not tag['src'].startswith(('http://', 'https://')):
                tag['src'] = f"https://example.com/{tag['src'].lstrip('/')}"
            if tag.get('href') and not tag['href'].startswith(('http://', 'https://')):
                tag['href'] = f"https://example.com/{tag['href'].lstrip('/')}"
        
        # Add email-specific CSS
        style = soup.new_tag('style')
        style.string = """
            /* Reset styles for email clients */
            body { margin: 0; padding: 0; }
            img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
            table { border-collapse: collapse !important; }
            body, #bodyTable, #bodyCell { height: 100% !important; margin: 0; padding: 0; width: 100% !important; }
            /* Prevent Gmail from changing text sizes */
            * { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
            /* Prevent WebKit and Windows mobile from changing default text sizes */
            body { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        """
        soup.head.append(style)
    
    def _add_email_client_fixes(self, soup: BeautifulSoup) -> None:
        """Add email client specific fixes.
        
        Args:
            soup: BeautifulSoup object containing the HTML
        """
        # Apply Outlook fixes
        for tag_name, style in self.email_clients['outlook']['fixes'].items():
            for tag in soup.find_all(tag_name):
                if tag.get('style'):
                    tag['style'] += style
                else:
                    tag['style'] = style
        
        # Apply Gmail fixes
        for tag_name, style in self.email_clients['gmail']['fixes'].items():
            for tag in soup.find_all(tag_name):
                if tag.get('style'):
                    tag['style'] += style
                else:
                    tag['style'] = style
    
    def _add_preview_modifications(self, soup: BeautifulSoup) -> None:
        """Add modifications for preview mode.
        
        Args:
            soup: BeautifulSoup object containing the HTML
        """
        # Add preview border
        body = soup.find('body')
        if body:
            body['style'] = (body.get('style', '') + ' border: 2px dashed #ccc; padding: 10px;')
        
        # Add preview header
        header = soup.new_tag('div', style='background: #f5f5f5; padding: 10px; margin-bottom: 10px;')
        header.string = 'Email Preview'
        soup.body.insert(0, header)
    
    def _validate_html(self, html: str) -> None:
        """Validate the HTML content for email compatibility.
        
        Args:
            html: The HTML content to validate
            
        Raises:
            ValueError: If the HTML is invalid or incompatible with email clients
        """
        # Check for required elements
        soup = BeautifulSoup(html, 'html.parser')
        
        # Must have a body
        if not soup.find('body'):
            raise ValueError("HTML must contain a body element")
        
        # Check for common email client issues
        if len(soup.find_all('style')) > 1:
            raise ValueError("Multiple style tags are not recommended for email")
        
        # Check for inline styles (recommended for email)
        inline_styles = soup.find_all(style=True)
        if not inline_styles:
            raise ValueError("Email should use inline styles for better compatibility")
        
        # Check for responsive design elements
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            raise ValueError("Email should include viewport meta tag for responsive design")
        
        # Check for email-specific attributes
        for img in soup.find_all('img'):
            if not img.get('alt'):
                raise ValueError("All images must have alt text")
            
            if not img.get('style'):
                raise ValueError("Images should have inline styles for better email client compatibility")
            
            # Check for responsive image attributes
            if not any(attr in img.get('style', '') for attr in ['width', 'max-width']):
                raise ValueError("Images should have width or max-width specified for responsive design") 