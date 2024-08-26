from django.shortcuts import render, resolve_url
from django.views.generic import TemplateView, ListView, DetailView
from .models import Restaurant, Favorite, Reservation,Review
from .models import Subscription
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy, reverse
from django.views import generic
from urllib import parse
from .forms import SignUpForm
from .forms import UserEditForm
from .forms import RestaurantFilterForm
from .models import User, Store
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from .forms import EmailAuthenticationForm


# Create your views here.

class TopView(TemplateView):
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['has_subscription'] = Subscription.objects.filter(user=user).exists()
        else:
            context['has_subscription'] = False
        
        # 検索クエリを取得
        query = self.request.GET.get('search_query')
        if query:
            context['object_list'] = Restaurant.objects.filter(name__icontains=query)
            return context
        else:
            context['object_list'] = Restaurant.objects.all()
        
        # カテゴリーを取得
        category = self.request.GET.get('search_category')
        if category:
            context['object_list'] = Restaurant.objects.filter(category__name__icontains=category)
        else:
            context['object_list'] = Restaurant.objects.all()

        return context
    
class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = "Restaurant_detail.html"
    context_object_name = "restaurant"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = context["restaurant"]
        user = self.request.user
        if user.is_authenticated:
            context["is_favorite"] = Favorite.objects.filter(
                user=user, restaurant=restaurant
            ).exists()
            # 予約の存在チェックを追加
            context["has_reservation"] = Reservation.objects.filter(
                user=user, restaurant=restaurant
            ).exists()

            if context["has_reservation"]:
                context["url"] = "cancel_reservation"
            else:
                context["url"] = "create_reservation"
        else:
            context["is_favorite"] = False
            context["has_reservation"] = False

        # レストランに紐づくレビュー一覧を取得
        context["reviews"] = Review.objects.filter(restaurant=restaurant)
        return context

class MypageView(TemplateView):
    template_name = 'mypage.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["has_subscription"] = Subscription.objects.filter(user=user).exists()
        return context
     


class RestaurantListView(ListView):
    model = Restaurant
    template_name = "index.html"
    context_object_name = 'restaurant_list'

    def get_queryset(self):
        sort = self.request.GET.get('sort')
        queryset = super().get_queryset()
      
       # フィルタリングフォームのデータを取得
        form = RestaurantFilterForm(self.request.GET)
        
        if form.is_valid():
            category = form.cleaned_data.get('category')
            price_min = form.cleaned_data.get('price_min')
            price_max = form.cleaned_data.get('price_max')
            business_hours = form.cleaned_data.get('business_hours')

            # カテゴリでフィルタリング
            if category:
                queryset = queryset.filter(category__name__icontains=category)
            # 最小価格でフィルタリング
            if price_min:
                queryset = queryset.filter(price_range__gte=price_min)
            # 最大価格でフィルタリング
            if price_max:
                 queryset = queryset.filter(price_range__lte=price_max)
            # 営業時間でフィルタリング
            if business_hours:
                 queryset = queryset.filter(business_hours__icontains=business_hours)


        if sort in ['name', 'price_min', 'business_hours']:
          queryset = queryset.order_by(sort)
          
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = RestaurantFilterForm(self.request.GET)
        return context


        
    
class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    
class LogoutView(LoginRequiredMixin, LogoutView):
     template_name = 'index.html'

class SignupView(generic.CreateView):
    model = User
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    

    def get_return_link(request):
      top_page = resolve_url('diary:top')  
      referer = request.environ.get('HTTP_REFERER')  # これが、前ページのURL
   
      if referer:

       
          parse_result = parse.urlparse(referer)
   
          if request.method == 'POST':
            form = SignUpForm(request.POST)
            if request.get_host() == parse_result.netloc:
                return referer

            return top_page
          
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):

        user = request.user
        if not Subscription.objects.filter(user=user).exists():
            messages.success(request, "有料会員になる必要があります。")
            return redirect("payment_form")

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)

        if not created:
            favorite.delete()
        else:
            favorite.save()

        return redirect('restaurant_detail', pk=restaurant.id)
    
class CreateReservationView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):

        user = request.user
        if not Subscription.objects.filter(user=user).exists():
            messages.success(request, "有料会員になる必要があります。")
            return redirect("payment_form")

        user = request.user
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        reservation_date = request.POST.get('reservation_date')
        reservation_time = request.POST.get('reservation_time')
        number_of_people = request.POST.get('number_of_people')

        reservation = Reservation(
            user=user,
            restaurant=restaurant,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            number_of_people=number_of_people
        )
        reservation.save()

        messages.success(request, "予約が完了しました。")
        return redirect('restaurant_detail', pk=restaurant.id)
    
class ReviewView(TemplateView):
    template_name = "crud/review_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs.get("restaurant_id")
        context["restaurant"] = get_object_or_404(Restaurant, pk=restaurant_id)
        return context

    def post(self, request, restaurant_id):
        user = request.user
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        score = request.POST.get("score", 0)
        comment = request.POST.get("comment", "")
        review = Review(user=user, restaurant=restaurant, score=score, content=comment)
        review.save()

        messages.success(request, "投稿しました。")
        return redirect("restaurant_detail", pk=restaurant.id)
    

class ReviewView(TemplateView):
    template_name = "review_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.kwargs.get("restaurant_id")
        context["restaurant"] = get_object_or_404(Restaurant, pk=restaurant_id)
        return context

    def post(self, request, restaurant_id):
        user = request.user
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        score = request.POST.get("score", 0)
        comment = request.POST.get("comment", "")
        review = Review(user=user, restaurant=restaurant, score=score, content=comment)
        review.save()

        messages.success(request, "投稿しました。")
        return redirect("restaurant_detail", pk=restaurant.id)

class PaymentFormView(TemplateView):
     template_name = 'payment_form.html'

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        user = self.request.user
        context["has_subscription"] = Subscription.objects.filter(user=user).exists()
        return context
     
@method_decorator(csrf_exempt, name='dispatch')
class CreateSubscriptionView(View):

    def post(self, request, *args, **kwargs):
        token = request.POST.get('stripeToken')
        price_id = 'price_1PmYTQCxkLD8AKFtbHkwp6l2'

        try:
            customer = stripe.Customer.create(
                source=token,
                email=request.user.email
            )
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
            )

            django_subscription = Subscription(
                user=request.user,
                stripe_subscription_id=subscription.id,
                stripe_customer_id=customer.id
            )
            django_subscription.save()

            messages.success(request, 'Subscription created successfully!')
            return redirect('top')
        except stripe.error.StripeError as e:
            print(f'Error creating subscription: {str(e)}')
            messages.error(request, f'Error creating subscription: {str(e)}')

class EditReviewView(DetailView):
    model = Review
    template_name = 'crud/edit_review.html'
    pk_url_kwarg = 'review_id'

    def post(self, request, *args, **kwargs):
        user = request.user
        if not Subscription.objects.filter(user=user).exists():
            messages.success(request, "有料会員になる必要があります。")
            return redirect("payment_form")

        review = self.get_object()
        score = request.POST.get("score")
        content = request.POST.get("content")
        review.score = score
        review.content = content
        review.save()
        # レビューに紐づくレストランの詳細ページにリダイレクト
        restaurant_id = review.restaurant.id
        return redirect('restaurant_detail', pk=restaurant_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review'] = self.get_object()
        return context
    
class DeleteReviewView(LoginRequiredMixin, View):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        if request.user == review.user:
            review.delete()
            messages.success(request, "レビューが削除されました。")
        else:
            messages.error(request, "このレビューを削除する権限がありません。")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "top"))

class EditUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('top')

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # フォームのデータを保存する
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)
    
class FavoritesListView(ListView):
    model = Favorite
    template_name = "favorites_list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        # ログインしているユーザーのお気に入りとそれに紐づいているレストランを取得
        return Favorite.objects.filter(user=self.request.user).select_related('restaurant')
    
class ReservationsListView(ListView):
    model = Reservation
    template_name = "reservations_list.html"
    context_object_name = "reservations"

    def get_queryset(self):
        # ログインしているユーザーの予約のみを取得
        return Reservation.objects.filter(user=self.request.user)
    
class CustomerPortalView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        user = request.user
        try:
            subscription = Subscription.objects.get(user=user)
            customer_id = subscription.stripe_customer_id

            # 顧客ポータルセッションの作成
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url="https://test052214-27c4362284fb.herokuapp.com/",
            )

            # 顧客ポータルのURLへリダイレクト
            return HttpResponseRedirect(session.url)
        except Subscription.DoesNotExist:
            messages.error(request, "有料登録してください。")
            return redirect("top")
        
from django.http import JsonResponse
class CancelSubscriptionView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")

        try:
            subscription = Subscription.objects.get(user=user)
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            subscription.delete()
            messages.success(request, "解約が完了しました")
            return redirect("top")
        except Subscription.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "No subscription found."}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        
class EditUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'edit_user.html'
    success_url = reverse_lazy('top')

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # フォームのデータを保存する
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)
    
class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, restaurant_id):
        user = request.user
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

        user = request.user
        if not Subscription.objects.filter(user=user).exists():
            messages.success(request, "有料会員になる必要があります。")
            return redirect("payment_form")

        reservation = Reservation.objects.filter(user=user, restaurant=restaurant)
        reservation.delete()

        messages.success(request, "予約をキャンセルしました。")
        return redirect('restaurant_detail', pk=restaurant.id)
    
from django.views.generic import TemplateView
from .models import CompanyInfo

class CompanyInfoView(TemplateView):
    template_name = 'company_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_info'] = CompanyInfo.objects.first()  # 会社情報を取得
        return context

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    token_generator = auth_views.PasswordResetView.token_generator

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    token_generator = auth_views.PasswordResetView.token_generator

    def form_valid(self, form):
        for user in form.get_users(form.cleaned_data["email"]):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = self.token_generator.make_token(user)
            domain = self.request.META['HTTP_HOST']
            link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            full_link = f"http://{domain}{link}"

            context = {
                'user': user,
                'domain': domain,
                'uid': uid,
                'token': token,
                'full_link': full_link,
            }
            # 件名を生成し、改行を削除
            subject = render_to_string(self.subject_template_name, context).replace('\n', '').replace('\r', '')
            # メール本文を生成
            message = render_to_string(self.email_template_name, context)

            # メールを送信
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return super().form_valid(form)

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

class StoreView(ListView):
    model = Store
    template_name = 'index.html'
    context_object_name = 'stores'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search_query')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset