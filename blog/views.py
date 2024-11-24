from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from .models import Post, ContactForm

from django.core.mail import send_mail
from django.conf import settings 

from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .tokens import token_generator
from django.http import HttpResponse

# Home page view
def home_page(request):
    objects = Post.objects.all()
    return render(request, "blog/home.html", {"data": objects})

# About us page view
def about_us(request):
    return render(request, "blog/aboutus.html")

# Contact us page view with form submission
def contact_us(request):
    if request.method == "POST":
        fullname = request.POST["fname"]
        email_address = request.POST["email"]
        number = request.POST["number"]
        address = request.POST["address"]
        msg = request.POST["message"]
        
        if fullname == "" or email_address == "" or number == "" or address == "" or msg == "":
            messages.error(request, "All Input Must Be Filled !!")
            return redirect("contact_us")
        
        if len(number) != 10:
            messages.error(request, "Enter 10 Digits Number !!")
            return redirect("contact_us")
        
        else:
            ContactForm.objects.create(
                fullname=fullname,
                email=email_address,
                phone=number,
                address=address,
                message=msg
            )
            messages.success(request, "Form Submitted Successfully !!")
            return redirect("contact_us")
            
    return render(request, "blog/contact.html")

# Dashboard view for logged in users
def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
        full_name = user.get_full_name()
        gps = user.groups.all()
        
        if user.is_staff or user.is_superuser:
            posts = Post.objects.all() 
            return render(request, "blog/dashboard.html", {"posts": posts, "full_name": full_name, "groups": gps})
        else: 
            posts = Post.objects.filter(author=request.user)
            return render(request, "blog/dashboard.html", {"posts": posts, "full_name": full_name, "groups": gps})
    else:
        return redirect("login")

# Logout page view
def logout_page(request):
    if request.method == "POST":
        logout(request)
        messages.error(request, "Logout Successfully !!")
        return redirect("home_page")
    return render(request, "blog/logout.html")

# Register page with form validation and email confirmation
def register(request):
    form = RegisterForm()
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        pass1 = request.POST["password1"]
        pass2 = request.POST["password2"]
        
        if len(username) > 15:
            messages.error(request, "Character of username can't be more than 15 !!")
            return redirect("register")
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists !!")
            return redirect("register")
        if pass1 != pass2:
            messages.error(request, "Password did not match !!")
            return redirect("register")
        if username == "":
            messages.error(request, "Username can't be Empty !!")
            return redirect("register")
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=pass1
            )
            group = Group.objects.get(name="Author")
            user.groups.add(group)
            
            # Send registration email
            subject = "Thank You For Registration"
            message = f"Thank You {username} for Registration. We will send our updates to your email {email}"
            recipient_list = [email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=True)
            
            user.is_active = False
            user.save()
            
            # Prepare Email Confirmation
            current_site = get_current_site(request)
            email_subject = "Activate Your Account"
            email_message = render_to_string("account_activation.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": token_generator.make_token(user),
            })
            
            send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, recipient_list)
            messages.success(request, "Check Your Email For Account Activation !!")
            return redirect("register")
    return render(request, "blog/register.html", {"form": form})

# Email activation view for account verification
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your Account is Successfully Activated")
        return redirect("login")
    else:
        return HttpResponse("<h1>Failed To Activate</h1>")

# Login page view with authentication
def login_page(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            user_name = request.POST["username"]
            user_pass = request.POST["password"]
            
            new_user = authenticate(request, username=user_name, password=user_pass)
            if new_user is not None:
                login(request, new_user)
                messages.success(request, "Logged In Successfully !!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid Credentials !!")
                return redirect("login")
    else:
        return redirect("dashboard")
    return render(request, "blog/login.html")

# Add post page view for authenticated users
def add_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            title = request.POST["title"]
            desc = request.POST["desc"]
            
            if title == "" or desc == "":
                messages.error(request, "Title or Description Can't be Empty !!")
                return redirect("addpost")
            
            else:
                post = Post.objects.create(title=title, description=desc, author=request.user)
                post.save()
                messages.success(request, "Post Added Successfully!!")
                return redirect("dashboard")
        return render(request, "blog/addpost.html")
    else:
        return redirect("login")

# Edit post page view for authenticated users
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "blog/editpost.html", {"post": post})
        
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["desc"]
            
            post.title = title
            post.description = description
            post.save()
            
            messages.success(request, "Post Edited Successfully !!")
            return redirect("dashboard")
    else:
        return redirect("login")

# Delete post page view for authenticated users
def delete_post(request, id):
    if request.user.is_authenticated:
        if request.method == "POST":
            post = get_object_or_404(Post, pk=id)
            post.delete()
            return redirect("dashboard")
    return render(request, "blog/dashboard.html")
