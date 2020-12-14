import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.db import IntegrityError
from django.http import JsonResponse

from .models import User, Fencer
# Create your views here.

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

    # # Update whether email is read or should be archived
    # elif request.method == "PUT":
    #     data = json.loads(request.body)
    #     if data.get("read") is not None:
    #         email.read = data["read"]
    #     if data.get("archived") is not None:
    #         email.archived = data["archived"]
    #     email.save()
    #     return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

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
