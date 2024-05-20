from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.
@login_required
def index(request):
    return render(request, 'dashboard/landing_home.html')


@login_required
def recent_documents(request):
    return render(request, 'recent_documents/documents.html')


@login_required
def tutorials(request):
    return render(request, 'tutorials/tutorials.html')
