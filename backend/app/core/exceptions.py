from typing import Optional

class FigmaIntegrationError(Exception):
    """Base exception for Figma integration errors."""
    pass

class FigmaAPIError(FigmaIntegrationError):
    """Raised when Figma API requests fail."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(f"Figma API Error: {message} (Status: {status_code})")

class FigmaValidationError(FigmaIntegrationError):
    """Raised when Figma data validation fails."""
    pass

class FigmaConversionError(FigmaIntegrationError):
    """Raised when HTML conversion fails."""
    pass

class FigmaCacheError(FigmaIntegrationError):
    """Raised when caching operations fail."""
    pass 