# hub/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    """
    Home general del sistema.
    Punto de entrada tras login.
    """
    return render(request, "hub/home.html")
