from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from weasyprint import HTML, CSS
from jinja2 import Template
from typing import Dict, Any, List
import io
import json
from models.cv import CVData, CVSection

class ExportService:
    """Service for exporting CVs to various formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    async def export_to_pdf(self, cv_data: CVData, template_styles: Dict[str, Any] = None) -> bytes:
        """Export CV to PDF using ReportLab"""
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        )
        story.append(Paragraph(cv_data.title, title_style))
        
        # Add sections
        for section in sorted(cv_data.sections, key=lambda x: x.order):
            if section.is_visible:
                story.extend(self._build_pdf_section(section))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    async def export_to_html(self, cv_data: CVData, template_styles: Dict[str, Any] = None) -> str:
        """Export CV to HTML with CSS styling"""
        
        # HTML template
        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { 
            font-family: {{ font_family|default('Arial, sans-serif') }}; 
            line-height: 1.6; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            color: {{ text_color|default('#333') }};
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 2px solid {{ accent_color|default('#3498db') }};
            padding-bottom: 20px;
        }
        .section { 
            margin-bottom: 25px; 
        }
        .section-title { 
            color: {{ accent_color|default('#3498db') }}; 
            font-size: 18px; 
            font-weight: bold; 
            margin-bottom: 10px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        .contact-info { 
            margin: 10px 0; 
        }
        .experience-item, .education-item { 
            margin-bottom: 15px; 
        }
        .item-title { 
            font-weight: bold; 
            color: {{ secondary_color|default('#2c3e50') }};
        }
        .item-company { 
            color: #666; 
            font-style: italic; 
        }
        .item-date { 
            color: #888; 
            font-size: 14px; 
        }
        .skills-list { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
        }
        .skill-item { 
            background: {{ accent_color|default('#3498db') }}20; 
            padding: 5px 10px; 
            border-radius: 15px; 
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
    </div>
    
    {% for section in sections %}
        {% if section.is_visible %}
            <div class="section">
                <h2 class="section-title">{{ section.title }}</h2>
                {{ render_section_content(section) }}
            </div>
        {% endif %}
    {% endfor %}
</body>
</html>
        """)
        
        # Render template
        return html_template.render(
            title=cv_data.title,
            sections=cv_data.sections,
            render_section_content=self._render_html_section_content,
            **template_styles or {}
        )
    
    async def export_to_word_html(self, cv_data: CVData, template_styles: Dict[str, Any] = None) -> str:
        """Export CV to Word-compatible HTML format"""
        
        word_template = Template("""
<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office" 
      xmlns:w="urn:schemas-microsoft-com:office:word" 
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <!--[if gte mso 9]>
    <xml>
        <w:WordDocument>
            <w:View>Print</w:View>
            <w:Zoom>90</w:Zoom>
        </w:WordDocument>
    </xml>
    <![endif]-->
    <style>
        body { font-family: 'Times New Roman', serif; font-size: 11pt; }
        h1 { font-size: 16pt; font-weight: bold; }
        h2 { font-size: 14pt; font-weight: bold; color: #1f4e79; }
        .section { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    {% for section in sections %}
        {% if section.is_visible %}
            <div class="section">
                <h2>{{ section.title }}</h2>
                {{ render_section_content(section) }}
            </div>
        {% endif %}
    {% endfor %}
</body>
</html>
        """)
        
        return word_template.render(
            title=cv_data.title,
            sections=cv_data.sections,
            render_section_content=self._render_word_section_content
        )
    
    def _build_pdf_section(self, section: CVSection) -> List:
        """Build PDF content for a section"""
        content = []
        
        # Section title
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#3498db')
        )
        content.append(Paragraph(section.title, section_style))
        
        # Section content based on type
        if section.type == 'personal_info':
            content.extend(self._build_personal_info_pdf(section.content))
        elif section.type == 'experience':
            content.extend(self._build_experience_pdf(section.content))
        elif section.type == 'education':
            content.extend(self._build_education_pdf(section.content))
        elif section.type == 'skills':
            content.extend(self._build_skills_pdf(section.content))
        else:
            # Generic content
            content.append(Paragraph(str(section.content.get('text', '')), self.styles['Normal']))
        
        content.append(Spacer(1, 12))
        return content
    
    def _build_personal_info_pdf(self, content: Dict[str, Any]) -> List:
        """Build personal info section for PDF"""
        items = []
        
        info_items = [
            content.get('full_name', ''),
            content.get('email', ''),
            content.get('phone', ''),
            content.get('location', ''),
            content.get('linkedin', ''),
            content.get('website', '')
        ]
        
        info_text = ' | '.join([item for item in info_items if item])
        items.append(Paragraph(info_text, self.styles['Normal']))
        
        if content.get('summary'):
            items.append(Spacer(1, 6))
            items.append(Paragraph(content['summary'], self.styles['Normal']))
        
        return items
    
    def _build_experience_pdf(self, content: Dict[str, Any]) -> List:
        """Build experience section for PDF"""
        items = []
        
        for exp in content.get('experiences', []):
            # Job title and company
            title_text = f"<b>{exp.get('title', '')}</b> at {exp.get('company', '')}"
            items.append(Paragraph(title_text, self.styles['Normal']))
            
            # Date range
            date_range = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            items.append(Paragraph(f"<i>{date_range}</i>", self.styles['Normal']))
            
            # Description
            if exp.get('description'):
                items.append(Paragraph(exp['description'], self.styles['Normal']))
            
            items.append(Spacer(1, 6))
        
        return items
    
    def _build_education_pdf(self, content: Dict[str, Any]) -> List:
        """Build education section for PDF"""
        items = []
        
        for edu in content.get('education', []):
            title_text = f"<b>{edu.get('degree', '')}</b> - {edu.get('institution', '')}"
            items.append(Paragraph(title_text, self.styles['Normal']))
            
            date_text = f"{edu.get('start_date', '')} - {edu.get('end_date', '')}"
            items.append(Paragraph(f"<i>{date_text}</i>", self.styles['Normal']))
            
            if edu.get('description'):
                items.append(Paragraph(edu['description'], self.styles['Normal']))
                
            items.append(Spacer(1, 6))
        
        return items
    
    def _build_skills_pdf(self, content: Dict[str, Any]) -> List:
        """Build skills section for PDF"""
        items = []
        
        skills_text = ', '.join(content.get('skills', []))
        items.append(Paragraph(skills_text, self.styles['Normal']))
        
        return items
    
    def _render_html_section_content(self, section: CVSection) -> str:
        """Render section content for HTML export"""
        if section.type == 'personal_info':
            return self._render_personal_info_html(section.content)
        elif section.type == 'experience':
            return self._render_experience_html(section.content)
        elif section.type == 'education':
            return self._render_education_html(section.content)
        elif section.type == 'skills':
            return self._render_skills_html(section.content)
        else:
            return f"<p>{section.content.get('text', '')}</p>"
    
    def _render_personal_info_html(self, content: Dict[str, Any]) -> str:
        """Render personal info for HTML"""
        html = ""
        
        contact_items = []
        for key, value in content.items():
            if value and key != 'summary':
                contact_items.append(f"<span>{value}</span>")
        
        if contact_items:
            html += f'<div class="contact-info">{", ".join(contact_items)}</div>'
        
        if content.get('summary'):
            html += f'<p>{content["summary"]}</p>'
        
        return html
    
    def _render_experience_html(self, content: Dict[str, Any]) -> str:
        """Render experience for HTML"""
        html = ""
        
        for exp in content.get('experiences', []):
            html += '<div class="experience-item">'
            html += f'<div class="item-title">{exp.get("title", "")}</div>'
            html += f'<div class="item-company">{exp.get("company", "")}</div>'
            html += f'<div class="item-date">{exp.get("start_date", "")} - {exp.get("end_date", "Present")}</div>'
            if exp.get('description'):
                html += f'<p>{exp["description"]}</p>'
            html += '</div>'
        
        return html
    
    def _render_education_html(self, content: Dict[str, Any]) -> str:
        """Render education for HTML"""
        html = ""
        
        for edu in content.get('education', []):
            html += '<div class="education-item">'
            html += f'<div class="item-title">{edu.get("degree", "")}</div>'
            html += f'<div class="item-company">{edu.get("institution", "")}</div>'
            html += f'<div class="item-date">{edu.get("start_date", "")} - {edu.get("end_date", "")}</div>'
            if edu.get('description'):
                html += f'<p>{edu["description"]}</p>'
            html += '</div>'
        
        return html
    
    def _render_skills_html(self, content: Dict[str, Any]) -> str:
        """Render skills for HTML"""
        skills = content.get('skills', [])
        if skills:
            skill_items = [f'<span class="skill-item">{skill}</span>' for skill in skills]
            return f'<div class="skills-list">{"".join(skill_items)}</div>'
        return ""
    
    def _render_word_section_content(self, section: CVSection) -> str:
        """Render section content for Word export"""
        # Similar to HTML but with Word-compatible styling
        return self._render_html_section_content(section)