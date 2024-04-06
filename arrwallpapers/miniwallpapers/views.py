import os
import razorpay
import uuid
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
import requests
from .models import Category, ChatMessage, Tag, UserProfileDoc, WallpaperCollection
from django.shortcuts import get_object_or_404, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required  
from .models import UserProfileDoc
from django.views.decorators.cache import cache_control


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

            # Create UserProfileDoc and set is_premium to True
            user_profile = UserProfileDoc.objects.create(user=user, is_approved=True, is_premium=True)

            # Check and update SocialAccount if it exists
            if SocialAccount.objects.filter(user=user, provider='google').exists():
                google_account = SocialAccount.objects.get(user=user, provider='google')
                google_account.extra_data['is_premium'] = True
                google_account.save()

                user.is_staff = True
                user.save()

            messages.success(request, 'Your Premium Account has been Created')
            return redirect('login')
        except ValidationError as e:
            messages.error(request, str(e))
            messages.error(request, 'Cannot Register')
            return redirect('PremiumUserPage/Premium_signup')

    return render(request, "PremiumUserPage/Premium_signup.html")


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def set_premium_status(request):
    user = request.user
    user_profile = user.userprofiledoc 

    # Set is_premium to True
    user_profile.is_premium = True
    user_profile.save()

    return JsonResponse({'message': 'is_premium set to True'})



from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .forms import LoginForm

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if reCAPTCHA is valid
        if form.is_valid():
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_superuser or (hasattr(user, 'userprofiledoc') and user.userprofiledoc.is_approved):
                    auth.login(request, user)
                    if user.is_superuser or user.userprofiledoc.is_premium:
                        return redirect('index')
                    else:
                        return redirect('index')
                else:
                    messages.info(request, 'Your account is not approved yet. Please wait for admin approval.')
                    return redirect('login')
            else:
                messages.info(request, 'Invalid Credentials')
                return redirect('login')
        else:
            # ReCAPTCHA validation failed, display error message
            messages.error(request, 'Please complete the reCAPTCHA verification.')
            return redirect('login')
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})



from django.shortcuts import render
from .models import WallpaperCollection, UserProfileDoc, Category, Review
from django.views.decorators.cache import cache_control
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    query = request.GET.get('q')
    # Fetch wallpapers and creators excluding those with is_deleted=True
    wallpapers = WallpaperCollection.objects.select_related('user').prefetch_related('tags').filter(is_deleted=False).order_by('-upload_date')
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()

    # Retrieve the most viewed wallpapers
    most_viewed_wallpapers = WallpaperCollection.objects.order_by('-view_count')[:5]

    # Integrate sentiment analysis recommendation logic
    recommended_wallpapers = get_recommended_wallpapers(wallpapers)

    if query:
        wallpapers = wallpapers.filter(title__icontains=query)

    return render(request, 'index.html', {'wallpapers': wallpapers, 'creators': creators, 'admin_user': admin_user, 'categories': categories, 'query': query, 'most_viewed_wallpapers': most_viewed_wallpapers, 'recommended_wallpapers': recommended_wallpapers})



def get_recommended_wallpapers(wallpapers):
    sid = SentimentIntensityAnalyzer()
    for wallpaper in wallpapers:
        reviews_text = ' '.join([review.text for review in wallpaper.review_set.all()])
        if reviews_text:
            sentiment_score = sid.polarity_scores(reviews_text)['compound']
            wallpaper.sentiment_score = round(sentiment_score, 2)
        else:
            wallpaper.sentiment_score = 0.00
    recommended_wallpapers = wallpapers.order_by('-sentiment_score')[:5]

    return recommended_wallpapers







from django.shortcuts import render
from django.http import JsonResponse

def live_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('query', '')
        results = WallpaperCollection.objects.filter(title__istartswith=search_query, is_deleted=False)
        product_data = []

        for product in results:
            product_info = {
                'name': product.title,
                'id': product.id,
                'img1_url': product.wallpaper_image.url,  # Include img1 URL
            }
            product_data.append(product_info)

        return JsonResponse({'products': product_data})
    
from django.http import JsonResponse
from django.urls import reverse
from .models import WallpaperCollection, Category

def live_filter(request):
    categories = Category.objects.all()
    wallpapers = WallpaperCollection.objects.filter(is_deleted=False)

    # Extract filters from request
    query = request.GET.getlist('category')
    license_filter = request.GET.getlist('license')
    ratings_filter = request.GET.get('ratings', '')

    if query:
        wallpapers = wallpapers.filter(category__name__in=query)
    if license_filter:
        wallpapers = wallpapers.filter(price__in=license_filter)
    if ratings_filter:
        wallpapers = wallpapers.filter(average_rating=float(ratings_filter))

    # Generate HTML content for filtered wallpapers
    wallpaper_html_list = []

    for idx, wallpaper in enumerate(wallpapers):
        # Start a new row for every 3 wallpapers
        if idx % 3 == 0:
            wallpaper_html_list.append('<div class="row">')

        # Determine the title color based on the wallpaper's price
        title_color = 'white' if wallpaper.price == 'free' else 'gold'

        # Add a paid icon if the wallpaper is paid
        paid_icon = '<i class="fas fa-crown" style="position: absolute; top: 10px; right: 10px;"></i>' if wallpaper.price == 'paid' else ''

        wallpaper_html_list.append(
            f'<div class="col-md-4">' +
            f'   <a href="{reverse("wallpaper_details", args=[wallpaper.id])}" class="card-link" style="position: relative; overflow: hidden;">' +
            f'       <div class="card">' +
            f'           {paid_icon}' +
            f'           <img class="card-img-top" src="{wallpaper.wallpaper_image.url}" alt="{wallpaper.title}">' +
            f'           <div class="card-body">' +
            f'               <p class="card-title" style="color: {title_color};">Title: {wallpaper.title}</p>' +
            f'           </div>' +
            f'       </div>' +
            f'   </a>' +
            f'</div>'
        )

        # End the row for every 3 wallpapers
        if (idx + 1) % 3 == 0 or (idx + 1) == len(wallpapers):
            wallpaper_html_list.append('</div>')

    # Join the HTML content
    wallpaper_html = ''.join(wallpaper_html_list)

    # Return the HTML content as JSON response
    return JsonResponse({'html_content': wallpaper_html})






from django.shortcuts import render
from .models import WallpaperCollection, Category

def category_filter(request, category):
    category_obj = get_object_or_404(Category, name__iexact=category)
    categories = Category.objects.all()
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    wallpapers = WallpaperCollection.objects.filter(category=category_obj, is_deleted=False).order_by('-upload_date')

    return render(request, 'category_filter.html', {'wallpapers': wallpapers, 'selected_category': category_obj, 'categories': categories, 'admin_user': admin_user, 'creators' : creators})


def AIEditor(request):
    return render(request, 'AIEditor.html')




def subscribe_page(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
    return render(request, 'subscribe_page.html', context)



def arr_contributor(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
    return render(request, 'arr_contributor.html', context)



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfileDoc, WallpaperCollection
from django.db.models import Sum
from django.core.paginator import Paginator


def profileview(request, username):
    user = get_object_or_404(User, username=username)
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()

    if user.is_staff:
        user_profile = get_object_or_404(User, username=username)
        user_content = WallpaperCollection.objects.filter(user=user, is_deleted=False)
    else:
        user_profile = get_object_or_404(UserProfileDoc, user__username=username)
        user_content = WallpaperCollection.objects.filter(user=user_profile.user, is_superuser=False, is_deleted=False)

    superuser_content = WallpaperCollection.objects.filter(is_superuser=True, is_deleted=False)
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
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }

    return render(request, 'profileview.html', context)


def wallpaper_details(request, wallpaper_id):
    wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
    wallpapers = WallpaperCollection.objects.select_related('user').prefetch_related('tags').order_by('-upload_date')
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()

    # Increment view count
    wallpaper.view_count += 1
    wallpaper.save()

    ratings = Rating.objects.filter(wallpaper=wallpaper)
    reviews = Review.objects.filter(wallpaper=wallpaper, text__isnull=False).order_by('-created_at')


    total_ratings = ratings.count()
    total_reviews = reviews.count()
    total_users_rated = ratings.values('user').distinct().count()

    if wallpaper.price == 'paid':
        if request.user.is_authenticated:
            try:
                user_profile = UserProfileDoc.get_or_create_profile(request.user)

                # Check if the user is subscribed
                if user_profile.subscribed:
                    # Check if the user has already downloaded this wallpaper
                    if request.user not in wallpaper.downloads_by_user.all():
                        # Increment the download count for the wallpaper
                        wallpaper.downloads += 1
                        wallpaper.downloads_by_user.add(request.user)
                        wallpaper.save()

                        # Increment the creator's (uploader's) earnings
                        wallpaper.user.userprofiledoc.money += 5
                        wallpaper.user.userprofiledoc.save()

            except Exception as e:
                pass

    return render(request, 'wallpaper_details.html', {
        'wallpaper': wallpaper,
        'wallpapers': wallpapers,
        'creators': creators,
        'admin_user': admin_user,
        'categories': categories,
        'ratings': ratings,
        'reviews': reviews,
        'total_ratings': total_ratings,
        'total_reviews': total_reviews,
        'total_users_rated': total_users_rated,
    })



    
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import WallpaperCollection, Rating, Review

@login_required
def post_rating(request, wallpaper_id):
    if request.method == 'POST':
        try:
            wallpaper = WallpaperCollection.objects.get(id=wallpaper_id)
        except WallpaperCollection.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Wallpaper not found'})

        user = request.user
        rating_value = request.POST.get('star')

        try:
            # Ensure 'value' is a valid number
            rating_value = int(rating_value)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid rating value'})

        review_text = request.POST.get('review', '')

        # Save the rating
        Rating.objects.create(user=user, wallpaper=wallpaper, value=rating_value)

        # Save the review
        Review.objects.create(user=user, wallpaper=wallpaper, text=review_text)

        # Update average rating and total ratings for the wallpaper
        wallpaper.update_average_rating()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})



import qrcode
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from io import BytesIO

def generate_qrcode_url(request, wallpaper_id):
    wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
    wallpaper_url = request.build_absolute_uri(wallpaper.wallpaper_image.url)
    return HttpResponse(wallpaper_url)
    # qr_code_url = f"https://arrwallpapers.pythonanywhere.com/wallpaper/{wallpaper_id}/"
    # return HttpResponse(qr_code_url)





from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfileDoc

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

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
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

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



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

def delete_sub(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect('admin_dashboard')  
    return render(request, 'admin_dashboard.html') 



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    if request.user.is_superuser:
        # Fetch all users and user profiles
        users = User.objects.all()
        user_profiles = UserProfileDoc.objects.select_related('user').all()

        # Fetch notifications
        notifications = UserProfileDoc.objects.filter(is_approved=False)

        context = {
            'users': users,
            'user_profiles': user_profiles,
            'notifications': notifications,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        return redirect('login')



from django.contrib.auth import logout as django_logout
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def custom_logout(request):
    django_logout(request)
    return redirect('index')  



from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .models import UserProfileDoc, WallpaperCollection

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_profile(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    user = request.user

    # Fetch the count of uploaded wallpapers
    uploaded_wallpapers_count = WallpaperCollection.objects.filter(user=user).count()


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

    return render(request, 'userprofile.html', {'user_profile': user_profile, 'user': user, 'uploaded_wallpapers_count': uploaded_wallpapers_count})



def Billinginfo(request):
    return render(request, 'PremiumUserPage/Billinginfo.html')


def forgot_password(request):
    return render(request, 'forgot_password.html')


def successpage(request):
    return render(request, 'PremiumUserPage/successpage.html')

def errorpage(request):
    return render(request, 'PremiumUserPage/errorpage.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfileDoc  # Import your UserProfileDoc model here

@login_required
def premiumuserpage(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        
        # Handle avatar update
        avatar = request.FILES.get('avatar')
        print(avatar)  # Add this line for debugging
        if avatar:
            # Assuming UserProfileDoc is related to User through a OneToOneField
            profile, created = UserProfileDoc.objects.get_or_create(user=user)
            profile.avatar = avatar
            profile.save()

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
from datetime import datetime, timedelta, timezone
from .models import UserProfileDoc
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.utils import formats
from io import BytesIO
import os
from django.core.mail import EmailMessage

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
            result = client.utility.verify_payment_signature(params_dict)

            if result is not None:
                authenticated_user = request.user
                print(authenticated_user)
                user_profile = UserProfileDoc.objects.get(user=authenticated_user)
                print(user_profile)
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
                
                # Generate PDF invoice
                pdf_data, pdf_path = generate_invoice(username, current_date, expiration_date)

                # Save PDF file to media/invoices folder
                user_profile.invoice_path = pdf_path
                user_profile.save()

                # Send the email with PDF attachment
                subject = 'Subscription Successful'
                message = (
                    'Dear {},'
                    '\n\nThank you for subscribing to our platform. We are thrilled to have you on board! Your subscription is now active, and you can start enjoying our exclusive content.;'
                    '\n\nTo begin your journey, click here👉🏻 http://127.0.0.1:8000/ to visit our index page. We have also attached a digital signature to this email for your reference.;'
                    '\n\nIf you have any questions or need assistance, please don\'t hesitate to contact us.;'
                    '\n\nBest Regards,'
                    '\nARR'
                ).format(username)
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [authenticated_user.email]
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=recipient_list,
                )
                email.attach('invoice.pdf', pdf_data, 'application/pdf')
                email.send(fail_silently=False)
                return render(request, 'PremiumUserPage/successpage.html')
            else:
                return render(request, 'PremiumUserPage/errorpage.html')
        except Exception as e:
            print(e, "sdfsdf")
            return render(request, 'PremiumUserPage/errorpage.html', {'error_message': str(e)})
    else:
        return render(request, 'PremiumUserPage/errorpage.html')

def generate_invoice(username, start_date, end_date):
    # Create a buffer to store the PDF data
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    data = [
        ['Username', 'Subscription Start Date', 'Subscription End Date'],
        [username, formats.date_format(start_date, 'SHORT_DATE_FORMAT'), formats.date_format(end_date, 'SHORT_DATE_FORMAT')],
    ]
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    pdf.build([table])
    pdf_data = buffer.getvalue()
    buffer.close()

    # Define the path where the PDF will be saved
    pdf_filename = f"{username}_invoice.pdf"
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', pdf_filename)

    # Check if the file already exists
    if os.path.exists(pdf_path):
        # If it exists, remove it
        os.remove(pdf_path)

    # Write the PDF data to the file
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)

    return pdf_data, pdf_path



from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import WallpaperCollection, Category, Tag
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico', 'jfif', 'pjpeg', 'pjp', 'avif']
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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



from django.shortcuts import render, get_object_or_404, redirect
from .models import WallpaperCollection  # Import your WallpaperCollection model
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_delete_wallpaper(request):
    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
        
        # Update the 'is_deleted' field instead of calling delete()
        wallpaper.is_deleted = True
        wallpaper.save()
        
        return redirect('view_delete_wallpaper')
    
    wallpapers = WallpaperCollection.objects.filter(is_deleted=False)
    context = {'wallpapers': wallpapers}
    return render(request, 'view_delete_wallpaper.html', context)



from django.contrib.auth.decorators import login_required
from .models import WallpaperCollection, UserProfileDoc
from django.shortcuts import render, redirect, get_object_or_404
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def view_delete_userwallpaper(request):
    user = request.user
    uploaded_wallpapers_count = WallpaperCollection.objects.filter(user=user, is_deleted=False).count()
    wallpapers = WallpaperCollection.objects.filter(user=user, is_deleted=False)
    try:
        user_profile = UserProfileDoc.objects.get(user=user)
        avatar = user_profile.avatar
    except UserProfileDoc.DoesNotExist:
        avatar = None  

    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper_to_delete = get_object_or_404(WallpaperCollection, id=wallpaper_id, user=user, is_deleted=False)
        wallpaper_to_delete.is_deleted = True
        wallpaper_to_delete.save()
        return redirect('view_delete_userwallpaper')

    context = {
        'wallpapers': wallpapers,
        "user_profile": user_profile,  
        'uploaded_wallpapers_count': uploaded_wallpapers_count,
    }
    return render(request, 'view_delete_userwallpaper.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import WallpaperCollection
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def recyclebin(request):
    deleted_wallpapers = WallpaperCollection.objects.filter(is_deleted=True, user=request.user)
    context = {'deleted_wallpapers': deleted_wallpapers}
    return render(request, 'recyclebin.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def restore_wallpaper(request):
    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
        
        # Restore the wallpaper by setting is_deleted to False
        wallpaper.is_deleted = False
        wallpaper.save()

    return redirect('recyclebin')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userrecyclebin(request):
    deleted_wallpapers = WallpaperCollection.objects.filter(is_deleted=True, user=request.user)
    context = {'deleted_wallpapers': deleted_wallpapers}
    return render(request, 'userrecyclebin.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def restore_wallpaper1(request):
    if request.method == 'POST':
        wallpaper_id = request.POST.get('wallpaper_id')
        wallpaper = get_object_or_404(WallpaperCollection, id=wallpaper_id)
        
        # Restore the wallpaper by setting is_deleted to False
        wallpaper.is_deleted = False
        wallpaper.save()

    return redirect('userrecyclebin')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .models import WallpaperCollection, Category, Tag, UserProfileDoc

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'ico', 'jfif', 'pjpeg', 'pjp', 'avif']
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_upload(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    categories = Category.CATEGORY_CHOICES  # Define categories outside the if-else block
    
    # Default values
    uploaded_wallpapers_count = 0

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        user = request.user  # Move this line here
        category_name = request.POST.get("category")
        tags_input = request.POST.get("tags")
        tags_names = [tag.strip() for tag in tags_input.split(",")]

        # Create or get tags from the database
        tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_names]

        category, created = Category.objects.get_or_create(name=category_name)
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

        # Move this line after the user is assigned a value
        uploaded_wallpapers_count = WallpaperCollection.objects.filter(user=user).count()

    else:
        tags = Tag.objects.all()
        user = request.user  # Move this line here
        # Fetch the count of uploaded wallpapers outside the if-else block
        uploaded_wallpapers_count = WallpaperCollection.objects.filter(user=user).count()

    context = {
        "tags": tags,
        "categories": categories,
        "user_profile": user_profile,
        'uploaded_wallpapers_count': uploaded_wallpapers_count,
    }

    return render(request, "user_upload.html", context)



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_edit_wallpaper(request):
    user_profile = UserProfileDoc.objects.get(user=request.user)
    wallpapers = WallpaperCollection.objects.filter(user=request.user)
    
    # Fetch the count of uploaded wallpapers
    uploaded_wallpapers_count = WallpaperCollection.objects.filter(user=request.user).count()

    all_tags = Tag.objects.all()

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

            # Create or get tags from the database
            tags = [Tag.objects.get_or_create(name=tag)[0] for tag in tags_list]

            wallpaper.tags.set(tags)

            messages.success(request, "Wallpaper updated successfully")
        except WallpaperCollection.DoesNotExist:
            messages.error(request, "Wallpaper not found or you don't have permission to edit it")

    context = {
        "wallpapers": wallpapers,
        "all_tags": all_tags,
        "user_profile": user_profile,  
        'uploaded_wallpapers_count': uploaded_wallpapers_count, 
    }
    return render(request, "user_edit.html", context)




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
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
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
    
    context = {"wallpapers": liked_wallpapers_data,
               "categories": categories,
               "admin_user" : admin_user,
               "creators": creators,
               
               }
    return render(request, 'liked_wallpapers.html', context)




from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def contactform(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
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

    return render(request, 'registration/contactform.html', context)



from django.shortcuts import render
import base64
import requests
import os

def ai_wallpaper_generator(request):
    if request.method == 'POST':
        user_prompt = request.POST.get('prompt')
        user_quantity = int(request.POST.get('quantity', 4))  

        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"

        body = {
            "steps": 40,
            "width": 512,
            "height": 512,
            "seed": 0,
            "cfg_scale": 5,
            "samples": user_quantity,
            "text_prompts": [
                {
                    "text": user_prompt,
                    "weight": 1
                },
                {
                    "text": "blurry, bad",
                    "weight": -1
                }
            ],
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-XpqT6E5KObGoqZc5g5aj3tQNIKMP0rZGXFmOhEuN8P7y4RlL",  
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()

        image_data = [{'b64_json': image['base64']} for image in data["artifacts"]]

        return render(request, 'ai_wallpaper_generator.html', {'image_data': image_data})

    return render(request, 'ai_wallpaper_generator.html')



# import os
# import requests
# from django.conf import settings 
# from django.shortcuts import render

# # Load API key 
# API_KEY = os.environ.get('sk-JVY41JII6OjgoPqnzsyTzxas7iJsjFeOCyY9DLRGJXy7x8o7')

# def upscaleimage(request):
#     if request.method == 'POST':
#         image = request.FILES['image']
        
#         # Save image 
#         temp_path = os.path.join(settings.MEDIA_ROOT, 'temp.png')
#         with open(temp_path, 'wb+') as f:
#             for chunk in image.chunks(): 
#                 f.write(chunk)
        
#         # Prepare headers
#         headers = {
#             'Authorization': f'Bearer {API_KEY}',
#             'Accept': 'application/json'  
#         }
        
#         # API request
#         endpoint = 'https://api.stability.ai/v1/image-to-image/upscale'  
#         files = {'image': open(temp_path, 'rb')}
#         response = requests.post(endpoint, headers=headers, files=files)

#         # Process response 
#         upscaled_images = []
#         if response.status_code == 200:
#             data = response.json()
            
#             for item in data['artifacts']:
#                 image = base64.b64decode(item['base64']) 
#                 filename = f'upscaled_{item["seed"]}.png'
                
#                 image_path = os.path.join(settings.MEDIA_ROOT, filename)  
#                 with open(image_path, 'wb') as f:
#                     f.write(image)  
                    
#                 upscaled_images.append(filename)

#         context = {'images': upscaled_images}       
#         return render(request, 'upscaleimage.html', context)

#     return render(request, 'upscaleimage.html')


def about(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
    return render(request, 'registration/about.html', context)



def termsofservice(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
    
    return render(request, 'registration/termsofservice.html', context)


def privacypolicy(request):
    creators = UserProfileDoc.objects.filter(is_creator=True)
    admin_user = User.objects.filter(is_staff=True).first()
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'admin_user': admin_user,
        'creators' : creators,
    }
    return render(request, 'registration/privacypolicy.html', context)



import os
import numpy as np
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings  # Import Django settings module
from .models import WallpaperCollection
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from keras.applications import VGG16

# Load pre-trained VGG16 model
vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Function to extract features from an image using VGG16 model
def extract_features_vgg(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    features = vgg_model.predict(img_array)
    features = features.flatten()
    return features

def calculate_similarity(descriptor1, descriptor2):
    # Use cosine similarity for comparing feature vectors
    return cosine_similarity([descriptor1], [descriptor2])[0][0]

from django.shortcuts import render
from .models import WallpaperCollection, UserProfileDoc, Category

def retrival(request):
    if request.method == 'POST' and request.FILES.get('fileInput'):
        uploaded_file = request.FILES['fileInput']  # Get the uploaded file object

        # Save the uploaded file to the media/similarimage folder
        media_root = settings.MEDIA_ROOT
        similar_image_dir = os.path.join(media_root, 'similarimage')
        if not os.path.exists(similar_image_dir):
            os.makedirs(similar_image_dir)

        uploaded_image_path = os.path.join(similar_image_dir, uploaded_file.name)
        with open(uploaded_image_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Extract features from the uploaded image
        uploaded_image_descriptor = extract_features_vgg(uploaded_image_path)

        # Retrieve all wallpapers from the database
        all_wallpapers = WallpaperCollection.objects.select_related('user').filter(is_deleted=False)

        # Calculate similarity with each wallpaper
        similarity_scores = []
        for wallpaper in all_wallpapers:
            wallpaper_descriptor = extract_features_vgg(wallpaper.wallpaper_image.path)
            similarity_score = calculate_similarity(uploaded_image_descriptor, wallpaper_descriptor)
            similarity_scores.append((wallpaper, similarity_score))

        # Sort wallpapers by similarity score (descending order)
        similarity_scores.sort(key=lambda x: x[1], reverse=True)

        # Fetch top 5 wallpapers with the highest similarity scores
        similar_wallpapers = similarity_scores[:5]

        # Prepare data for rendering
        similar_wallpapers_data = [{
            'title': wallpaper.title,
            'image_url': wallpaper.wallpaper_image.url,
            'pk': wallpaper.pk,
            'similarity_score': score
        } for wallpaper, score in similar_wallpapers]

        # Retrieve additional context variables
        creators = UserProfileDoc.objects.filter(is_creator=True)
        admin_user = User.objects.filter(is_staff=True).first()
        categories = Category.objects.all()

        # Combine all context variables
        context = {
            'similar_wallpapers': similar_wallpapers_data,
            'categories': categories,
            'admin_user': admin_user,
            'creators': creators,
        }

        # Render the HTML template with the retrieved wallpapers and additional context
        return render(request, 'retrival.html', context)
    elif request.method == 'GET':
        # Handle the GET request, e.g., render the template with an empty list
        return render(request, 'retrival.html', {'similar_wallpapers': []})
    else:
        # Handle other request methods
        return render(request, 'retrival.html', {'error': 'Invalid request'})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatMessage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render
from .models import UserProfileDoc

def community(request):
    chat_messages = ChatMessage.objects.select_related('user__userprofiledoc').order_by('timestamp')
    users_with_avatars = User.objects.filter(userprofiledoc__avatar__isnull=False)
    return render(request, 'community.html', {'chat_messages': chat_messages, 'users_with_avatars': users_with_avatars})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def send_message(request):
    if request.method == 'POST':
        user = request.user
        message = request.POST.get('message', '')
        image = request.FILES.get('image')

        # Check if the message or image is not empty
        if message or image:
            chat_message = ChatMessage.objects.create(user=user, message=message, image=image)
            channel_layer = get_channel_layer()
            try:
                async_to_sync(channel_layer.group_send)(
                    'chat_group',
                    {
                        'type': 'chat.message',
                        'message': chat_message.message,
                        'username': user.username,
                        'image_url': chat_message.image.url if chat_message.image else None,
                    }
                )
                messages.success(request, 'Message sent successfully!')
            except Exception as e:
                print(f"Error sending message: {e}")
                messages.error(request, 'Failed to send message.')
        else:
            messages.error(request, 'Invalid message or image. Please provide a non-empty message or select an image.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('community')
    










from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

class SuperuserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfileDoc
from .serializers import UserProfileSerializer

class UserProfileListView(APIView):
    def get(self, request):
        user_profiles = UserProfileDoc.objects.filter(is_creator=True)
        serializer = UserProfileSerializer(user_profiles, many=True)
        return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import UserProfileDoc
from .serializers import UserProfileSerializer

@api_view(['POST'])
def approve_user_api(request, user_id):
    user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
    user_profile.is_approved = True
    user_profile.save()
    # You can also send an email notification here if needed
    return Response({'message': 'User approved successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def deactivate_user_api(request, user_id):
    user_profile = get_object_or_404(UserProfileDoc, user__id=user_id)
    user_profile.is_approved = False
    user_profile.save()
    # You can also send an email notification here if needed
    return Response({'message': 'User deactivated successfully'}, status=status.HTTP_200_OK)
