from django.shortcuts import render, redirect
from .forms import SignupForm  # Import your SignupForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user to the database
            return redirect('success_url')  # Replace with your success URL
    else:
        form = SignupForm()
    return render(request, 'SignUpPage.html', {'form': form})
