import os
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from .models import UserProfileDoc
from django.shortcuts import get_object_or_404, redirect

# from .models import Creatorauth

def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        uploaded_files = request.FILES.getlist('portfolio')  # Get the uploaded files

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')

            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')

            else:
                user = User.objects.create_user(username=username, password=password1, email=email)
                user_profile = UserProfileDoc(user=user, is_approved=False)  # Set is_approved to False
                user_profile.save()

                for uploaded_file in uploaded_files:
                    unique_filename = str(uuid.uuid4()) + os.path.splitext(uploaded_file.name)[1]
                    user_profile.portfolio.save(unique_filename, uploaded_file)
                
                messages.info(request, 'Your Account has been Created... Wait for Admins Approval')
                return redirect('login')

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    return render(request, "signup.html")
    

def approve_user(request, user_id):
    if request.user.is_superuser:
        user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
        user_profile.is_approved = True
        user_profile.save()
        return redirect('admin_dashboard')
    else:
        return redirect('login')

def delete_user(request, user_id):
    user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
    user_profile.user.delete()
    return redirect('admin_dashboard')  


def admin_dashboard(request):
    if request.user.is_superuser:
        users = User.objects.all()
        user_profiles = UserProfileDoc.objects.select_related('user').all()
        context = {
            'users': users,
            'user_profiles': user_profiles,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        return redirect('login')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.is_superuser or (hasattr(user, 'userprofiledoc') and user.userprofiledoc.is_approved):
                auth.login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                else:
                    return redirect('userprofile')
            else:
                messages.info(request, 'Your account is not approved yet. Please wait for admin approval.')
                return redirect('login')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return redirect("index")

def userprofile(request): 
    return render(request, 'userprofile.html')

def forgot_password(request):
    # Handle form submission here (sending password reset email, etc.)
    # Implement your forgot password logic here if needed
    return render(request, 'forgot_password.html')

def Premium_signup(request):
    return render(request, 'Premium_signup.html')






#for using Model use this code:
# def signup(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']

#         if Creatorauth.objects.filter(username=username).exists():
#             messages.info(request, "Username already exists.")
#             return redirect('signup')
#         elif Creatorauth.objects.filter(email=email).exists():
#             messages.info(request, "Email already exists.")
#             return redirect('signup')
#         else:
#             user = Creatorauth(username=username, email=email, password=password)
#             user.save()

#             # PDF file upload
#             uploaded_files = request.FILES.getlist('uploaded_file')
#             for file in uploaded_files:
#                 unique_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
#                 user.portfolio.save(unique_filename, file)

#             success_message = "Registration and file upload successful. You can now log in."
#             messages.success(request, success_message)
#             return redirect('login')
#     else:
#         return render(request, "signup.html")

# def login_user(request):
#     if request.method == "POST":
#         email = request.POST['email']
#         password = request.POST['password']

#         user = authenticate(email=email, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, "Login successful.")
#             return redirect('index')  # Replace 'index' with the URL to your desired page after login
#         else:
#             messages.error(request, "Invalid email or password.")
#             return redirect('login')  # Replace 'login' with the URL to your login page
#     else:
#         return render(request, "login.html")


# def signup(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         if Creatorauth.objects.filter(username=username).exists():
#             messages.info(request, "Username already exists.")
#             return redirect('signup')
#         elif Creatorauth.objects.filter(email=email).exists():
#             messages.info(request, "Email already exists.")
#             return redirect('signup')
#         else:
#             # Create a new user with hashed password
#             # hashed_password = make_password(password)
#             # user = Creatorauth(username=username, email=email, password=hashed_password)
#             user = Creatorauth(username=username, email=email, password=password)
#             user.save()
#             uploaded_file = request.FILES.getlist('uploaded_file')
#             if uploaded_file:
#                 for file in uploaded_file:
#                     unique_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
#                     user.portfolio.save(unique_filename, file)
#             user.save()
#             success_message = "Registration successful. You can now log in."
#             messages.success(request, success_message)
#             return redirect('login')
#     else:
#         return render(request, "signup.html")


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




