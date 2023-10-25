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
from django.contrib.auth.decorators import login_required  
from .models import UserProfileDoc


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phoneno = request.POST['phoneno'] 
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
            user_profile = UserProfileDoc(user=user, is_approved=False, is_creator=True, phoneno=phoneno)
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
from django.core.validators import validate_email 
from .models import UserProfileDoc
from allauth.socialaccount.models import SocialAccount 

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
                raise ValidationError('Username is already taken. Please choose a different username.')

            if User.objects.filter(email=email).exists():
                raise ValidationError('Email is already registered. Please use a different email.')

            user = User.objects.create_user(username=username, password=password1, email=email)
            user_profile = UserProfileDoc(user=user, is_approved=True, is_premium=True)
            
            if SocialAccount.objects.filter(user=user, provider='google').exists():
                google_account = SocialAccount.objects.get(user=user, provider='google')
                google_account.extra_data['is_premium'] = True
                google_account.save()

            user_profile.save()
            request.session['is_premium'] = True
            messages.success(request, 'Your Premium Account has been Created')
            return redirect('login')
        except ValidationError as e:
            messages.error(request, str(e))
            messages.error(request, 'Cannot Register')
            return redirect('PremiumUserPage/Premium_signup')
    return render(request, "PremiumUserPage/Premium_signup.html")



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



def index(request):
    query = request.GET.get('q')
    wallpapers = WallpaperCollection.objects.select_related('user').prefetch_related('tags').order_by('-upload_date') 
    if query:
        wallpapers = wallpapers.filter(title__icontains=query)
    return render(request, 'index.html', {'wallpapers': wallpapers, 'query': query})



def subscribe_page(request):
    return render(request, 'subscribe_page.html')



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfileDoc, WallpaperCollection
from django.db.models import Sum
from django.core.paginator import Paginator

def profileview(request, username):
    user=User.objects.get(username=username)
    if user.is_staff:
        # Admin view
        user_profile = get_object_or_404(User, username=username)
        user_content = WallpaperCollection.objects.filter(user=user)
    else:
        user_profile = get_object_or_404(UserProfileDoc, user__username=username)
        user_content = WallpaperCollection.objects.filter(user=user_profile.user, is_superuser=False)

    superuser_content = WallpaperCollection.objects.filter(is_superuser=True)
    paginator = Paginator(user_content, 10)
    page = request.GET.get('page')
    wallpapers = paginator.get_page(page)
    total_view_count = user_content.aggregate(Sum('view_count'))['view_count__sum'] or 0
    total_downloads = user_content.aggregate(Sum('downloads'))['downloads__sum'] or 0

    context = {
        'user_profile': user_profile,
        'user_content': wallpapers,
        'superuser_content': superuser_content,
        'uploaded_wallpapers_count': user_content.count(),
        'uploaded_wallpapers': user_content,
        'total_view_count': total_view_count,
        'total_downloads': total_downloads,
        'userdetail': user,
    }

    return render(request, 'profileview.html', context)





def wallpaper_details(request, wallpaper_id):
    wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
    wallpaper.view_count += 1
    # wallpaper.downloads += 1
    wallpaper.save()
    return render(request, 'wallpaper_details.html', {'wallpaper': wallpaper})
    
    

from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfileDoc

@login_required
def approve_user(request, user_id):
    if request.user.is_superuser:
        user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
        user_profile.is_approved = True
        user_profile.save()
        subject = 'Account Approved'
        message = (
            f'Dear {user_profile.user.username},\n\n'
            'Your account on our platform has been approved and activated. You can now access all features and content.\n\n'
            'Thank you for joining us!\n\n'
            'Best Regards,\n'
            'ARR'
        )
        from_email = settings.DEFAULT_FROM_EMAIL 
        recipient_list = [user_profile.user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        
        return redirect('admin_dashboard')
    else:
        return redirect('login')



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User  
from .models import UserProfileDoc, WallpaperCollection
from django.core.mail import send_mail
from django.conf import settings

def delete_user(request, user_id):
    user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
    if not user_profile.is_approved:
        return redirect('admin_dashboard') 
    user_profile.is_approved = False
    user_profile.save()
    subject = 'Account Deactivation'
    message = (
        f'Dear {user_profile.user.username},\n\n'
        'Your account on our platform has been deactivated by the administrator. If you have any questions or need further assistance, please contact us.\n\n'
        'Thank you for using our platform.\n\n'
        'Best regards,\n'
        'Your Platform Team'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_profile.user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        pass
    
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
from django.contrib.auth.models import User 
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .models import UserProfileDoc
@login_required

def user_profile(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if first_name and last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        about_me = request.POST.get('about_me')
        if about_me is not None and about_me.strip():
            user_profile.about_me = about_me

        uploaded_avatar = request.FILES.get('avatar')
        
        if uploaded_avatar:
            if user_profile.avatar:
                avatar_path = user_profile.avatar.path
                fs = FileSystemStorage()
                if fs.exists(avatar_path):
                    fs.delete(avatar_path)
            
            user_profile.avatar = uploaded_avatar

        user_profile.save()
        return redirect('userprofile')

    return render(request, 'userprofile.html', {'user_profile': user_profile, 'user': user})


def Billinginfo(request):
    return render(request, 'PremiumUserPage/Billinginfo.html')


def forgot_password(request):
    return render(request, 'forgot_password.html')


def successpage(request):
    return render(request, 'PremiumUserPage/successpage.html')

def errorpage(request):
    return render(request, 'PremiumUserPage/errorpage.html')



@login_required
def premiumuserpage(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        avatar = request.FILES.get('avatar')
        if avatar:
            user.userprofiledoc.avatar = avatar
            user.userprofiledoc.save()

        user.save()
        messages.success(request, 'Profile updated successfully.')

        return redirect('premiumuserpage')

    return render(request, 'PremiumUserPage/premiumuserpage.html', {'user': user})



from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
import razorpay
from .models import UserProfileDoc

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def paymentform(request: HttpRequest):
    currency = 'INR'
    amount = int(request.GET.get("amount")) * 100  # Rs. 200

    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount / 100
    context['currency'] = currency
    context['callback_url'] = callback_url

    return render(request, 'paymentform.html', context=context)

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from .models import UserProfileDoc

@csrf_exempt
@login_required
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
            client = razorpay.Client(auth=('rzp_test_0zpOMoTxoYH2my', '8CMU9Qg9plMX3mYD07IrUEu2'))
            payment = client.payment.fetch(payment_id)
            payment_amount = payment['amount']
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                authenticated_user = request.user
                user_profile = UserProfileDoc.objects.get(user=authenticated_user)
                amount = 200 if payment_amount == 20000 else 1000
                # Set the subscription duration based on the plan
                if amount == 200:
                    user_profile.subscription_duration = 1  # 1 month
                elif amount == 1000:
                    user_profile.subscription_duration = 12  # 12 months
                # Calculate the subscription expiration date
                current_date = datetime.now().date()
                expiration_date = current_date + timedelta(days=30 * user_profile.subscription_duration)  # Assuming 30 days per month
                user_profile.subscription_expiration = expiration_date
                # Set the user as subscribed
                user_profile.subscribed = True
                user_profile.save()
                username = authenticated_user.username
                # Your code for sending a successful subscription email
                subject = 'Subscription Successful'
                message = ('Dear {};'
                       '\n\nThank you for subscribing to our platform. We are thrilled to have you on board! Your subscription is now active, and you can start enjoying our exclusive content.;'
                       '\n\nTo begin your journey, click here👉🏻 http://127.0.0.1:8000/ to visit our index page. We have also attached a digital signature to this email for your reference.;'
                       '\n\nIf you have any questions or need assistance, please don\'t hesitate to contact us.;'
                       '\n\nBest Regards,'
                       '\nARR').format(username)
            
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [authenticated_user.email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                return render(request, 'PremiumUserPage/successpage.html')
            else:
                return render(request, 'PremiumUserPage/errorpage.html')
        except Exception as e:
            return render(request, 'PremiumUserPage/errorpage.html', {'error_message': str(e)})
    else:
        return render(request, 'PremiumUserPage/errorpage.html')







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
    wallpapers = WallpaperCollection.objects.filter(user=request.user)  # Move this line here
    all_tags = Tag.objects.all()  # Move this line here

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
        avatar = None  

    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper_to_delete = WallpaperCollection.objects.get(id=wallpaper_id)
        if wallpaper_to_delete.user == user:
            wallpaper_to_delete.delete()
            return redirect('view_delete_userwallpaper')

    context = {
        'wallpapers': wallpapers,
       "user_profile": user_profile,   
    }
    return render(request, 'view_delete_userwallpaper.html', context)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import WallpaperCollection
from django.shortcuts import render  # Import the render function

@csrf_exempt
def liked_wallpapers(request):
    liked_wallpaper_ids = json.loads(request.COOKIES.get("likedWallpapers")) or []

    liked_wallpapers_data = []
    
    for wallpaper_id in liked_wallpaper_ids:
        try:
            wallpaper = WallpaperCollection.objects.get(id=wallpaper_id)
            
            # Check if wallpaper.id is not empty (None) before including it in the data
            if wallpaper.id is not None:
                liked_wallpapers_data.append({
                    'title': wallpaper.title,
                    'image_url': request.build_absolute_uri(wallpaper.wallpaper_image.url),
                    'id': wallpaper.id  # Include wallpaper.id in the data
                })
        except ObjectDoesNotExist:
            pass
    
    context = {"wallpapers": liked_wallpapers_data}
    return render(request, 'liked_wallpapers.html', context)




from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def contactform(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        query = request.POST['query']

        # Send the email
        subject = 'Contact Form Submission'
        message = f'Name: {name}\nEmail: {email}\nQuery:\n{query}'
        from_email = email  
        recipient_list = [settings.EMAIL_HOST_USER]  

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, 'Your query has been submitted successfully.')
        except Exception as e:
            messages.error(request, f'An error occurred while sending your query: {str(e)}')

        return redirect('contactform')

    return render(request, 'registration/contactform.html')



def about(request):
    return render(request, 'registration/about.html')

def termsofservice(request):
    return render(request, 'registration/termsofservice.html')

def privacypolicy(request):
    return render(request, 'registration/privacypolicy.html')


def retrival(request):
    return render(request, 'retrival.html')
