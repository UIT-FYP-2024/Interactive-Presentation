from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, FileResponse
from django.shortcuts import render

from .utils import *

logger = logging.getLogger(__name__)


def powerpoint_generator(request):
    """
    Render the PowerPoint generation interface.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Rendered PowerPoint generation interface page.
    """
    return render(request, 'powerpoint_generator/ppt_generator.html')


def generate_presentation(request):
    """
    Generate PowerPoint based on user inputs.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: JSON response containing the generated PowerPoint or an error message.
    """
    if request.method == 'POST':
        form_data = extract_form_data(request.POST)

        if not form_data:
            return HttpResponseBadRequest("All fields are required and 'No Of Slides' must be a number.")

        slides_content = generate_prompt(form_data)
        if not slides_content:
            return HttpResponseBadRequest("Failed to generate content for the presentation.")

        presentation_file = create_ppt(template_choice=form_data['template_choice'], slides_content=slides_content,
                                       presentation_title=form_data['topic_name'])

        if presentation_file:
            try:
                with open(presentation_file, 'rb') as ppt_file:
                    response = HttpResponse(ppt_file.read(),
                                            content_type='application/vnd.openxmlformats-officedocument'
                                                         '.presentationml.presentation')
                    response['Content-Disposition'] = f'attachment; filename="{form_data["topic_name"]}.pptx"'
                    return response
            except FileNotFoundError:
                logger.error(f"Presentation file not found: {presentation_file}")
                return HttpResponseBadRequest("Presentation file not found.")
        else:
            return HttpResponseBadRequest("Failed to create the presentation.")


def last_created_ppt(request):
    # Define the target directory where PPT files are located
    target_dir = os.path.join('static', 'stock', 'presentations')

    # Get a list of all PPT files in the target directory
    ppt_files = [file for file in os.listdir(target_dir) if file.endswith('.pptx')]

    # Check if there are any PPT files in the directory
    if not ppt_files:
        return HttpResponseBadRequest("No PPT files found in the target directory.")

    # Sort the PPT files by creation time (ascending order)
    ppt_files.sort(key=lambda x: os.path.getctime(os.path.join(target_dir, x)))

    # Get the path to the last created PPT file
    last_created_ppt_file = os.path.join(target_dir, ppt_files[-1])

    # Serve the file using FileResponse
    try:
        return FileResponse(open(last_created_ppt_file, 'rb'),
                            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    except Exception as e:
        return HttpResponseBadRequest(f"Error: {str(e)}")
