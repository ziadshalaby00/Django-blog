import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views import View
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
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
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        
        for post in posts:
            post.likes_count = post.likes.filter(like=True).count()
            if(request.user.is_authenticated):
                post.is_liked = post.likes.filter(like=True, user=request.user).exists()
                
        tags = Tag.objects.all()
        return render(request, 'profilePage.html', {"tags": tags, "posts": posts})
    
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
    get_tag = request.GET.get('tag')

    posts = []
    if(get_tag):
        posts = Post.objects.filter(tag=get_tag).order_by('-created_at')

    else:
        posts = Post.objects.all().order_by('-created_at')
        
    tags = Tag.objects.all()
    
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    for post in posts:
        post.likes_count = post.likes.filter(like=True).count()
        if(request.user.is_authenticated):
            post.is_liked = post.likes.filter(like=True, user=request.user).exists()
    
    if get_tag: 
        posts.tag_id = get_tag
        
        tag_name = Tag.objects.filter(id=get_tag)
        if tag_name.exists(): posts.tag_name = tag_name.first()
        
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

def getComment(request):
    post_id = request.GET.get("post_id")
    if not post_id:
        return JsonResponse({"error": "post_id is required"}, status=400)
    comments = Comment.objects.filter(post=post_id).values(
        "id", "user__id", "user__username",
        "image", "content", "created_at").order_by("-created_at")
    return JsonResponse({
        "comments": list(comments),
        "current_user": request.user.id
    }, status=200)

@login_required(login_url='/login/')
def deletePost(request, id):
    post = Post.objects.filter(user=request.user, id=id)
    if post.exists():
        post.first().delete()
        
    return redirect(request.META.get('HTTP_REFERER', '/'))
    
@login_required(login_url='/login/')
def updatePost(request, id):
    if request.method == "POST":
        post = Post.objects.filter(user=request.user, id=id).first()
        tag = Tag.objects.filter(id=request.POST.get("tag")).first()
        title = request.POST.get("title")
        content = request.POST.get("content")
        image = request.FILES.get("image")

        if post:
            if tag: post.tag = tag
            if title: post.title = title
            if content: post.content = content
            if image: post.image = image
            post.save()
            
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='/login/')
def createPost(request):
    if request.method == "POST":
        tag = Tag.objects.filter(id=request.POST.get("tag")).first()
        title = request.POST.get("title")
        content = request.POST.get("content")
        image = request.FILES.get("image")

        if title and content:
            Post.objects.create(
                user=request.user,
                tag=tag,
                title=title,
                content=content,
                image=image,
            )
            
    return redirect('blog')

@login_required(login_url='/login/')
def createComment(request, id):
    user = request.user
    post = Post.objects.filter(id=id).first()
    if post:
        content = request.POST.get("content")
        image = request.FILES.get("image")
        
    if content:
        Comment.objects.create(
            user=user,
            post=post,
            content=content,
            image=image
        )
        return JsonResponse({}, status=200)
    
    return JsonResponse({}, status=400)

@login_required(login_url='/login/')
def deleteComment(request, id):
    comment = Comment.objects.filter(user=request.user, id=id).first()
    if comment:
        comment.delete()
        return JsonResponse({}, status=200)
    return JsonResponse({}, status=400)

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