"""Модуль с формами для кастомного пользователя."""
import unicodedata

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.crypto import get_random_string

User = get_user_model()


class UsernameField(forms.CharField):

    def to_python(self, value):
        value = super().to_python(value)
        return None if value is None else unicodedata.normalize("NFKC", value)


class UserAdminForm(UserChangeForm):

    username = UsernameField(label="Ник", required=False)
    password = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:

        model = User
        fields = "__all__"


class UserAdminCreationForm(UserCreationForm):

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:

        model = User
        fields = ("username", "email", "first_name", "last_name",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(get_random_string(8))
        if commit:
            user.save()
        return user
