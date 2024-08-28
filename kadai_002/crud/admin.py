from django.contrib import admin
from .models import Restaurant,Category,Subscription,Review,Favorite
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.models import Group
from .models import Account
from .models import CompanyInfo

# Register your models here.

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'representative', 'established_date')

class RestaurantAdmin(admin.ModelAdmin):
     list_display = ('id', 'name', 'business_hours', 'start_time', 'end_time', 'zip_code', 'address', 'phone_number', 'price_range', 'price_min', 'category', 'image')
     search_fields = ('name',)
     list_filter = ('category',)
     ordering = ('name',)  # デフォルトで名前順に並び替え

     def image(self, obj):
         if obj.img:
             return mark_safe(f'<img src="{obj.img.url}" style="width:100px; height:auto;">')
         return "No Image"
    
class CategoryAdmin(admin.ModelAdmin):
     list_display = ('id', 'name')
     search_fields = ('name',)

class SubscriptionAdmin(admin.ModelAdmin):
     list_display = ('id', 'stripe_subscription_id', 'stripe_customer_id',)
     search_fields = ('stripe_subscription_id',)

class ReviewAdmin(admin.ModelAdmin):
     list_display = ('id', 'restaurant', 'content',)
     search_fields = ('restaurant',)    

class FavoriteAdmin(admin.ModelAdmin):
     list_display = ('id', 'restaurant',)
     search_fields = ('restaurant',)    

class AccountAdmin(admin.ModelAdmin):
     list_display = ('id', 'email', 'account_id', 'postal_code', 'address', 'phone_number', 'created_at', 'updated_at')
     search_fields = ('email', 'account_id')
     list_filter = ('created_at', 'updated_at')




admin.site.unregister(Group)  # Groupモデルは不要のため非表示にします
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(User, UserAdmin) 