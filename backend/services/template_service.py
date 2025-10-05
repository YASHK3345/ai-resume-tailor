from typing import List, Dict, Any, Optional
from models.cv import CVTemplate
import uuid

class TemplateService:
    """Service for managing CV templates"""
    
    def __init__(self):
        self.default_templates = self._create_default_templates()
    
    def get_all_templates(self) -> List[CVTemplate]:
        """Get all available CV templates"""
        return self.default_templates
    
    def get_template_by_id(self, template_id: str) -> Optional[CVTemplate]:
        """Get a specific template by ID"""
        for template in self.default_templates:
            if template.id == template_id:
                return template
        return None
    
    def get_templates_by_category(self, category: str) -> List[CVTemplate]:
        """Get templates by category"""
        return [t for t in self.default_templates if t.category == category]
    
    def _create_default_templates(self) -> List[CVTemplate]:
        """Create default CV templates"""
        templates = []
        
        # Professional Templates
        templates.extend([
            CVTemplate(
                id="professional-classic",
                name="Professional Classic",
                description="Clean, traditional layout perfect for corporate roles",
                category="professional",
                is_premium=False,
                layout="single-column",
                styles={
                    "font_family": "Times New Roman, serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#2c3e50",
                        "secondary": "#34495e",
                        "accent": "#3498db"
                    },
                    "spacing": "normal",
                    "margins": "standard"
                }
            ),
            CVTemplate(
                id="professional-modern",
                name="Professional Modern",
                description="Contemporary design with subtle color accents",
                category="professional",
                is_premium=False,
                layout="single-column",
                styles={
                    "font_family": "Arial, sans-serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#1a1a1a",
                        "secondary": "#666666",
                        "accent": "#007acc"
                    },
                    "spacing": "compact",
                    "margins": "narrow"
                }
            ),
            CVTemplate(
                id="professional-executive",
                name="Executive",
                description="Sophisticated layout for senior positions",
                category="professional",
                is_premium=True,
                layout="two-column",
                styles={
                    "font_family": "Georgia, serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#2c2c54",
                        "secondary": "#706fd3",
                        "accent": "#ff4757"
                    },
                    "spacing": "normal",
                    "margins": "wide"
                }
            )
        ])
        
        # Creative Templates
        templates.extend([
            CVTemplate(
                id="creative-modern",
                name="Creative Modern",
                description="Bold design for creative professionals",
                category="creative",
                is_premium=False,
                layout="two-column",
                styles={
                    "font_family": "Helvetica, Arial, sans-serif",
                    "font_size": "10pt",
                    "colors": {
                        "primary": "#2c2c2c",
                        "secondary": "#f39c12",
                        "accent": "#e74c3c"
                    },
                    "spacing": "compact",
                    "margins": "narrow"
                }
            ),
            CVTemplate(
                id="creative-artistic",
                name="Artistic",
                description="Vibrant design for artists and designers",
                category="creative",
                is_premium=True,
                layout="two-column",
                styles={
                    "font_family": "Montserrat, sans-serif",
                    "font_size": "10pt",
                    "colors": {
                        "primary": "#2d3436",
                        "secondary": "#00b894",
                        "accent": "#fd79a8"
                    },
                    "spacing": "normal",
                    "margins": "standard"
                }
            ),
            CVTemplate(
                id="creative-minimalist",
                name="Minimalist Creative",
                description="Clean, minimal design with creative touches",
                category="creative",
                is_premium=False,
                layout="single-column",
                styles={
                    "font_family": "Lato, sans-serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#2c3e50",
                        "secondary": "#95a5a6",
                        "accent": "#1abc9c"
                    },
                    "spacing": "wide",
                    "margins": "wide"
                }
            )
        ])
        
        # Modern Templates
        templates.extend([
            CVTemplate(
                id="modern-tech",
                name="Tech Modern",
                description="Perfect for tech and startup roles",
                category="modern",
                is_premium=False,
                layout="two-column",
                styles={
                    "font_family": "Source Sans Pro, sans-serif",
                    "font_size": "10pt",
                    "colors": {
                        "primary": "#1a1a1a",
                        "secondary": "#6c5ce7",
                        "accent": "#00d2ff"
                    },
                    "spacing": "compact",
                    "margins": "narrow"
                }
            ),
            CVTemplate(
                id="modern-gradient",
                name="Modern Gradient",
                description="Eye-catching design with gradient elements",
                category="modern",
                is_premium=True,
                layout="single-column",
                styles={
                    "font_family": "Open Sans, sans-serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#2d3436",
                        "secondary": "#636e72",
                        "accent": "#a29bfe"
                    },
                    "spacing": "normal",
                    "margins": "standard"
                }
            )
        ])
        
        # Classic Templates
        templates.extend([
            CVTemplate(
                id="classic-traditional",
                name="Traditional",
                description="Timeless design for any industry",
                category="classic",
                is_premium=False,
                layout="single-column",
                styles={
                    "font_family": "Times New Roman, serif",
                    "font_size": "12pt",
                    "colors": {
                        "primary": "#000000",
                        "secondary": "#333333",
                        "accent": "#666666"
                    },
                    "spacing": "normal",
                    "margins": "standard"
                }
            ),
            CVTemplate(
                id="classic-elegant",
                name="Classic Elegant",
                description="Refined design with elegant typography",
                category="classic",
                is_premium=False,
                layout="single-column",
                styles={
                    "font_family": "Garamond, serif",
                    "font_size": "11pt",
                    "colors": {
                        "primary": "#2c3e50",
                        "secondary": "#7f8c8d",
                        "accent": "#8e44ad"
                    },
                    "spacing": "wide",
                    "margins": "wide"
                }
            )
        ])
        
        return templates