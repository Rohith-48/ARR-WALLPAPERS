import os
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from .models import Tag, UserProfileDoc, WallpaperCollection
from django.shortcuts import get_object_or_404, redirect

# from .models import Creatorauth

def index(request):
    wallpapers = WallpaperCollection.objects.select_related('user').all()
    return render(request, 'index.html', {'wallpapers': wallpapers})


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


def upload_wallpaper(request):
    if request.method == 'POST':
        title = request.POST['title']
        price = request.POST['price']
        description = request.POST['description']
        wallpaper_file = request.FILES['wallpaper_file']
        user = request.user
        # category_name = request.POST['category']
        tags_names = request.POST.getlist('tags')

        # category = Category.objects.get(name=category_name)
        tags = Tag.objects.filter(name__in=tags_names)

        wallpaper = WallpaperCollection.objects.create(
            title=title,
            price=price,
            description=description,
            user=user,
            # category=category,
            wallpaper_image=wallpaper_file
        )
        wallpaper.tags.set(tags)

        return redirect('upload_wallpaper')  # Replace 'index' with the appropriate URL name
    else:
        # categories = Category.objects.all()
        tags = Tag.objects.all()
        upload_successful = True
        return render(request, 'upload_wallpaper.html', {'tags': tags, 'upload_successful': upload_successful})
    


def view_delete_wallpaper(request):
    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
        wallpaper.delete()
        # Optionally, you can add a success message using messages framework
        return redirect('view_delete_wallpaper')
    
    # Retrieve the list of wallpapers
    wallpapers = WallpaperCollection.objects.all()
    context = {'wallpapers': wallpapers}
    return render(request, 'view_delete_wallpaper.html', context)




def update_wallpaper(request):
    if request.method == 'POST':
        selected_wallpaper_id = request.POST.get('selected_wallpaper')
        title = request.POST['title']
        description = request.POST['description']
        selected_tags = request.POST.getlist('tags') 

        wallpaper = get_object_or_404(WallpaperCollection, id=selected_wallpaper_id)
        wallpaper.title = title
        wallpaper.description = description
        wallpaper.save()
        tags = Tag.objects.filter(id__in=selected_tags)
        wallpaper.tags.set(tags)

        messages.success(request, 'Wallpaper updated successfully')
        return redirect('update_wallpaper')
    wallpapers = WallpaperCollection.objects.all()
    all_tags = Tag.objects.all()
    return render(request, 'update_wallpaper.html', {'wallpapers': wallpapers, 'all_tags': all_tags})