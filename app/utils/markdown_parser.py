"""
Markdown parser utility for BTG app.
Provides functions to convert markdown text to HTML for display in the UI.
"""
import markdown
import bleach
from markupsafe import Markup

# List of allowed HTML tags for security
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 
    'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'hr',
    'br', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
]

# List of allowed HTML attributes for security
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'class', 'target'],
    'abbr': ['title'],
    'acronym': ['title'],
    '*': ['class', 'id'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class', 'style'],
}

def convert_markdown_to_html(text):
    """
    Convert markdown text to safe HTML.
    
    Args:
        text (str): The markdown text to convert
        
    Returns:
        Markup: MarkupSafe's Markup object containing safe HTML
    """
    if not text:
        return Markup("")
    
    # Convert markdown to HTML
    html = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists'
        ]
    )
    
    # Sanitize HTML to prevent XSS attacks
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    # Mark as safe for Jinja2 templates
    return Markup(clean_html)
