import logging
import os
from django.conf import settings
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt
import google.generativeai as genai

logger = logging.getLogger(__name__)


def generate_content(payload):
    try:
        genai.configure(api_key=settings.API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(payload)
        return response.text
    except Exception as e:
        logger.error(f"Error generating text with genie: {e}")
        return 'Failed to generate text'


def create_ppt(slides_content, template_choice, presentation_title):
    if not template_choice:
        template_choice = "dark_modern"

    template_path = os.path.join('stock', 'templates', f"{template_choice}.pptx")
    if not os.path.exists(template_path):
        logger.error(f"Template file {template_path} not found.")
        return None

    try:
        prs = Presentation(template_path)
    except Exception as e:
        logger.error(f"Error opening presentation template: {e}")
        return None

    title_slide_layout = prs.slide_layouts[0]
    content_slide_layout = prs.slide_layouts[1]

    # Add title slide
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    title.text = presentation_title

    if template_choice == 'dark_modern':
        for paragraph in title.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Times New Roman'
                run.font.color.rgb = RGBColor(255, 165, 0)  # RGB for orange color

    elif template_choice == 'bright_modern':
        for paragraph in title.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = 'Arial'
                run.font.color.rgb = RGBColor(255, 20, 147)  # RGB for deep pink color

    # Add content slides
    for slide_index, slide_content in enumerate(slides_content):
        slide = prs.slides.add_slide(content_slide_layout)

        title_placeholder = slide.placeholders[0]  # Title
        content_placeholder = slide.placeholders[1]  # Content

        title_placeholder.text = slide_content.get('title', '')
        content_placeholder.text = slide_content.get('content', '')

        if template_choice == 'dark_modern':
            for paragraph in title_placeholder.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(45)
                    run.font.color.rgb = RGBColor(255, 165, 0)  # RGB for orange color
            for paragraph in content_placeholder.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(35)
                    run.font.color.rgb = RGBColor(255, 255, 255)  # RGB for white color

    # Ensure output directory exists
    output_dir = os.path.join('stock', 'presentations', "generated_presentation.pptx")

    os.makedirs(output_dir, exist_ok=True)

    output_path = "stock/presentations/generated_presentation.pptx"
    prs.save(output_path)
    return output_path
