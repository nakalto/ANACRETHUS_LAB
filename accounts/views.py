
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def signup(request):
    # for post request process the form 
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            form.save()
            # Redirect to login page after successful signup
            return redirect('accounts:login')
    else:
        # For GET requests, show an empty form
        form = UserCreationForm()
    # Render the signup template with the form
    return render(request, 'accounts/signup.html', {'form': form})



