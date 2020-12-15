import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.db import IntegrityError
from django.http import JsonResponse
from django import forms

from .models import User, Fencer
# Create your views here.

class SearchForm(forms.Form):
    search = forms.CharField(label="Search")

def index(request):
    if request.user.is_authenticated:
        return render(request, "UI/dashboard.html")
    else:
        return HttpResponseRedirect(reverse("login"))


def fencers(request):

    # Query for requested email
    try:
        fencers = Fencer.objects.all()
    except Fencer.DoesNotExist:
        return JsonResponse({"error": "Fencer not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return render(request, "UI/fencer.html", {
            'fencers': fencers
        })

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET request required."
        }, status=400)


def get_search(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            search = form.cleaned_data['search']
            results = []
            for fencer in Fencer.objects.all():
                if search.upper() in fencer.last_name.upper() or search.upper() in fencer.first_name.upper():
                    results.append(fencer)
            return render(request, 'UI/search_results.html', {'fencers': results})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'UI/fencer.html', {'form': form, 'fencers': Fencer.objects.all()})



# login stuff

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "UI/login/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "UI/login/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "UI/login/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "UI/login/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "UI/login/register.html")
