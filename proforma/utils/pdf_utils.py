from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from django.core.files.base import ContentFile

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return ContentFile(result.getvalue())
    return None
