from django import forms
from .models import Customer
from django.contrib.auth.hashers import make_password

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = ['username', 'email']

    def clean_password_confirm(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            raise forms.ValidationError("Passwords do not match")
        return self.cleaned_data['password_confirm']

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.password_hash = make_password(self.cleaned_data['password'])
        if commit:
            customer.save()
        return customer
