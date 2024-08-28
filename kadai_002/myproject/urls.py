"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, re_path
from crud import views as crud_views
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from crud import views



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # トップページ
    path('', crud_views.TopView.as_view(), name='home'),
    path('top/', crud_views.TopView.as_view(), name="top"),

    # レストランのリスト表示ページ
    path('restaurants/', crud_views.RestaurantListView.as_view(), name="restaurant_list"),

    # 検索機能のページ
    path('search/', crud_views.StoreView.as_view(), name='store_search'),

    # アカウント関連のページ
    path('account/', crud_views.TopView.as_view(), name="account"),
    path('login/', crud_views.LoginView.as_view(), name="login"),
    path('logout/', crud_views.LogoutView.as_view(next_page='/'), name="logout"),
    path('accounts/signup/', crud_views.SignupView.as_view(), name="signup"),
    path('accounts/edit/', crud_views.EditUserView.as_view(), name='edit_user'),

    # その他のページ
    path('crud/detail/<int:pk>', crud_views.RestaurantDetailView.as_view(), name="detail"),
    path('restaurant/<int:restaurant_id>/toggle_favorite/', crud_views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('mypage/', crud_views.MypageView.as_view(), name='mypage'),
    path('restaurant/<int:restaurant_id>/reserve/', crud_views.CreateReservationView.as_view(), name='create_reservation'),
    path('restaurant/<int:restaurant_id>/review/', crud_views.ReviewView.as_view(), name='review_form'),
    path('restaurant/<int:pk>/', crud_views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('payment/', crud_views.PaymentFormView.as_view(), name='payment_form'),
    path('create-subscription/', crud_views.CreateSubscriptionView.as_view(), name='create_subscription'),
    path('password_reset/', crud_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', crud_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', crud_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', crud_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('review/edit/<int:review_id>/', crud_views.EditReviewView.as_view(), name='edit_review'),
    path('review/delete/<int:review_id>/', crud_views.DeleteReviewView.as_view(), name='delete_review'),
    path('favorites/', crud_views.FavoritesListView.as_view(), name='favorites_list'),
    path('reservations/', crud_views.ReservationsListView.as_view(), name='reservations_list'),
    path('billing-portal/', crud_views.CustomerPortalView.as_view(), name='billing-portal'),
    path('cancel-subscription/', crud_views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('restaurant/<int:restaurant_id>/cancel/', crud_views.CancelReservationView.as_view(), name='cancel_reservation'),
    path('company-info/', crud_views.CompanyInfoView.as_view(), name='company_info'),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
   re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
   re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]