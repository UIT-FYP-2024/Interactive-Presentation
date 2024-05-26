import json
import logging
import os
from urllib.parse import quote_plus
import google.generativeai as genai
import requests
from django.conf import settings
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

logger = logging.getLogger(__name__)


def get_font_colors(template_choice):
    """
    Get font colors based on the selected template.

    Args:
        template_choice (str): The chosen template ("dark_modern" or "bright_modern").

    Returns:
        Tuple[RGBColor, RGBColor]: Tuple containing (title_font_color, content_font_color).
    """
    if template_choice == 'dark_modern':
        return RGBColor(255, 255, 255), RGBColor(255, 255, 255)  # White
    elif template_choice == 'bright_modern':
        return RGBColor(0, 0, 0), RGBColor(0, 0, 0)  # Black
    else:
        return RGBColor(0, 0, 0), RGBColor(0, 0, 0)  # Black, Black


def apply_formatting(paragraphs, font_name, font_color, font_size):
    """
    Apply formatting to paragraphs.

    Args:
        paragraphs (Iterable): Iterable containing paragraph objects.
        font_name (str): Name of the font.
        font_color (RGBColor): Color of the font.
        font_size (Pt): Font size.
    """
    for paragraph in paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = font_size
            run.font.color.rgb = font_color


def extract_form_data(post_data):
    """
    Extract form data from POST request.

    Args:
        post_data (dict): Dictionary containing POST data.

    Returns:
        dict: Extracted form data.
    """
    required_fields = ['topic_name', 'no_of_slides', 'user_role', 'tone', 'target_audience', 'prompt',
                       'template_choice']
    for field in required_fields:
        value = post_data.get(field, '').strip()
        if not value:
            return None
        elif field == 'no_of_slides' and not value.isdigit():
            return None
    return {
        'topic_name': post_data['topic_name'],
        'no_of_slides': int(post_data['no_of_slides']),
        'user_role': post_data['user_role'],
        'tone': post_data['tone'],
        'target_audience': post_data['target_audience'],
        'prompt': post_data['prompt'],
        'template_choice': post_data['template_choice'],
    }


def generate_prompt(form_data):
    """
    Generate text prompt based on form data.

    Args:
        form_data (dict): Dictionary containing form data.

    Returns:
        str: Generated text prompt.
    """
    payload = (
        f"Create a presentation on the topic '{form_data['topic_name']}'. You are acting as a '{form_data['user_role']}'"
        f"targeting an audience interested in '{form_data['target_audience']}'. The presentation should convey the "
        f"following information: '{form_data['prompt']}' and maintain a '{form_data['tone']}' tone throughout. The "
        f"presentation should be divided into {form_data['no_of_slides']} slides, dont use * anywhere. Response "
        f"should be in JSON format as mentioned"
    )

    # Generate the JSON string for the slides content
    slides_content_json = json.dumps({
        "Slide 1": {
            "title": " ",
            "content": " ",
            "promptImage": " "
        },
        "Slide 2": {
            "title": " ",
            "content": " ",
            "promptImage": " "
        },
        # Add more slides as needed
    }, indent=4)  # Indent for better readability

    # Append the JSON string to the payload
    payload += slides_content_json

    return generate_content(payload)


def generate_content(payload):
    """
    Generate content based on the provided payload.

    Args:
        payload (str): Payload for content generation.

    Returns:
        str: Generated content.
    """
    try:
        genai.configure(api_key=settings.API_KEY_GEMINI)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(payload)
        return response.text
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return 'Failed to generate content'


def search_images_pexels(prompt):
    """
    Search images from Pexels API based on the provided prompt.

    Args:
        prompt (str): Search prompt.

    Returns:
        tuple: Tuple containing image URL and source URL.
    """
    query = quote_plus(prompt.lower())
    PEXELS_API_URL = f"https://api.pexels.com/v1/search?{query}&per_page=1"
    headers = {'Authorization': settings.PEXELS_API_KEY}
    response = requests.get(PEXELS_API_URL, headers=headers)
    data = response.json()
    if 'photos' in data and data['photos']:
        return data['photos'][0]['src']['medium'], data['photos'][0]['url']
    return None


def create_ppt(template_choice, slides_content, presentation_title):
    """
    Create a PowerPoint presentation.

    Args:
        template_choice (str): Template choice.
        slides_content (str): JSON string containing slides content.
        presentation_title (str): Title of the presentation.

    Returns:
        str: Path to the created presentation file.
    """
    template_choice = template_choice or "dark_modern"
    template_path = os.path.join('static', 'stock', 'templates', f"{template_choice}.pptx")
    if not os.path.exists(template_path):
        logger.error(f"Template file {template_path} not found.")
        return None

    try:
        prs = Presentation(template_path)
        title_font_color, content_font_color = get_font_colors(template_choice)

        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # Title slide
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        title.text = presentation_title
        apply_formatting(title.text_frame.paragraphs, font_name='Times New Roman', font_color=title_font_color,
                         font_size=Pt(45))

        # Validate and parse the JSON content
        try:
            slides_content_dict = json.loads(slides_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
            return None

        # Iterate over the slides content dictionary
        for slide_number, slide_content in slides_content_dict.items():
            slide = prs.slides.add_slide(content_slide_layout)
            title_placeholder = slide.placeholders[0]
            content_placeholder = slide.placeholders[1]

            # Set the title and content in the slide placeholders
            title_placeholder.text = slide_content['title']
            content_placeholder.text = slide_content['content']

            apply_formatting(title_placeholder.text_frame.paragraphs, font_name='Times New Roman',
                             font_color=title_font_color, font_size=Pt(24))
            apply_formatting(content_placeholder.text_frame.paragraphs, font_name='Times New Roman',
                             font_color=content_font_color, font_size=Pt(18))

        output_dir = os.path.join('static', 'stock', 'presentations')
        os.makedirs(output_dir, exist_ok=True)

        # Construct the output file path with the actual presentation title
        sanitized_title = "".join(c for c in presentation_title if c.isalnum() or c in [' ', '_', '-'])
        output_path = os.path.join(output_dir, f"{sanitized_title}.pptx")
        prs.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error creating presentation: {e}")
        return None
