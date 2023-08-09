from django.shortcuts import render

def homepage(request):
    return render(request, 'index.html')



def loginpage(request):
    return render(request, 'login.html')

    
def signuppage(request):
    return render(request, 'signup.html')


def forgot(request):
    # Handle form submission here (sending password reset email, etc.)
    # Implement your forgot password logic here if needed
    return render(request, 'forgot_password.html')