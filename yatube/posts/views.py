from django.shortcuts import get_object_or_404, render, redirect
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm
from posts.utils import paginate
from django.contrib.auth.decorators import login_required

PAGE_FOR_LIST = 10
LETTERS_FOR_POST = 30


def index(request):
    post_list = Post.objects.all()
    page_obj = paginate(request, post_list, PAGE_FOR_LIST)
    context = {
        'page_obj': page_obj, }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    page_obj = paginate(request, posts, PAGE_FOR_LIST)
    context = {
        'group': group,
        'page_obj': page_obj, }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = 'Профайл пользователя'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count_posts = posts.count()
    page_obj = paginate(request, posts, PAGE_FOR_LIST)
    status_of_client = request.user.is_authenticated
    request_for_follow = status_of_client and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    context = {
        'following': request_for_follow,
        'author': author,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'title': title, }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    all_posts = post.author.posts
    count = all_posts.count()
    short_post = post.text[:LETTERS_FOR_POST]
    title = 'Пост'
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'form': form,
        'comments': comments,
        'post': post,
        'count': count,
        'short_post': short_post,
        'title': title, }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True, }
    return render(request, 'posts/edit_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    author_posts_following = Post.objects.filter(
        author__following__user=request.user)
    page_obj = paginate(request, author_posts_following, PAGE_FOR_LIST)
    context = {
        'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(
        user=request.user,
        author=author
    ).exists() and request.user != author:
        Follow.objects.create(
            user=request.user,
            author=get_object_or_404(User, username=username))
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)).exists()
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)).delete()
    return redirect('posts:profile', username)
