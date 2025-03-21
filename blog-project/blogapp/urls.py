"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import *

urlpatterns = [
    path("login/", loginView.as_view(), name="login"),
    path("signup/", signupView.as_view(), name="signup"),
    
    path("userInfo/", userInfo.as_view(), name="userInfo"),
    path("logout/", logoutView, name="logout"),
    
    path("Blog/", BlogView, name="blog"),
    
    path("deletePost/<int:id>", deletePost, name="deletePost"),
    path("updatePost/<int:id>", updatePost, name="updatePost"),
    path("updatePost/", updatePost, name="updatePost"),
    path("createPost/", createPost, name="createPost"),
    
    path("createComment/<int:id>", createComment, name="createComment"),
    path("createComment/", createComment, name="createComment"),
    
    path("deleteComment/<int:id>/", deleteComment, name="deleteComment"),
    path("deleteComment/", deleteComment, name="deleteComment"),
    
    path("likes/", likes, name="likes"),
    path("getComment/", getComment, name="getComment"),
    
    # path("createTestPost/", createTestPost),
]
