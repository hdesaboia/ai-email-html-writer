# Phase 2 Technical Specifications

## Figma Integration

### API Client
```python
class FigmaClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.figma.com/v1"

    async def get_file(self, file_key: str) -> Dict:
        """Fetch Figma file data"""
        pass

    async def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict:
        """Fetch specific nodes from a Figma file"""
        pass

    async def get_file_images(self, file_key: str, node_ids: List[str]) -> Dict:
        """Fetch images from Figma file"""
        pass
```

### Component Parser
```python
class ComponentParser:
    def __init__(self, figma_data: Dict):
        self.figma_data = figma_data

    def extract_components(self) -> List[Component]:
        """Extract components from Figma data"""
        pass

    def extract_styles(self) -> Dict[str, Style]:
        """Extract styles from Figma data"""
        pass

    def extract_layout(self) -> Layout:
        """Extract layout information"""
        pass
```

## AI Processing Engine

### Component Matching
```python
class ComponentMatcher:
    def __init__(self, template_library: TemplateLibrary):
        self.template_library = template_library

    def match_component(self, figma_component: Component) -> Template:
        """Match Figma component to HTML template"""
        pass

    def calculate_similarity(self, component: Component, template: Template) -> float:
        """Calculate similarity between component and template"""
        pass
```

### HTML Generation
```python
class HTMLGenerator:
    def __init__(self, matcher: ComponentMatcher):
        self.matcher = matcher

    def generate_html(self, components: List[Component]) -> str:
        """Generate HTML from matched components"""
        pass

    def apply_styles(self, html: str, styles: Dict[str, Style]) -> str:
        """Apply styles to generated HTML"""
        pass
```

## Frontend Components

### Design Input
```typescript
interface DesignInputProps {
  onFileSelect: (fileId: string, nodeId: string) => void;
  onError: (error: Error) => void;
}

const DesignInput: React.FC<DesignInputProps> = ({
  onFileSelect,
  onError,
}) => {
  // Implementation
};
```

### Preview Component
```typescript
interface PreviewProps {
  html: string;
  onUpdate: (html: string) => void;
}

const Preview: React.FC<PreviewProps> = ({
  html,
  onUpdate,
}) => {
  // Implementation
};
```

## Data Models

### Figma Component
```typescript
interface FigmaComponent {
  id: string;
  name: string;
  type: string;
  children: FigmaComponent[];
  styles: {
    [key: string]: string;
  };
  layout: {
    width: number;
    height: number;
    x: number;
    y: number;
  };
}
```

### HTML Template
```typescript
interface HTMLTemplate {
  id: string;
  name: string;
  html: string;
  styles: {
    [key: string]: string;
  };
  interpolations: {
    [key: string]: string;
  };
}
```

## API Endpoints

### Figma Integration
```typescript
// POST /api/v1/figma/parse
interface ParseFigmaRequest {
  file_id: string;
  node_id: string;
}

interface ParseFigmaResponse {
  components: FigmaComponent[];
  styles: {
    [key: string]: string;
  };
}
```

### HTML Generation
```typescript
// POST /api/v1/generate
interface GenerateHTMLRequest {
  components: FigmaComponent[];
  styles: {
    [key: string]: string;
  };
}

interface GenerateHTMLResponse {
  html: string;
  preview_url: string;
  decisions: {
    component_mappings: {
      [key: string]: string;
    };
    interpolations: string[];
  };
}
```

## Testing Strategy

### Figma Integration Tests
1. **API Tests**
   - File fetching
   - Node extraction
   - Image handling

2. **Parser Tests**
   - Component extraction
   - Style parsing
   - Layout analysis

### AI Processing Tests
1. **Component Matching**
   - Template matching accuracy
   - Similarity calculation
   - Edge case handling

2. **HTML Generation**
   - HTML output validation
   - Style application
   - Interpolation handling

### Frontend Tests
1. **Component Tests**
   - Design input validation
   - Preview rendering
   - User interaction

2. **Integration Tests**
   - API communication
   - Real-time updates
   - Error handling 