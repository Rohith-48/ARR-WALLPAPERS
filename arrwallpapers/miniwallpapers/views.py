from django.shortcuts import render, redirect
from .models import Creatorauth
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        if Creatorauth.objects.filter(username=username).exists():
            messages.info(request,"Username Already Exists")
            return redirect('register')
        elif Creatorauth.objects.filter(email=email).exists():
            messages.info(request,"Email Already Exists") 
            return redirect('register')
        else:
            user=Creatorauth.objects.create(username=username,email=email,password=password)
            user.save()
            success_message = "Registration successful. You can now log in."
            messages.success(request, success_message)
            return redirect('login')
           
    else:
        return render (request, "signup.html")

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