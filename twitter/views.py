from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import Profile, Tweet
from .forms import TweetForm, SignUpForm, ProfilePicForm

def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, ("Seu Tweet Foi Publicado!"))
                return redirect('home')
            
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets":tweets, "form":form})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets":tweets})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles": profiles})
    else:
        messages.success(request, ("Você precisa estar logado para ver esta página..."))
        return redirect('home')

def unfollow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.remove(profile)
		# Save our profile
		request.user.profile.save()

		# Return message
		messages.success(request, (f"Você deixou de seguir com sucesso {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("Você precisa estar logado para visualizar esta página..."))
		return redirect('home')

def follow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.add(profile)
		# Save our profile
		request.user.profile.save()

		# Return message
		messages.success(request, (f"Você seguiu com sucesso {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("Você precisa estar logado para visualizar esta página..."))
		return redirect('home')

def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        tweets = Tweet.objects.filter(user_id=pk).order_by("-created_at")

        #Post form logic
        if request.method == "POST":
            # Get current user
            current_user_profile = request.user.profile
            # Get form data
            action = request.POST['follow']
            # Decide to follow or unfollow
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            # Save de profile
            current_user_profile.save()
            
        return render(request, "profile.html", {"profile": profile, "tweets": tweets})
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página..."))
        return redirect('home')

def followers(request, pk):
	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = Profile.objects.get(user_id=pk)
			return render(request, 'followers.html', {"profiles":profiles})
		else:
			messages.success(request, ("Essa não é a sua página de perfil..."))
			return redirect('home')	
	else:
		messages.success(request, ("Você deve estar logado para ver esta página..."))
		return redirect('home')

def follows(request, pk):
	if request.user.is_authenticated:
		if request.user.id == pk:
			profiles = Profile.objects.get(user_id=pk)
			return render(request, 'follows.html', {"profiles":profiles})
		else:
			messages.success(request, ("Essa não é a sua página de perfil..."))
			return redirect('home')	
	else:
		messages.success(request, ("Você deve estar logado para ver esta página..."))
		return redirect('home')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("Você foi logado! Comece a twittar!"))
            return redirect('home')
        else:
            messages.success(request, ("Houve um erro ao fazer login. Por favor, tente novamente..."))
            return redirect('login')
    else:
        return render(request, "login.html", {})


def logout_user(request):
	logout(request)
	messages.success(request, ("Você foi desconectado. Lamentamos vê-lo partir..."))
	return redirect('home')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ("Você se registrou com sucesso! Bem-vindo!"))
			return redirect('home')

	return render(request, "register.html", {'form':form})

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        # Get Forms
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            login(request, current_user)
            messages.success(request, ("Seu perfil foi atualizado!"))
            return redirect('home')

        return render(request, "update_user.html", {'user_form':user_form, 'profile_form':profile_form})
    else:
        messages.success(request, ("Você deve estar logado para ver esta página..."))
        return redirect('home')


def tweet_like(request, pk):
	if request.user.is_authenticated:
		tweet = get_object_or_404(Tweet, id=pk)
		if tweet.likes.filter(id=request.user.id):
			tweet.likes.remove(request.user)
		else:
			tweet.likes.add(request.user)

		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("Você deve estar logado para ver essa página..."))
		return redirect('home')

def delete_tweet(request, pk):
	if request.user.is_authenticated:
		tweet = get_object_or_404(Tweet, id=pk)
		# Check to see if you own the tweet
		if request.user.username == tweet.user.username:
			# Delete The tweet
			tweet.delete()

			messages.success(request, ("O tweet foi deletado!"))
			return redirect(request.META.get("HTTP_REFERER"))	
		else:
			messages.success(request, ("Você não possui esse tweet!!"))
			return redirect('home')

	else:
		messages.success(request, ("Por favor, faça login para continuar..."))
		return redirect(request.META.get("HTTP_REFERER"))
	
def edit_tweet(request,pk):
	if request.user.is_authenticated:
		# Grab The tweet!
		tweet = get_object_or_404(Tweet, id=pk)

		# Check to see if you own the tweet
		if request.user.username == tweet.user.username:

			form = TweetForm(request.POST or None, instance=tweet)
			if request.method == "POST":
				if form.is_valid():
					tweet = form.save(commit=False)
					tweet.user = request.user
					tweet.save()
					messages.success(request, ("Seu tweet foi atualizado!"))
					return redirect('home')
			else:
				return render(request, "edit_tweet.html", {'form':form, 'tweet':tweet})

		else:
			messages.success(request, ("Você não possui esse tweet!!"))
			return redirect('home')

	else:
		messages.success(request, ("Por favor, faça login para continuar..."))
		return redirect('home')