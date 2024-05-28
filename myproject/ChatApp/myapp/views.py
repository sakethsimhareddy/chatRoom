from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import auth
from django.http import HttpResponse, JsonResponse
from .models import Room, Message
import random
import string

# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'You are now registered and can log in')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'register.html')

def home(request):
    if request.method == 'POST':
        while True:
            characters = string.ascii_letters + string.digits
            random_string = ''.join(random.choice(characters) for _ in range(5))
            if not Room.objects.filter(name=random_string).exists():
                break
        room = Room.objects.create(name=random_string)
        room.save()
        username = request.user.username
        return redirect(f'/{random_string}/?username={username}')
    return render(request, 'home.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def join(request):
    if request.method == 'POST':
        room_name = request.POST.get('room')
        if Room.objects.filter(name=room_name).exists():
            username = request.user.username
            return redirect(f'/{room_name}/?username={username}')
        else:
            messages.error(request, 'Room does not exist')
    return render(request, 'join.html')


def room(request, room):
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })


def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})