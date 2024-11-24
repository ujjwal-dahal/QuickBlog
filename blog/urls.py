from django.urls import path
from . import views

urlpatterns = [
    path("",views.home_page,name="home_page"),
    path("about-us/",views.about_us,name="about_us"),
    path("contact-us/",views.contact_us,name="contact_us"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("logout/",views.logout_page,name="logout"),
    path("register/",views.register,name="register"),
    path("login/",views.login_page,name="login"),
    path("addpost/",views.add_post,name="addpost"),
    path("editpost/<int:id>/",views.edit_post,name="editpost"),
    path("deletepost/<int:id>/",views.delete_post,name="deletepost"),
    path("activate/<str:uidb64>/token/<str:token>",views.activate_account,name="activate"),
    
]
