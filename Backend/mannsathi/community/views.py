from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm
from notifications.utils import notify_new_comment

@login_required
def community_feed(request):
    category = request.GET.get('category', '')

    posts = Post.objects.all()

    if category:
        posts = posts.filter(category=category)

    return render(request, 'community/feed.html', {
        'posts':    posts,
        'category': category,
        'categories': Post.CATEGORY_CHOICES,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post      = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post shared with the community.")
            return redirect('community_feed')
    else:
        form = PostForm()

    return render(request, 'community/create_post.html', {'form': form})


@login_required
def post_detail(request, pk):
    post     = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment      = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            notify_new_comment(comment)
            messages.success(request, "Comment added.")
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()

    # Check if current user liked this post
    user_liked = request.user in post.likes.all()

    return render(request, 'community/post_detail.html', {
        'post':      post,
        'comments':  comments,
        'form':      form,
        'user_liked': user_liked,
    })


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('post_detail', pk=pk)


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
    return redirect('community_feed')