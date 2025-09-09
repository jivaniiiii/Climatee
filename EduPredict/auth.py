from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from educationmodel.models import Signup
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Login View
def loginPage(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

# Signup View
def signupPageinserted(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        if Signup.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = Signup.objects.create(name=name, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully!")
            return render( request, 'login.html')



def loginpage(request) :
    if request.method == 'POST' : 
        email = request.POST['email']
        password = request.POST['password']
        checkdata = Signup.objects.get(email= email ,password = password).first()
    if checkdata :
          request.session["getname"] = checkdata.name
          request.session["getid"] = checkdata.id
          return render(request , 'home.html')
    else :
          messages.error(request, 'Invalid Credential')
          return render(request , 'login.html')

# Home View
def homePage(request) : 
    if request.session.get('getname') == '' : 
        return render(request, 'login.html')
    else :
     return render(request , 'home.html')

# About View
def aboutPage(request) : 
    return render(request , 'about.html')

# Contact View
def contactPage(request) : 
    return render(request , 'contact.html')

# Forgot Password View
def forgotPasswordPage(request) : 
    return render(request , 'forgot-password.html')


def SignupPage(request) : 
    return render(request , 'signup.html')