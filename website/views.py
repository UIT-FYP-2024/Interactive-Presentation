from django.shortcuts import render


# Create your views here.
def website(request):
    return render(request, template_name="website/index.html", context={})
