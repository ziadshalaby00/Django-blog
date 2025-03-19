import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import View
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required

# creating a form  

class signupView(View):
    def get(self, request):
        return render(request, 'SignupPage.html')
    
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        profile_image = request.FILES.get("profile_image")
        
        if User.objects.filter(username=username).exists():
            return render(request, 'SignupPage.html', {"error": "This username is already exist"})
        
        user = User.objects.create_user(username=username, password=password)
        if profile_image:
            UserProfile.objects.create(user=user, profile_image=profile_image)
        return redirect('login')

class loginView(View):
    def get(self, request):
        return render(request, 'LoginPage.html')

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog')
        
        return render(request, 'LoginPage.html', {"error": "Username or Password is invalid"})
    

class userInfo(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def get(self, request):
        return render(request, "profilePage.html")
    
    def post(self, request):
        user = User.objects.get(id=request.user.id)
        old_profile_image = UserProfile.objects.filter(user=user).first()
        
        username = request.POST.get("username")
        profile_image = request.FILES.get("profile_image")
        
        if old_profile_image:
            profile_image = profile_image or old_profile_image.profile_image
            old_profile_image.profile_image = profile_image
            old_profile_image.save()
            
        elif profile_image:
            UserProfile.objects.create(user=user, profile_image=profile_image)
        
        
        user.username = username if username else user.username
        user.save()
        return redirect('userInfo')

    def delete(self, request):
        request.user.delete()
    
def BlogView(request):
    tags = Tag.objects.all()
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        post.likes_count = post.likes.filter(like=True).count()
        if(request.user.is_authenticated):
            post.is_liked = post.likes.filter(like=True, user=request.user).exists()
            
    return render(request, 'BlogPage.html', {"tags": tags, "posts": posts})

@login_required(login_url='/login/')
def likes(request):
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post = Post.objects.filter(id=post_id)
        user = request.user
        if post.exists():
            post=post.first()
            like_geted, created = Likes.objects.get_or_create(user=user, post=post)
            like_geted.like = not like_geted.like
            like_geted.save()
            return JsonResponse({
                "message": "success",
                "likes_count": post.likes.filter(like=True).count(),
                "is_liked": post.likes.filter(like=True, user=request.user).exists(),
                }, status=200)
        else:
            return JsonResponse({"message": "invalid 1"}, status=400) 
    else:
        return JsonResponse({"message": "invalid 2"}, status=400)
        

def logoutView(request):
    logout(request)
    return redirect('login')


##################### Tags #####################
hashtags = [
    "sports 🏆", "run 🏃‍♂️", "basketball 🏀", "football ⚽", "motivation 🔥",
    "workout 🏃", "gym 💪", "fitness 🏋️", "machinelearning 🧠", "cybersecurity 🔐",
    "python 🐍", "javascript 🟨", "webdesign 🎨", "developer 🏗", "coding 🧑‍💻",
    "AI 🤖", "programming 💻", "tech 🚀", "happy 😊", "art 🎨", "nature 🍃",
    "photography 📸", "picoftheday 🖼", "beautiful 🌸", "photooftheday 📷",
    "fashion 👗", "instagood 📸", "love ❤️"
]
##################### Tags #####################

##################### test functions #####################

# def createTestUser(request):
#     User.objects.create(username="test_user", password="test_user")
#     return HttpResponse("Done")

# def createTestTags(request):
#     for item in hashtags:
#         Tag.objects.create(name=item)
#     return HttpResponse("Done")

# def createTestPost(request):
#     for tag in Tag.objects.all():
#         for i in range(3):
#             Post.objects.create(user=User.objects.get(username="test_user"), 
#             tag=tag, 
#             title=f"test {i} for tag {tag.name}", 
#             content='''test test test test test test test test test test test 
#             test test test test test test test test test test''', likes='99',
#             image="blog_images/44776 - Copy.jpg")
#     return HttpResponse("Done")

# def createTestComments(request):
#     for post in Post.objects.all():
#         for i in range(5):
#             if i <= 2:
#                 Comment.objects.create(user=User.objects.get(username="test_user"), 
#                 post=post, 
#                 content=f'''{i} coment test for post {post.title} coment test coment test coment test coment test coment test''')
#             else:
#                 Comment.objects.create(user=User.objects.get(username="test_user"), 
#                 post=post, 
#                 content=f'''{i} coment test for post {post.title} coment test coment test coment test coment test coment test''',
#                 image="blog_images/cropped-1280-1024-737474.png")
#     return HttpResponse("Done")

# def createTestLikes(request):
#     for post in Post.objects.all():
#         Likes.objects.create(user=User.objects.get(username="test_user"), post = post, like=True)
#     return HttpResponse("Done")

##################### test functions #####################