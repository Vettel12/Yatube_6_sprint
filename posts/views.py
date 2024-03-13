from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


from .models import Post, User, Group
from .forms import PostForm

def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})

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