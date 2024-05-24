from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .utils import create_ppt, generate_content


def generate_presentation(request):
    if request.method == 'POST':
        # Extract form data
        topic_name = request.POST.get('topic_name', '').strip()
        no_of_slides = request.POST.get('no_of_slides', '').strip()
        user_role = request.POST.get('user_role', '').strip()
        tone = request.POST.get('tone', '').strip()
        target_audience = request.POST.get('target_audience', '').strip()
        prompt = request.POST.get('prompt', '').strip()
        template_choice = request.POST.get('template_choice', '').strip()
        suggest_pictures = request.POST.get('suggest_pictures', 'off') == 'on'

        # Basic validation
        if not (topic_name and no_of_slides.isdigit() and user_role and tone and target_audience and prompt):
            return HttpResponseBadRequest("All fields are required and 'No Of Slides' must be a number.")

        payload = (
            f"Create Presentation on {topic_name}, Think as {user_role}, My target Audience is {target_audience}, "
            f"Include Details About {prompt}, content should be in {tone} tone. Structure of response should be json "
            f"split in {no_of_slides} Slides, Example {{Slide 1: ' ', Slide 2: ' '}}."
        )

        if suggest_pictures:
            payload += " Also suggest some pictures."

        # Generate slides content based on form data
        slides_content = generate_content(payload)

        if not slides_content:
            return HttpResponseBadRequest("Failed to generate content for the presentation.")

        # Create PowerPoint presentation
        presentation_file = create_ppt(slides_content, template_choice=template_choice, presentation_title=topic_name)

        if not presentation_file:
            return HttpResponseBadRequest("Failed to create the presentation.")

        # Respond with the presentation file for download
        response = HttpResponse(presentation_file, content_type='application/vnd.openxmlformats-officedocument'
                                                                '.presentationml.presentation')
        response['Content-Disposition'] = f'attachment; filename="{topic_name}.pptx"'
        return response

    return render(request, 'powerpoint_generator/ppt_generator.html')
