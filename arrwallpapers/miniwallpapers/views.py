import os
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from .models import Creatorauth
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if Creatorauth.objects.filter(username=username).exists():
            messages.info(request, "Username already exists.")
            return redirect('signup')
        elif Creatorauth.objects.filter(email=email).exists():
            messages.info(request, "Email already exists.")
            return redirect('signup')
        else:
            # Create a new user with hashed password
            hashed_password = make_password(password)
            user = Creatorauth(username=username, email=email, password=hashed_password)
            user.save()

            uploaded_file = request.FILES.getlist('uploaded_file')
            if uploaded_file:
                for file in uploaded_file:
                    # Generate a unique filename using a UUID
                    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
                    user.portfolio.save(unique_filename, file)

            user.save()
            success_message = "Registration successful. You can now log in."
            messages.success(request, success_message)
            return redirect('login')
    else:
        return render(request, "signup.html")


# def login(request):
#     if request.method == "POST":
#         email = request.POST['email']
#         password = request.POST['password']

#         user = authenticate(request, email=email, password=password)

#         if user is not None and user.is_active and user.is_approved:
#             login(request, user)
#             return redirect('userprofile')  # Redirect to the user's dashboard
#         elif user is not None and not user.is_approved:
#             messages.info(request, "Your account has not been approved yet.")
#         else:
#             messages.error(request, "Invalid login credentials.")

#     return render(request, "login.html")
def login_user(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = Creatorauth.objects.get(email=email)
        except Creatorauth.DoesNotExist:
            user = None

        if user is not None:
            print(f"User with email {email} found.")
            authenticated_user = authenticate(email=email, password=password)

            if authenticated_user is not None:
                print("User authenticated successfully.")
                login(request, authenticated_user)
                return redirect('userprofile')
            else:
                print("Authentication failed.")
                messages.error(request, "Invalid email or password.")
                return redirect('login')
        else:
            print(f"User with email {email} not found.")
            messages.error(request, "Invalid email or password.")
            return redirect('login')
    else:
        return render(request, 'login.html')





def userprofile(request):
    return render(request, 'userprofile.html')

def forgot_password(request):
    # Handle form submission here (sending password reset email, etc.)
    # Implement your forgot password logic here if needed
    return render(request, 'forgot_password.html')

def Premium_signup(request):
    return render(request, 'Premium_signup.html')