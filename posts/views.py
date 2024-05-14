from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Post, User, Group, Follow, Comment
from .forms import PostForm, CommentForm

User = get_user_model()

def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().order_by("-pub_date")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    context = {'group': group, 'page': page, 'form': form}
    return render(request, "group.html", context)

@login_required
def new_post(request):
    is_edit = False
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            cache.clear()
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    else:
        form = PostForm()
        
    return render(request, "new.html", {"form": form, "is_edit": is_edit})

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)

    post_list = posts.order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # Переменная в URL с номером запрошенной страницы.
    page = paginator.get_page(page_number)  # Получить записи с нужным смещением.

    form = CommentForm()

    followers_count = Follow.objects.filter(author=user).count()
    following_count = Follow.objects.filter(user=user).count()

    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=user).exists()
    else:
        following = False

    context = {
        'posts': posts,
        'user': user,
        'form': form,
        'page': page,
        'followers_count': followers_count,
        'following_count': following_count,
        'following': following,
    }

    return render(request, 'profile.html', context)

def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user)

    post = get_object_or_404(Post, pk=post_id, author__username=username)

    post.comment = Comment.objects.filter(post=post)

    form = CommentForm()

    followers_count = Follow.objects.filter(author=user).count()
    following_count = Follow.objects.filter(user=user).count()
    
    context = {
        'user': user,
        'posts': posts,
        'post': post,
        'form': form,
        'followers_count': followers_count,
        'following_count': following_count
    }
    
    return render(request, 'post.html', context)

@login_required
def post_edit(request, username, post_id):
    is_edit = True
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    
    if request.method == 'POST':
        if form.is_valid():
            cache.clear()
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)

    return render(
        request, 'new.html', {'form': form, 'post': post, "is_edit": is_edit},
    )

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            cache.clear()
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username=username, post_id=post_id)
    else:
        form = CommentForm()
    
    return render(request, 'comments.html', {'form': form, 'post': post})

@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    posts_sort = posts.order_by('-pub_date')
    paginator = Paginator(posts_sort, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        'page': page,
        'paginator': paginator,
        'form': form
    }
    return render(request, "follow.html", context)

@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author and not Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.create(user=user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if user != author and Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.filter(user=user, author=author).delete()
    return redirect('profile', username=username)