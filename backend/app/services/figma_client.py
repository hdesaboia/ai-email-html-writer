from typing import Dict, Optional, Any, List
import requests
from pydantic import BaseModel, Field, validator
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.core.exceptions import FigmaAPIError, FigmaValidationError
from app.utils.cache import cache_figma_data


class FigmaFile(BaseModel):
    """Represents a Figma file with its metadata."""
    key: str
    name: str
    last_modified: str
    thumbnail_url: Optional[str] = None
    version: str = Field(..., description="Version of the file")

    @validator('key')
    def validate_key(cls, v):
        if not v or not isinstance(v, str) or len(v) < 5:
            raise FigmaValidationError("Invalid Figma file key")
        return v


class FigmaNode(BaseModel):
    """Represents a Figma node (component, frame, etc.)."""
    id: str
    name: str
    type: str
    children: Optional[List['FigmaNode']] = None
    style: Optional[Dict[str, Any]] = None
    absoluteBoundingBox: Optional[Dict[str, float]] = None

    @validator('type')
    def validate_type(cls, v):
        valid_types = {'FRAME', 'COMPONENT', 'INSTANCE', 'GROUP', 'VECTOR', 'TEXT', 'RECTANGLE', 'IMAGE'}
        if v not in valid_types:
            raise FigmaValidationError(f"Invalid node type: {v}")
        return v


class FigmaClient:
    """Client for interacting with the Figma API.
    
    This service handles:
    - Authentication with Figma API
    - File fetching and parsing
    - Node extraction and processing
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize the Figma client.
        
        Args:
            access_token: Figma personal access token. If not provided,
                         will use the one from settings.
        """
        self.access_token = access_token or settings.FIGMA_ACCESS_TOKEN
        self.base_url = "https://api.figma.com/v1"
        self.headers = {
            "X-Figma-Token": self.access_token,
            "Content-Type": "application/json"
        }
        self._validate_token()
    
    def _validate_token(self) -> None:
        """Validate the Figma access token."""
        if not self.access_token:
            raise FigmaValidationError("Figma access token is required")
        
        try:
            response = requests.get(f"{self.base_url}/me", headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise FigmaAPIError("Invalid Figma access token", getattr(e.response, 'status_code', None))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda _: None  # Return None on final failure
    )
    @cache_figma_data(expire_seconds=3600)
    def get_file(self, file_key: str) -> FigmaFile:
        """Fetch a Figma file by its key with retries and caching."""
        try:
            url = f"{self.base_url}/files/{file_key}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return FigmaFile(
                key=file_key,
                name=data.get("name", ""),
                last_modified=data.get("lastModified", ""),
                thumbnail_url=data.get("thumbnailUrl"),
                version=data.get("version", "")
            )
        except requests.exceptions.RequestException as e:
            raise FigmaAPIError(f"Failed to fetch Figma file: {str(e)}", 
                              getattr(e.response, 'status_code', None))
        except FigmaValidationError as e:
            raise FigmaValidationError(f"Invalid Figma file data: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda _: None
    )
    @cache_figma_data(expire_seconds=3600)
    def get_file_nodes(self, file_key: str, node_ids: Optional[List[str]] = None) -> Dict[str, FigmaNode]:
        """Fetch specific nodes from a Figma file with retries and caching.
        
        Args:
            file_key: The key of the Figma file
            node_ids: List of node IDs to fetch. If None, fetches the entire file.
            
        Returns:
            Dictionary mapping node IDs to FigmaNode objects
        """
        try:
            if node_ids and "0:0" in node_ids:
                # Special case for root node - fetch the entire file
                url = f"{self.base_url}/files/{file_key}"
                print(f"Fetching root node from URL: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                print(f"Response status: {response.status_code}")
                print(f"Response data keys: {list(data.keys())}")
                document = data.get("document")
                if not document:
                    print("No document found in response")
                    return {}
                print(f"Document keys: {list(document.keys())}")
                # Set the ID to "0:0" for the root node
                document["id"] = "0:0"
                return {"0:0": self._process_node(document)}
            elif node_ids:
                # Fetch specific nodes
                url = f"{self.base_url}/files/{file_key}/nodes"
                params = {"ids": ",".join(node_ids)}
                print(f"Fetching nodes from URL: {url} with params: {params}")
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                print(f"Response status: {response.status_code}")
                print(f"Response data keys: {list(data.keys())}")
                nodes_data = data.get("nodes", {})
                nodes = {}
                for node_id, node_info in nodes_data.items():
                    if node_info.get("document"):
                        nodes[node_id] = self._process_node(node_info["document"])
                return nodes
            else:
                # Fetch the entire file
                url = f"{self.base_url}/files/{file_key}"
                print(f"Fetching entire file from URL: {url}")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                print(f"Response status: {response.status_code}")
                print(f"Response data keys: {list(data.keys())}")
                document = data.get("document")
                if not document:
                    print("No document found in response")
                    return {}
                print(f"Document keys: {list(document.keys())}")
                # Set the ID to "0:0" for the root node
                document["id"] = "0:0"
                return {"0:0": self._process_node(document)}
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            raise FigmaAPIError(f"Failed to fetch Figma nodes: {str(e)}", 
                              getattr(e.response, 'status_code', None))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda _: None
    )
    @cache_figma_data(expire_seconds=3600)
    def get_image_urls(self, file_key: str, node_ids: List[str]) -> Dict[str, str]:
        """Fetch image URLs for nodes with retries and caching."""
        try:
            url = f"{self.base_url}/images/{file_key}"
            params = {
                "ids": ','.join(node_ids),
                "format": "png",
                "scale": "2"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("images", {})
        except requests.exceptions.RequestException as e:
            raise FigmaAPIError(f"Failed to fetch image URLs: {str(e)}", 
                              getattr(e.response, 'status_code', None))
    
    def get_component_sets(self, file_key: str) -> Dict[str, FigmaNode]:
        """Get all component sets from a Figma file.
        
        Args:
            file_key: The key of the Figma file
            
        Returns:
            Dictionary mapping component set IDs to FigmaNode objects
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        nodes = self.get_file_nodes(file_key)
        component_sets = {}
        
        def find_component_sets(node: FigmaNode) -> None:
            """Recursively find component sets in the node tree."""
            if node.type == "COMPONENT_SET":
                component_sets[node.id] = node
            
            if node.children:
                for child in node.children:
                    find_component_sets(child)
        
        for node in nodes.values():
            find_component_sets(node)
        
        return component_sets

    def _process_node(self, node_data: Dict[str, Any]) -> FigmaNode:
        """Process a node and its children recursively.
        
        Args:
            node_data: Dictionary containing node data from Figma API
            
        Returns:
            FigmaNode object with processed data
            
        Raises:
            FigmaValidationError: If node data is invalid
        """
        try:
            # Validate required fields
            if "id" not in node_data:
                print(f"Node data missing ID: {node_data}")
                raise FigmaValidationError("Missing required field 'id' in node data")
            if "type" not in node_data:
                print(f"Node data missing type: {node_data}")
                raise FigmaValidationError("Missing required field 'type' in node data")
            
            print(f"Processing node: {node_data.get('name', 'unnamed')} ({node_data['type']}, id: {node_data['id']})")
            
            children = None
            if "children" in node_data:
                print(f"Processing {len(node_data['children'])} children")
                children = []
                for child in node_data["children"]:
                    try:
                        processed_child = self._process_node(child)
                        children.append(processed_child)
                    except FigmaValidationError as e:
                        print(f"Warning: Failed to process child node: {str(e)}")
                        continue
            
            node = FigmaNode(
                id=node_data["id"],
                name=node_data.get("name", ""),
                type=node_data["type"],
                children=children,
                style=node_data.get("style"),
                absoluteBoundingBox=node_data.get("absoluteBoundingBox")
            )
            print(f"Successfully processed node: {node.name} ({node.type}, id: {node.id})")
            return node
            
        except KeyError as e:
            print(f"Missing required field in node data: {str(e)}")
            print(f"Node data: {node_data}")
            raise FigmaValidationError(f"Missing required field in node data: {str(e)}")
        except Exception as e:
            print(f"Error processing node: {str(e)}")
            print(f"Node data: {node_data}")
            raise FigmaValidationError(f"Invalid node data: {str(e)}") 