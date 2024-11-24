from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User,on_delete=models.CASCADE)



class ContactForm(models.Model):
    fullname = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=20)
    message = models.TextField()
    
    def __str__(self):
        return self.fullname