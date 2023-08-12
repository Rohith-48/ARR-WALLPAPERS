from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        #portfolio= request.POST['portfolio']        
        user=User.objects.create_user(username=username, password=password,email=email)#portfolio=portfolio)
        user.save()
        messages.success(request, f"Account has been created. Welcome, {username}!")
        return redirect("login")

    else:
        return render(request, 'signup.html')


def login(request):
    return render(request, 'login.html')


def userprofile(request):
    return render(request, 'userprofile.html')

def forgot_password(request):
    # Handle form submission here (sending password reset email, etc.)
    # Implement your forgot password logic here if needed
    return render(request, 'forgot_password.html')

def Premium_signup(request):
    return render(request, 'Premium_signup.html')