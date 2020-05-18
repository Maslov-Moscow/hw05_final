from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page


@cache_page(60 * 15)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            # Comment.objects.create(author=request.user, text=form.cleaned_data['text'], post=post)
            return redirect(f'/{username}/{post_id}')
            # return render(request, 'post.html', {'username': username, 'post_id': post_id})
        else:
            form = CommentForm(request.GET)
            author = get_object_or_404(User, username=username)
            post_count = Post.objects.filter(author=author).count()
            comments = Comment.objects.filter(post=post)
            return render(request, 'post.html', {"author": author, "post": post, "post_count": post_count,
                                                 "comments": comments, "form": form})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.image = form.cleaned_data['image']
            post.author = request.user
            post.save()
            return redirect('index')
        else:
            return render(request, 'new.html', {'form': form})
    else:
        form = PostForm(request.GET)
        return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    cur_user = get_object_or_404(User, username=username)  # новая хуйня
    post = get_object_or_404(Post, pk=post_id, author=cur_user)  # см.выше
    if request.user.username == username:  # Пользователь автор поста
        button_ed = "Редактировать запись"
        button_save = "Сохранить"
        if request.method == "POST":  # валидный пользователь отправляет
            form = PostForm(request.POST or None, files=request.FILES or None,
                            instance=post)  # было реквест пост ; or None, files=request.FILES or None
            if form.is_valid():
                form.text = form.cleaned_data['text']
                form.group = form.cleaned_data['group']
                form.image = form.cleaned_data['image']
                # Post.objects.filter(pk=post_id).update(text=text, group=group, image=image)

                form.save(commit=True)  # test!!!!
                return redirect(f'/{username}/{post_id}/')

            return render(request, "new.html", {"form": form, })  # ошибка в зап.

        post = get_object_or_404(Post, pk=post_id)  # ГЕТ запрос от атора
        form = PostForm(instance=post)  # было form = PostForm(instance=post)
        return render(request, "new.html",
                      {"form": form, "button_ed": button_ed, "button_save": button_save, "post": post})  # пост пост хз
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).all()
    post_count = Post.objects.filter(author=author).count()
    paginator = Paginator(posts, 10)
    post_author = request.user.username == username
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author).exists()
    else:
        following = None
    return render(request, "profile.html",
                  {"author": author, "page": page, "post_count": post_count, "paginator": paginator,
                   "post_author": post_author, "following":following})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)  # User.objects.get(username=username)
    post = get_object_or_404(Post, id=post_id)  # Post.objects.filter(id=post_id)
    post_count = Post.objects.filter(author=author).count()
    post_author = request.user.username == username
    comments = Comment.objects.filter(post=post).order_by("-created")
    form = CommentForm(request.POST)

    return render(request, "post.html",
                  {"author": author, "post": post, "post_count": post_count, "post_author": post_author,
                   "comments": comments, "form": form})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


# -------------------------ПОДПИСКИ----------------------------------------
@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    posts_f = Post.objects.filter(author__in=[follow.author for follow in follows]).order_by("-pub_date")
    paginator = Paginator(posts_f, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow_tr = Follow.objects.filter(user=request.user, author= author).exists()
    if author != request.user and not follow_tr:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.filter(user=user, author=author)
    if follow.exists():
        follow.delete()
    return redirect('profile', username=username)