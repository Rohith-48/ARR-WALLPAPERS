import os
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from .models import Category, Tag, UserProfileDoc, WallpaperCollection
from django.shortcuts import get_object_or_404, redirect

# from .models import Creatorauth

def index(request):
    wallpapers = WallpaperCollection.objects.select_related('user').prefetch_related('tags').all()
    return render(request, 'index.html', {'wallpapers': wallpapers})


def wallpaper_details(request, wallpaper_id):
    wallpaper = get_object_or_404(WallpaperCollection, pk=wallpaper_id)
    return render(request, 'wallpaper_details.html', {'wallpaper': wallpaper})



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


from .models import Category
def upload_wallpaper(request):
    if request.method == 'POST':
        title = request.POST['title']
        price = request.POST['price']
        description = request.POST['description']
        wallpaper_file = request.FILES['wallpaper_file']
        user = request.user
        category_name = request.POST['category']  # Get category name from the form
        tags_names = request.POST.getlist('tags')

        category, created = Category.objects.get_or_create(name=category_name)  # Get or create category
        tags = Tag.objects.filter(name__in=tags_names)

        wallpaper = WallpaperCollection.objects.create(
            title=title,
            price=price,
            description=description,
            user=user,
            category=category,
            wallpaper_image=wallpaper_file
        )
        wallpaper.tags.set(tags)

        return redirect('upload_wallpaper')
    else:
        categories = Category.CATEGORY_CHOICES
        tags = Tag.objects.all()
        upload_successful = True
        return render(request, 'upload_wallpaper.html', {'categories': categories, 'tags': tags, 'upload_successful': upload_successful})




def view_delete_wallpaper(request):
    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
        wallpaper.delete()
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
        selected_tags_str = request.POST['tags']  # Retrieve tags as a comma-separated string
        selected_tags = selected_tags_str.split(',')  # Split the string into a list of tags

        wallpaper = get_object_or_404(WallpaperCollection, id=selected_wallpaper_id)
        wallpaper.title = title
        wallpaper.description = description
        wallpaper.save()

        # Clear existing tags and add the new tags
        wallpaper.tags.clear()
        for tag_name in selected_tags:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            wallpaper.tags.add(tag)

        messages.success(request, 'Wallpaper updated successfully')
        return redirect('update_wallpaper')

    wallpapers = WallpaperCollection.objects.all()
    all_tags = Tag.objects.all()

    return render(request, 'update_wallpaper.html', {'wallpapers': wallpapers, 'all_tags': all_tags})




def user_upload(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        user = request.user
        category_name = request.POST.get("category")
        tags_input = request.POST.get("tags")  # Get tags as a comma-separated string

        # Split the tags string into a list
        tags_names = [tag.strip() for tag in tags_input.split(",")]

        category, created = Category.objects.get_or_create(name=category_name)
        tags = Tag.objects.filter(name__in=tags_names)

        wallpaper_image = request.FILES.get("wallpaper_file")
        wallpaper = WallpaperCollection.objects.create(
            title=title,
            description=description,
            price=price,
            user=user,
            category=category,
            wallpaper_image=wallpaper_image,
        )
        wallpaper.tags.set(tags)

        return redirect("user_upload")
    else:
        tags = Tag.objects.all()
        categories = Category.CATEGORY_CHOICES  # Assuming you have CATEGORY_CHOICES defined in your Category model

    context = {
        "tags": tags,
        "categories": categories,
    }
    return render(request, "user_upload.html", context)



def user_edit_wallpaper(request):
    if request.method == "POST":
        selected_wallpaper_id = request.POST.get("selected_wallpaper")
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags_input = request.POST.get("tags") 
        tags_list = [tag.strip() for tag in tags_input.split(",")] 
        user = request.user

        try:
            wallpaper = WallpaperCollection.objects.get(id=selected_wallpaper_id, user=user)

            wallpaper.title = title
            wallpaper.description = description
            wallpaper.save()
            tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_list]
            wallpaper.tags.set(tags)

            messages.success(request, "Wallpaper updated successfully")
        except WallpaperCollection.DoesNotExist:
            messages.error(request, "Wallpaper not found or you don't have permission to edit it")

        return redirect("user_edit")
    else:
        wallpapers = WallpaperCollection.objects.filter(user=request.user)
        all_tags = Tag.objects.all()

        context = {"wallpapers": wallpapers, "all_tags": all_tags}
        return render(request, "user_edit.html", context)



from django.contrib.auth.decorators import login_required
from .models import WallpaperCollection
@login_required
def view_delete_userwallpaper(request):
    user = request.user
    wallpapers = WallpaperCollection.objects.filter(user=user)

    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper_to_delete = WallpaperCollection.objects.get(id=wallpaper_id)
        if wallpaper_to_delete.user == user:
            wallpaper_to_delete.delete()
            return redirect('view_delete_userwallpaper')

    context = {
        'wallpapers': wallpapers,
    }
    return render(request, 'view_delete_userwallpaper.html', context)