from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

                                                                    # Create your models here.
CATEGORY_CHOICES = [
    ('Audio', 'Audio'),
    ('Books', 'Books'),
    ('Gallery', 'Gallery'),
    ('General', 'General'),
]

class customManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_date')


class contacus(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    subject=models.CharField(max_length=200,choices=CATEGORY_CHOICES, default='General')
    message=models.TextField(max_length=500)
    #created_time = models.DateTimeField(default=timezone.now)
    created_date=models.DateTimeField(auto_now_add=True)
    #objects=customManager() #this is how we can use custom manager to sort the records based on created date in descending order
    class Meta: #this is how we can use meta class to define the ordering of the records or meta can be used to define other things like verbose name, db table name etc.
        ordering = ('-created_date',)  #WE CAN SORT THE RECORDS BASED ON CREATED DATE IN DESCENDING ORDER USING THIS INSTEAD OF WRITING CUSTOM MANAGER


YEAR_CHOICES=[('1927','1927'),('1985','1985'),('2000','2000'),('2015','2015')]

class aboutdetails(models.Model):
    title = models.CharField(max_length=264)
    slug = models.SlugField(max_length=264, unique=True)
    body = models.TextField()
    phase=models.CharField(max_length=20,choices=YEAR_CHOICES,default='1927')

    class Meta:
        ordering = ('phase',)

    def __str__(self):
        return self.title

#this method is for returning the string representation of the object (i.e. in layman words it returns the title of the aboutdetails object instead of the object memory location
# for example in realworld if we have multiple aboutdetails objects and we want to see the list of all aboutdetails objects in the admin panel or in the shell then instead of showing the memory location of each object it will show the title of each object which is more meaningful to us)

    def get_absolute_url(self):
         return reverse('aboutdetail',args=[self.slug])




"""------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
                                            # THE BELOW MODEL IS A TEMPORARY MODEL TO STORE THE WISH DATA FOR MY PRACTICE

class loginFormdata(models.Model):
    loginemail=models.CharField(max_length=100)
    loginpassword=models.CharField(max_length=100)

class wishdata(models.Model):
    username=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    astrology_message=models.CharField(max_length=300)
    mobilenumber=models.BigIntegerField(default=0)

    def get_absolute_url(self):
        return reverse('wishdetail',kwargs={'pk':self.pk})

class author(models.Model):
    authorname = models.CharField(max_length=100)
    age = models.IntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.authorname

class book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(author, on_delete=models.CASCADE,related_name='books_by_author')
    published_date = models.DateField()

    def __str__(self):
        return self.title