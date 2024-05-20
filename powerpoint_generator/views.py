from django.shortcuts import render


def powerpoint_generator(request):

    # if we receive a get request
    return render(request=request, template_name="powerpoint_generator/ppt_generator.html", context={})
