from django.db import models

class Caretaker(models.Model):
  full_name = models.CharField(max_length=255, null=False)
  email = models.CharField(max_length=255, unique=True)
  password = models.CharField(max_length=255)  # Replace with hashed password field
  # Add other caretaker details (e.g., phone number)
  created_at = models.DateTimeField(auto_now_add=True)
