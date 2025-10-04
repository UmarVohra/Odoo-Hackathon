from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
import string
from .models import *
# Create your views here.


def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        logo = request.FILES.get("logo")
        country = request.POST.get("country")
        currency = request.POST.get("currency")
        password = request.POST.get("password")
        
        # Create user with encrypted password
        user = User.objects.create(
            username=email,  # Using email as username
            email=email,
            password=make_password(password),  # Encrypt password
            name=name,
            is_admin=True
        )
        
        # Create Company profile with role
        company = Company.objects.create(
            name=name,
            email=email,
            password=make_password(password),  # Encrypt password
            logo=logo,
            country=country,
            currency=currency,
        )
        
        # Update user with company information
        user.company_id = company.id
        user.save()
        
        # Redirect to login page after successful registration
        return redirect('login')

    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            # Try to get user by email (which we used as username)
            user = User.objects.get(email=email)
        
            authenticated_user = authenticate(username=email, password=password)
            
            if authenticated_user is not None:
                # Login the user
                login(request, authenticated_user)
                
                # Get user's role and redirect accordingly
                user_profile = User.objects.get(user=authenticated_user)
                if user_profile.role == 'admin':
                    return redirect('admin_dashboard')
                elif user_profile.role == 'manager':
                    return redirect('manager_dashboard')
                else:  # employee
                    return redirect('employee_dashboard')
            else:
                error = "Invalid password"
                return render(request, "login.html", {"error": error})
                
        except User.DoesNotExist:
            error = "User with this email does not exist"
            return render(request, "login.html", {"error": error})
        except User.DoesNotExist:
            error = "User profile not found"
            return render(request, "login.html", {"error": error})
    
    return render(request, "login.html")
    
    
def add_user(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return redirect('login')
        
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")
        speciality = request.POST.get("speciality", "")  # Get speciality if provided
        
        # Generate a random password
        password_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(password_characters) for i in range(12))
        
        try:
            # # Create user with encrypted password
            # user = User.objects.create(
            #     username=email,  # Using email as username
            #     email=email,
            #     password=make_password(password),  # Encrypt password
            #     first_name=name
            # )
            
            # Get logged in user's company
            admin_user = User.objects.get(email=request.user.email)
            if not admin_user.company_id:
                raise Exception("No company associated with your account")
                
            # Create User profile with roles
            user = User.objects.create(
                username=email,
                company_id=admin_user.company_id,  # Use the admin's company_id
                name=name,
                email=email,
                phone=phone,
                password=make_password(password),  # Store encrypted password in our User model
                # Set appropriate flags based on role and speciality
                is_employee=(role == 'employee'),
                is_manager=(role == 'manager'),
                is_director=(role == 'manager' and speciality == 'director'),
                is_finance=(role == 'manager' and speciality == 'finance'),
                is_admin=False,  # Set this based on your requirements
                is_mandatory=False  # Set this based on your requirements
            )
            user.save()
            
            # Send email with password
            email_subject = "Your Account Details"
            email_message = f"""
            Hello {name},
            
            Your account has been created successfully.
            Here are your login details:
            
            Email: {email}
            Password: {password}
            
            Please change your password after your first login for security purposes.
            
            Best regards,
            {user.company_id.name}
            """
            
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # Redirect to users list or appropriate dashboard with success message
            messages.success(request, f'User account created successfully. Password has been sent to {email}')
            return redirect('users_list')
            
        except Exception as e:
            # If any error occurs, show error message
            messages.error(request, f'Error creating user: {str(e)}')
            return redirect('add_user')
    
    # If GET request, show the add user form
    return render(request, "add_user.html")
