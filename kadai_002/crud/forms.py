from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='オプション',
        label='苗字'
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='オプション',
        label='名前'
    )
    email = forms.EmailField(
        max_length=254,
        help_text='必須 有効なメールアドレスを入力してください。',
        label='Eメールアドレス'
    )
    

    class Meta:
        model = User
        fields = ('last_name', 'first_name',  'email', 'username', 'password1', 'password2', )

class UserEditForm(UserCreationForm):
   email = forms.EmailField(label="Email", max_length=254, required=True)

   class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username'] 

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not email or not password:
            raise forms.ValidationError("Both email and password are required.")

        user = authenticate(username=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid email or password.")
        
        return self.cleaned_data
    
class RestaurantFilterForm(forms.Form):
    category = forms.CharField(max_length=100, required=False, label="カテゴリ")
    price_min = forms.DecimalField(
        max_digits=10, decimal_places=0, required=False, label="最小価格",
        widget=forms.NumberInput(attrs={'step': 1000})  # 1000円単位で増減
    )
    price_max = forms.DecimalField(
        max_digits=10, decimal_places=0, required=False, label="最大価格",
        widget=forms.NumberInput(attrs={'step': 1000})  # 1000円単位で増減
    )
    business_hours = forms.CharField(max_length=100, required=False, label="営業時間")
