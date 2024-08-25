from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.models import User  # For user creation (if applicable)

class SignupForm(forms.Form):
    username = forms.CharField(max_length=255, required=True, validators=[
        RegexValidator(r'^[^\d]', 'Username cannot start with a number')
    ])
    email = forms.CharField(max_length=255, required=True, validators=[EmailValidator()])
    password = forms.CharField(widget=forms.PasswordInput(), required=True, validators=[
        RegexValidator(r'[^\w\s]', 'Password must contain a special character'),
        RegexValidator(r'[A-Z]', 'Password must contain an uppercase letter'),
        RegexValidator(r'\d', 'Password must contain a number')
    ])
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check for duplicate email in the database
        if User.objects.filter(email=email).exists():  # Check for existing users (if using Django auth)
            raise forms.ValidationError('This email address is already in use.')
        # Check for duplicate email in patients table (if not using Django auth)
        try:
            from .models import Patient  # Import your Patient model (replace with your model name)
            if Patient.objects.filter(email=email).exists():
                raise forms.ValidationError('This email address is already in use.')
        except (ModuleNotFoundError, DoesNotExist):
            pass  # Handle potential model import or object retrieval errors
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = None  # Initialize user variable
        if User is not None and self.cleaned_data:  # Check if using Django's built-in user model
            username = self.cleaned_data['username']
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            user = User.objects.create_user(username, email, password)  # Create user (if applicable)
            # ... (code for handling user creation if applicable) ...
        else:
            # Implement database insertion if not using Django's auth
            try:
                from .models import Caretaker  # Import your Caretaker model (replace with your model name)
                full_name = self.cleaned_data['username']  # Assuming username represents full name
                email = self.cleaned_data['email']
                password = self.cleaned_data['password']

                # Hash the password before storing
                from django.contrib.auth.hashers import make_password
                hashed_password = make_password(password)

                caretaker = Caretaker.objects.create(full_name=full_name, email=email, password=hashed_password)  # Create caretaker record with hashed password
                user = caretaker  # Set user variable to the created caretaker object (if needed)
            except (ModuleNotFoundError, DoesNotExist):
                pass  # Handle potential model import or object creation errors
        return user
