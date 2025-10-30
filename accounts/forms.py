from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile


User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким e-mail уже зарегистрирован.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return cleaned

    def _make_unique_username(self, email: str) -> str:
        base = (email.split("@")[0] or "user").strip() or "user"
        cand = base
        i = 1
        while User.objects.filter(username=cand).exists():
            i += 1
            cand = f"{base}{i}"
        return cand

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower().strip()
        user.username = self._make_unique_username(user.email)  
        user.set_password(self.cleaned_data["password1"])

        if not getattr(user, "role", None):
            user.role = "STUDENT"
        if commit:
            user.save()
        return user
    



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'date_of_birth', 'phone']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }