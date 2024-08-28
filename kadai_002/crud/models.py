from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # 追加のフィールドが必要な場合はここに定義
    pass
      

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Restaurant(models.Model):
     name = models.CharField(max_length=200)
     business_hours = models.CharField(default=None, max_length=200)
     start_time = models.CharField(default=None, max_length=200)
     end_time = models.CharField(default=None, max_length=200)
     zip_code = models.CharField(max_length=200)
     address = models.CharField(max_length=200,default='愛知県')
     phone_number = models.CharField(max_length=200)
     price_range = models.CharField(max_length=200)
     price_min = models.IntegerField(null=True, blank=True) 
     category = models.ForeignKey(Category, on_delete=models.CASCADE)
     img = models.ImageField(blank=True, default='noimage.png')

     def __str__(self):
        return self.name
    
     # 新規作成・編集完了時のリダイレクト先
     def get_absolute_url(self):
        return reverse('top')
     
class Subscription(models.Model):
      user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
      stripe_subscription_id = models.CharField(max_length=255, blank=True)
      stripe_customer_id = models.CharField(max_length=255, blank=True)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def __str__(self):
         return f"{self.user.username}'s Subscription"
      
class Review(models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
      restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviewed_by')
      content = models.CharField(max_length=255, blank=True)
      score = models.IntegerField(null=True)

      def __str__(self):
         return f"{self.user.username}'s Review"
      
class Favorite(models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
      restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='favorited_by')

      def __str__(self):
         return f"{self.user.username}'s Favorite"
      
class Reservation(models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
      restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reserved_by')
      reservation_date = models.DateField(null=True)
      reservation_time = models.TimeField(null=True)
      number_of_people = models.IntegerField(default=None)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      def __str__(self):
         return f"{self.user.username}'s Reservation at {self.restaurant.name}"
      
class UserManager(BaseUserManager):
    def _create_user(self, email, account_id, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, account_id=account_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, account_id, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, account_id, password, **extra_fields)

    def create_superuser(self, email, account_id, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, account_id, password, **extra_fields)
    


class Account(AbstractBaseUser, PermissionsMixin):
    account_id = models.CharField(verbose_name=_("account_id"), unique=True, max_length=10)
    email = models.EmailField(verbose_name=_("email"), unique=True)
    password = models.CharField(verbose_name=_("password"), max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    postal_code = models.CharField(verbose_name=_("postal_code"), max_length=12, null=True, blank=True)
    address = models.TextField(verbose_name=_("address"), null=True, blank=True)
    phone_number = models.CharField(verbose_name=_("phone_number"), max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=_("created_at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated_at"), auto_now=True)
    groups = models.ManyToManyField(Group, related_name='account_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='account_permissions')
    objects = UserManager()

    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['account_id']

    @property
    def username(self):
        return self.account_id

    def __str__(self):
        return self.account_id
    
class CompanyInfo(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    representative = models.CharField(max_length=255)  # 代表者の名前を追加
    established_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name      

