import os
import razorpay
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from .models import Category, Tag, UserProfileDoc, WallpaperCollection
from django.shortcuts import get_object_or_404, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required  # Import this decorator
from .models import UserProfileDoc


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        uploaded_files = request.FILES.getlist('portfolio')

        try:
            if password1 != password2:
                raise ValidationError('Passwords do not match')

            validate_email(email) 

            if User.objects.filter(username=username).exists():
                raise ValidationError('Username Taken')

            if User.objects.filter(email=email).exists():
                raise ValidationError('Email already exists')

            user = User.objects.create_user(username=username, password=password1, email=email)
            user_profile = UserProfileDoc(user=user, is_approved=False, is_creator=True) 
            user_profile.save()

            for uploaded_file in uploaded_files:
                if not uploaded_file.name.endswith('.pdf'):
                    raise ValidationError('Invalid file format. Please upload a PDF file.')

                unique_filename = str(uuid.uuid4()) + '.pdf'
                user_profile.portfolio.save(unique_filename, uploaded_file)

            messages.success(request, 'Your Account has been Created as a Creator')
            return redirect('login')
        
        except ValidationError as e:
            messages.error(request, str(e))
            messages.error(request, 'Cannot Register')
            return redirect('signup')

    return render(request, "signup.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfileDoc

def Premium_signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        try:
            if password1 != password2:
                raise ValidationError('Passwords do not match')
            validate_email(email) 
            if User.objects.filter(username=username).exists():
                raise ValidationError('Username Taken')

            if User.objects.filter(email=email).exists():
                raise ValidationError('Email already exists')

            user = User.objects.create_user(username=username, password=password1, email=email)
            user_profile = UserProfileDoc(user=user, is_approved=True, is_premium=True) 
            user_profile.save()

            messages.success(request, 'Your Premium Account has been Created')
            return redirect('login')

        except ValidationError as e:
            messages.error(request, str(e))
            messages.error(request, 'Cannot Register')
            return redirect('PremiumUserPage/Premium_signup')

    return render(request, "PremiumUserPage/Premium_signup.html")


def index(request):
    query = request.GET.get('q')
    wallpapers = WallpaperCollection.objects.select_related('user').prefetch_related('tags').order_by('id')
    if query:
        wallpapers = wallpapers.filter(title__icontains=query)
    return render(request, 'index.html', {'wallpapers': wallpapers, 'query': query})



def subscribe_page(request):
    return render(request, 'subscribe_page.html')


def wallpaper_details(request, wallpaper_id):
    wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
    wallpaper.view_count += 1
    wallpaper.save()
    return render(request, 'wallpaper_details.html', {'wallpaper': wallpaper})



from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .models import UserProfileDoc

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
                    if user.userprofiledoc.is_premium:
                        return redirect('index')
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


from django.contrib.auth import logout as django_logout
def custom_logout(request):
    django_logout(request)
    return redirect('index')  


from django.contrib.auth.decorators import login_required
@login_required
def user_profile(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        user_profile.about_me = request.POST.get('about_me')
        uploaded_avatar = request.FILES.get('avatar')
        if uploaded_avatar:
            user_profile.avatar = uploaded_avatar

        user_profile.save()
        return redirect('userprofile')

    return render(request, 'userprofile.html', {'user_profile': user_profile, 'user': user})


def forgot_password(request):
    return render(request, 'forgot_password.html')


@login_required
def premiumuserpage(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('premiumuserpage')
    return render(request, 'PremiumUserPage/premiumuserpage.html', {'user': user})


from django.conf import settings
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpRequest
def paymentform(request: HttpRequest):
    currency = 'INR'
    amount = int(request.GET.get("amount")) * 100# Rs. 200
 
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount/100
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'paymentform.html', context=context)
 

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000 
                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    return render(request, 'paymentsuccess.html')
                except:
                    return render(request, 'paymentfail.html')
            else:
                return render(request, 'paymentfail.html')
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()



from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import WallpaperCollection, Category, Tag
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico', 'jfif', 'pjpeg', 'pjp', 'avif']

def upload_wallpaper(request):
    if request.method == 'POST':
        title = request.POST['title']
        price = request.POST['price']
        description = request.POST['description']
        wallpaper_file = request.FILES['wallpaper_file']
        user = request.user
        category_name = request.POST['category']
        tags_input = request.POST.get("tags")

        tags_names = [tag.strip() for tag in tags_input.split(",")]
        new_tags = []
        for tag_name in tags_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            new_tags.append(tag)
        category, created = Category.objects.get_or_create(name=category_name)
        extension = wallpaper_file.name.split('.')[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationError('File must be an image with a valid extension (jpg, jpeg, png, gif, bmp, tiff, webp, svg, ico, jfif, pjpeg, pjp, avif).')

        wallpaper = WallpaperCollection.objects.create(
            title=title,
            price=price,
            description=description,
            user=user,
            category=category,
            wallpaper_image=wallpaper_file
        )
        wallpaper.tags.set(new_tags)
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




from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .models import WallpaperCollection, Category, Tag, UserProfileDoc
from django.http import HttpResponseBadRequest

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico', 'jfif', 'pjpeg', 'pjp', 'avif']

@login_required
def user_upload(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    categories = Category.CATEGORY_CHOICES  # Define categories outside the if-else block
    
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        user = request.user
        category_name = request.POST.get("category")
        tags_input = request.POST.get("tags")
        tags_names = [tag.strip() for tag in tags_input.split(",")]
        category, created = Category.objects.get_or_create(name=category_name)
        tags = Tag.objects.filter(name__in=tags_names)
        wallpaper_image = request.FILES.get("wallpaper_file")
        extension = wallpaper_image.name.split('.')[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return HttpResponseBadRequest("File must be an image with a valid extension (jpg, jpeg, png, gif, bmp, tiff, webp, svg, ico, jfif, pjpeg, pjp, avif).")
        wallpaper = WallpaperCollection.objects.create(
            title=title,
            description=description,
            price=price,
            user=user,
            category=category,
            wallpaper_image=wallpaper_image,
        )
        wallpaper.tags.set(tags)

        if 'avatar' in request.FILES:
            avatar_image = request.FILES['avatar']
            user_profile.avatar = avatar_image
            user_profile.save()

    else:
        tags = Tag.objects.all()

    context = {
        "tags": tags,
        "categories": categories,
        "user_profile": user_profile,
    }

    return render(request, "user_upload.html", context)



@login_required
def user_edit_wallpaper(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    if request.method == "POST":
        selected_wallpaper_id = request.POST.get("selected_wallpaper")
        title = request.POST.get("title")
        description = request.POST.get("description")
        tags_input = request.POST.get("tags")
        tags_list = [tag.strip() for tag in tags_input.split(",")]
        try:
            wallpaper = WallpaperCollection.objects.get(id=selected_wallpaper_id, user=request.user)
            wallpaper.title = title
            wallpaper.description = description
            wallpaper.save()
            tags = Tag.objects.filter(name__in=tags_list)
            wallpaper.tags.set(tags)

            messages.success(request, "Wallpaper updated successfully")
        except WallpaperCollection.DoesNotExist:
            messages.error(request, "Wallpaper not found or you don't have permission to edit it")
    else:
        wallpapers = WallpaperCollection.objects.filter(user=request.user)
        all_tags = Tag.objects.all()

    context = {
        "wallpapers": wallpapers,
        "all_tags": all_tags,
        "user_profile": user_profile,  
    }
    return render(request, "user_edit.html", context)


from django.contrib.auth.decorators import login_required
from .models import WallpaperCollection, UserProfileDoc
from django.shortcuts import render, redirect

@login_required
def view_delete_userwallpaper(request):
    user = request.user
    wallpapers = WallpaperCollection.objects.filter(user=user)
    try:
        user_profile = UserProfileDoc.objects.get(user=user)
        avatar = user_profile.avatar
    except UserProfileDoc.DoesNotExist:
        avatar = None  # Handle the case when the profile doesn't exist

    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper_to_delete = WallpaperCollection.objects.get(id=wallpaper_id)
        if wallpaper_to_delete.user == user:
            wallpaper_to_delete.delete()
            return redirect('view_delete_userwallpaper')

    context = {
        'wallpapers': wallpapers,
       "user_profile": user_profile,   # Include the avatar in the context
    }
    return render(request, 'view_delete_userwallpaper.html', context)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import WallpaperCollection

@csrf_exempt  # Use this decorator to disable CSRF protection for this view (for simplicity, consider enabling it in production)
def liked_wallpapers(request):
    # Get the liked wallpaper IDs from the cookie
    liked_wallpaper_ids = json.loads(request.COOKIES.get("likedWallpapers")) or []

    liked_wallpapers_data = []
    
    for wallpaper_id in liked_wallpaper_ids:
        try:
            wallpaper = WallpaperCollection.objects.get(id=wallpaper_id)
            liked_wallpapers_data.append({
                'title': wallpaper.title,
                'image_url': request.build_absolute_uri(wallpaper.wallpaper_image.url),  # Build absolute image URL
            })
        except ObjectDoesNotExist:
            pass
    context = {"one": liked_wallpapers}
    return render(request, 'liked_wallpapers.html',{'wallpapers':liked_wallpapers_data} )
