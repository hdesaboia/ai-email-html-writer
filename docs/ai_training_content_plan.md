# AI Training Content Plan

## 1. Training Data Sources

### A. Figma Design System
1. **Typography Components**
   - Source: Figma file `hj82PYYXyGJnpo3lF9BMLI`
   - Node ID: `5884:903`
   - Components to extract:
     - Headlines (H1, H2, H3)
     - Body Text
     - Special Text (Eyebrow, Caption, Testimonial, CTA, Legal, Hyperlink)
     - Numbers
     - Form Elements
     - Navigation

2. **Color System**
   - Source: Figma file `hj82PYYXyGJnpo3lF9BMLI`
   - Node ID: `5884:3590`
   - Components to extract:
     - Background Colors:
       - White (#FFFFFF): Email logo header, Background 1, Social icons
       - Evergreen (#007B34): Buttons (primary and secondary), Icons, Social icons
       - Oat (#FFFBED): Background 2
       - Light grey (#EDEDED): Background 3
       - Lime 30% (#EDEDED): Background 4, Bullets
     - Text Colors:
       - Dark grey (#373938): Headlines and subheads, Small numbers
       - Mid grey (#848484): Legal copy
       - White (#FFFFFF): CTA copy (primary and secondary)
       - Evergreen (#007B34): Headlines and subheads, CTA copy (primary and secondary), Hyperlink

3. **Layout Components**
   - Source: Figma file `hj82PYYXyGJnpo3lF9BMLI`
   - Node ID: `5914:688`
   - Components to extract:
     - Spacing System:
       - Desktop Padding Components (5 variations)
       - Mobile Padding Components (5 variations)
     - Device Layouts:
       - Desktop:
         - Width: 600px
         - Layout Options:
           - Preferred: Single-column
           - Supported: Two-column
       - Mobile:
         - Width:
           - Minimum: 320px
           - Standard: 420px
         - Layout Requirements:
           - Must use single-column layout
           - Ensures seamless content adjustment
           - Maintains design quality
     - Usage Guidelines:
       - Section Separation: Use padding 6 (40px) between sections with background color changes
       - Component Spacing:
         - Headline to Body Copy: padding 3 (16px)
         - Headline to Image: padding 4 (24px)
         - Body Copy to CTA: padding 4 (24px)
         - Image to Body Copy: padding 3 (16px)
     - Component-Specific Padding:
       - Components with built-in padding:
         - Incentives
         - Spanish header/footer
         - Questions
     - Examples:
       - Desktop email with padding highlights
       - Mobile email with padding highlights

4. **Image Guidelines**
   - Source: Figma file `hj82PYYXyGJnpo3lF9BMLI`
   - Components to extract:
     - Static Images:
       - Single image approach for both desktop and mobile
       - Use larger size images for optimal quality
       - Responsive image handling
       - Accessibility:
         - Alt text must be provided by creative team
         - Alt text should be descriptive and meaningful
         - Alt text should be included in final deliverables
     - Animated GIFs:
       - File size limits:
         - Ideal: <250KB
         - Maximum: <1MB
       - Requirements:
         - Must include static fallback image
         - Fallback image should match GIF dimensions
         - Fallback image should represent key frame
       - Accessibility:
         - Alt text must be provided by creative team
         - Alt text should describe the animation content
         - Alt text should be included in final deliverables

### B. Email Templates
1. **Existing Email Examples**
   - Source: Iterable HTML exports
   - Components to extract:
     - Email Structure
     - Component Usage
     - Responsive Patterns
     - Email Client Compatibility

2. **Component Library**
   - Source: Coded components
   - Components to extract:
     - HTML Structure
     - CSS Properties
     - Responsive Behavior
     - Email Client Support

## 2. Training Data Structure

### A. Typography Training Data
```json
{
  "headlines": {
    "desktop": {
      "h1": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 40,
        "line_height": 1.2
      },
      "h2": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 28,
        "line_height": 1.2
      },
      "h3": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 20,
        "line_height": 1.2
      }
    },
    "mobile": {
      "h1": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 36,
        "line_height": 1.2
      },
      "h2": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 24,
        "line_height": 1.2
      },
      "h3": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 18,
        "line_height": 1.2
      }
    }
  },
  "body_text": {
    "regular": {
      "font_family": "Arial",
      "font_weight": "Regular",
      "font_size": 18,
      "line_height": 1.4
    },
    "bold": {
      "font_family": "Arial",
      "font_weight": "Bold",
      "font_size": 18,
      "line_height": 1.4
    }
  },
  "special_text": {
    "desktop": {
      "eyebrow": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 16,
        "line_height": 1.2,
        "letter_spacing": 3.2,
        "text_transform": "uppercase"
      },
      "caption": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 13,
        "line_height": 1.4
      },
      "testimonial": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 18,
        "line_height": 1.4,
        "font_style": "italic"
      },
      "cta": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 18,
        "line_height": 1.4
      },
      "legal": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 14,
        "line_height": 1.4
      },
      "hyperlink": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 18,
        "line_height": 1.4,
        "text_decoration": "underline"
      }
    },
    "mobile": {
      "eyebrow": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 16,
        "line_height": 1.2,
        "letter_spacing": 3.2,
        "text_transform": "uppercase"
      },
      "caption": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 12,
        "line_height": 1.4
      },
      "testimonial": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 18,
        "line_height": 1.4,
        "font_style": "italic"
      },
      "cta": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 18,
        "line_height": 1.4
      },
      "legal": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": 14,
        "line_height": 1.4
      },
      "hyperlink": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": 18,
        "line_height": 1.4,
        "text_decoration": "underline"
      }
    }
  }
}
```

### B. Component Training Data
```json
{
  "components": {
    "headline": {
      "html_template": "<h1 class='headline {{variant}}'>{{content}}</h1>",
      "css_properties": {
        "font_family": "Arial",
        "font_weight": "Bold",
        "font_size": "40px",
        "line_height": "1.2",
        "margin": "0 0 16px 0"
      },
      "variants": ["h1", "h2", "h3"],
      "responsive_rules": {
        "mobile": {
          "font_size": "36px"
        }
      }
    },
    "body_text": {
      "html_template": "<p class='body-text {{variant}}'>{{content}}</p>",
      "css_properties": {
        "font_family": "Arial",
        "font_weight": "Regular",
        "font_size": "18px",
        "line_height": "1.4",
        "margin": "0 0 16px 0"
      },
      "variants": ["regular", "bold"]
    }
  }
}
```

### C. Image Training Data
```json
{
  "image_guidelines": {
    "static_images": {
      "approach": "single_image",
      "quality_guidelines": {
        "use_larger_size": true,
        "responsive_handling": true
      },
      "accessibility": {
        "alt_text_required": true,
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
    "animated_gifs": {
      "file_size": {
        "ideal": 250000,
        "maximum": 1000000
      },
      "requirements": {
        "static_fallback": true,
        "fallback_guidelines": {
          "match_dimensions": true,
          "represent_key_frame": true
        }
      },
      "accessibility": {
        "alt_text_required": true,
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
  }
}
```

### D. Spacing Training Data
```json
{
  "spacing_system": {
    "desktop": {
      "padding_components": [
        {
          "name": "padding_1",
          "value": 8,
          "unit": "px"
        },
        {
          "name": "padding_2",
          "value": 16,
          "unit": "px"
        },
        {
          "name": "padding_3",
          "value": 24,
          "unit": "px"
        },
        {
          "name": "padding_4",
          "value": 32,
          "unit": "px"
        },
        {
          "name": "padding_5",
          "value": 40,
          "unit": "px"
        }
      ]
    },
    "mobile": {
      "padding_components": [
        {
          "name": "padding_1",
          "value": 8,
          "unit": "px"
        },
        {
          "name": "padding_2",
          "value": 16,
          "unit": "px"
        },
        {
          "name": "padding_3",
          "value": 24,
          "unit": "px"
        },
        {
          "name": "padding_4",
          "value": 32,
          "unit": "px"
        },
        {
          "name": "padding_5",
          "value": 40,
          "unit": "px"
        }
      ]
    },
    "usage_guidelines": {
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
  }
}
```

### E. Layout Training Data
```json
{
  "device_layouts": {
    "desktop": {
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
    "mobile": {
      "width": {
        "minimum": 320,
        "standard": 420,
        "unit": "px"
      },
      "layout_requirements": {
        "must_use_single_column": true,
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
  }
}
```

## 3. Training Process

### A. Phase 1: Data Collection
1. Extract typography data from Figma
2. Extract color system data
3. Extract layout components
4. Collect email template examples

### B. Phase 2: Data Processing
1. Convert Figma styles to email-safe CSS
2. Create component templates
3. Document responsive patterns
4. Validate against email clients

### C. Phase 3: Training Data Preparation
1. Structure data in JSON format
2. Create training examples
3. Add validation rules
4. Document edge cases

## 4. Success Metrics

### A. Component Recognition
- 95% accuracy in identifying typography components
- 90% accuracy in applying correct styles
- 85% accuracy in handling responsive variations

### B. Email Generation
- 90% accuracy in generating email-safe HTML
- 85% accuracy in maintaining responsive design
- 80% accuracy in handling dynamic content

## 5. Next Steps

1. Extract color system data from Figma
2. Create color training data structure
3. Develop component recognition training
4. Build email generation training set 