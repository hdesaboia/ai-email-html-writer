from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class FigmaNode(BaseModel):
    """Represents a Figma node with its properties."""
    id: str
    name: str
    type: str
    children: List['FigmaNode'] = Field(default_factory=list)
    styles: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True

# Update forward refs for the FigmaNode class to handle self-referential type
FigmaNode.update_forward_refs()

class FigmaFile(BaseModel):
    """Represents a Figma file with its metadata and nodes."""
    key: str
    name: str
    last_modified: str
    thumbnail_url: Optional[str] = None
    version: str
    document: Optional[Dict[str, Any]] = None
    nodes: Dict[str, FigmaNode] = Field(default_factory=dict)

    def get_root_node(self) -> Optional[FigmaNode]:
        """Get the root node of the document.
        
        Returns:
            The root FigmaNode if available, None otherwise
        """
        if not self.document:
            return None
        return FigmaNode(**self.document) 