import os
import django
import random
import requests
from django.core.files.base import ContentFile

# ⚠️ استبدل 'myproject' باسم مجلد إعدادات مشروعك الرئيسي
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from faker import Faker

# ⚠️ استبدل 'myapp' باسم التطبيق الخاص بك
from blogapp.models import UserProfile, Tag, Post, Likes, Comment

fake = Faker('en_US')

def get_dummy_image(width=600, height=400):
    """جلب صورة وهمية عبر الإنترنت"""
    try:
        url = f"https://picsum.photos/{width}/{height}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            filename = f"dummy_{random.randint(1000, 9999)}.jpg"
            return filename, ContentFile(response.content)
    except Exception as e:
        print(f"⚠️ Warning: Could not download image: {e}")
    return None, None

def run_seed():
    admin_username = 'admin'

    # 1. جلب حساب الأدمن الموّجد
    try:
        admin_user = User.objects.get(username=admin_username)
        print(f"✅ Found admin user: '{admin_username}'")
    except User.DoesNotExist:
        print(f"❌ Error: User '{admin_username}' does not exist! Please create the admin user first using 'python manage.py createsuperuser'.")
        return

    # 2. إضافة/تحديث الصورة الشخصية للأدمن إذا لم تكن موجودة
    profile, created = UserProfile.objects.get_or_create(user=admin_user)
    if not profile.profile_image:
        img_name, img_content = get_dummy_image(200, 200)
        if img_content:
            profile.profile_image.save(img_name, img_content, save=True)
            print("✅ Created profile image for admin.")

    # 3. إنشاء التاجز (Tags)
    tag_names = ['Technology', 'Programming', 'AI & Data', 'Design', 'Lifestyle', 'Health', 'Travel', 'Business']
    tag_objs = []
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name)
        tag_objs.append(tag)
    print(f"✅ Created/Loaded {len(tag_objs)} tags.")

    # 4. إنشاء المنشورات باسم الأدمن فقط (Posts)
    posts = []
    num_posts = 10  # عدد المنشورات المراد إنشاؤها
    for i in range(num_posts):
        post = Post(
            user=admin_user,  # ربط المنشور بالأدمن فقط
            tag=random.choice(tag_objs),
            title=fake.sentence(nb_words=6).rstrip('.'),
            content=fake.paragraph(nb_sentences=6)
        )
        # إرفاق صورة للمنشور
        img_name, img_content = get_dummy_image(800, 500)
        if img_content:
            post.image.save(img_name, img_content, save=False)
        post.save()
        posts.append(post)
    print(f"✅ Created {len(posts)} posts for user '{admin_username}'.")

    # 5. إنشاء الإعجابات باسم الأدمن (Likes)
    total_likes = 0
    for post in posts:
        Likes.objects.create(
            user=admin_user,
            post=post,
            like=True
        )
        total_likes += 1
    print(f"✅ Created {total_likes} likes from '{admin_username}'.")

    # 6. إنشاء تعليقات باسم الأدمن (Comments)
    total_comments = 0
    for post in posts:
        for _ in range(random.randint(1, 3)):  # 1 إلى 3 تعليقات لكل منشور
            comment = Comment(
                post=post,
                user=admin_user,  # التعليق باسم الأدمن
                content=fake.paragraph(nb_sentences=2)
            )
            # إضافة صورة وهمية لبعض التعليقات عشوائياً
            if random.choice([True, False]):
                img_name, img_content = get_dummy_image(400, 300)
                if img_content:
                    comment.image.save(img_name, img_content, save=False)
            comment.save()
            total_comments += 1
    print(f"✅ Created {total_comments} comments from '{admin_username}'.")

    print("\n🎉 Seeding completed successfully for user 'admin'!")

if __name__ == '__main__':
    run_seed()