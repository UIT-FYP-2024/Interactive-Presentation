from django.shortcuts import render


def powerpoint_editor(request):

    # if we receive a get request
    return render(request=request, template_name="powerpoint_editor/ppt_editor.html", context={})
