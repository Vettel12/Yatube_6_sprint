from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator


from .models import Post, User, Group, FollowerRelation
from .forms import PostForm

User = get_user_model()

def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    try:
        group = get_object_or_404(Group, slug=slug)
        posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    except Http404:
        group = None
        posts = []

    return render(request, "group.html", {"group": group, "posts": posts})

@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        group = form.cleaned_data.get("group")
        text = form.cleaned_data.get("text")
        post = Post(group=group, text=text, author=request.user)
        post.save()
        return redirect("index")
    else:
        return render(request, "new.html", {"form": form})

@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user)

    post_list = posts.order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # Переменная в URL с номером запрошенной страницы.
    page = paginator.get_page(page_number)  # Получить записи с нужным смещением.

    is_author = False
    if request.user == user:
        is_author = True

    total_posts = posts.count()  # Получить общее количество записей

    user_is_logged_in = False
    if request.user.is_authenticated:
        user_is_logged_in = True

    is_following = FollowerRelation.is_following(request.user, user)

    followers_count = FollowerRelation.objects.filter(following=user).count()
    following_count = FollowerRelation.objects.filter(follower=user).count()

    context = {
        'is_following': is_following,
        'user_is_logged_in': user_is_logged_in,
        'user': user,
        'is_author': is_author,
        'posts': page,
        'paginator': paginator,
        'total_posts': total_posts,
        'followers_count': followers_count,
        'following_count': following_count
    }

    return render(request, 'profile.html', context)

def follow_unfollow(request):
    if request.method == 'POST' and request.user.is_authenticated:
        following_user_id = request.POST.get('following_user_id')  # Получаем ID пользователя, на которого пользователь хочет подписаться или отписаться
        following_user = User.objects.get(id=following_user_id)

        # Проверяем, подписан ли пользователь уже на этого пользователя
        if FollowerRelation.is_following(request.user, following_user):
            # Если да, то отписываемся
            FollowerRelation.objects.filter(follower=request.user, following=following_user).delete()
        else:
            # Если нет, то подписываемся
            FollowerRelation.objects.create(follower=request.user, following=following_user)

    return redirect('profile', username=following_user.username)

def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user)
    post_list = posts.order_by('-pub_date')
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # Переменная в URL с номером запрошенной страницы.
    page = paginator.get_page(page_number)  # Получить записи с нужным смещением.
    is_author = False
    if request.user == user:
        is_author = True
    total_posts = posts.count()  # Получить общее количество записей
    user_is_logged_in = False
    if request.user.is_authenticated:
        user_is_logged_in = True

    is_following = FollowerRelation.is_following(request.user, user)

    followers_count = FollowerRelation.objects.filter(following=user).count()
    following_count = FollowerRelation.objects.filter(follower=user).count()

    post = get_object_or_404(Post, pk=post_id, author__username=username)

    context = {
        'is_following': is_following,
        'user_is_logged_in': user_is_logged_in,
        'user': user,
        'is_author': is_author,
        'posts': page,
        'paginator': paginator,
        'total_posts': total_posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'post': post,
    }
    return render(request, 'post.html', context)

@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)

    # Проверяем, что текущий пользователь является автором записи
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    
    return render(request, 'post_new.html', {'form': form, 'post': post})