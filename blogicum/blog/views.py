from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from .forms import PostForm, CommentForm
from .models import Category, Post, Comment, User


POSTS_ON_INDEX_PAGE = 10


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(
                reverse("blog:profile", args=[request.user.username])
            )
    else:
        form = PostForm()
    return render(request, "blog/create.html", {"form": form})


class ProfileView(ListView):
    template_name = "blog/profile.html"
    context_object_name = "posts"
    paginate_by = POSTS_ON_INDEX_PAGE
    slug_url_kwarg = "username"
    slug_field = "username"

    def get_queryset(self):
        self.user = get_object_or_404(
            User,
            username=self.kwargs.get(self.slug_url_kwarg),
        )
        return Post.objects.filter(author=self.user).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile_user"
    login_url = "/login/"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class IndexView(ListView):
    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = POSTS_ON_INDEX_PAGE

    def get_queryset(self):
        return (
            Post.published_posts.all()
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class CategoryView(ListView):
    template_name = "blog/category.html"
    context_object_name = "posts"
    paginate_by = POSTS_ON_INDEX_PAGE
    slug_url_kwarg = "slug"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs.get(self.slug_url_kwarg),
            is_published=True,
        )
        return Post.published_posts.filter(category=self.category).order_by(
            "-pub_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


def post_detail(request, pk):
    if request.user.is_authenticated:
        posts = Post.objects.filter(
            Q(is_published=True)
            | (Q(author=request.user) & Q(is_published=False))
        ).annotate(comment_count=Count("comments"))
    else:
        posts = Post.published_posts.all().annotate(
            comment_count=Count("comments")
        )

    post = get_object_or_404(posts, pk=pk)

    form = CommentForm()
    comments = post.comments.all()

    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, "blog/detail.html", context)


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect("blog:post_detail", pk=post.pk)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:post_detail", pk=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/create.html", {"form": form})


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs["post_id"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", args=[self.object.post.id])


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", args=[self.object.post.id])


class BaseDeleteView(UserPassesTestMixin, View):
    model = None
    template_name = None
    success_url_name = None

    def get_object(self, **kwargs):
        return get_object_or_404(self.model, pk=self.kwargs[self.key_name])

    def test_func(self):
        object = self.get_object()
        return self.request.user == object.author

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return render(
            request, self.template_name, {self.model.__name__.lower(): object}
        )

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        return self.get_success_url(object)

    def get_success_url(self, object):
        raise NotImplementedError

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        if request.user != object.author:
            raise PermissionDenied
        object.delete()
        success_url = self.get_success_url(object)
        return redirect(success_url)


class PostDeleteView(BaseDeleteView):
    model = Post
    template_name = "blog/create.html"
    success_url_name = "blog:profile"
    key_name = "post_id"

    def get_success_url(self, object):
        return redirect(
            reverse(
                self.success_url_name,
                kwargs={"username": object.author.username},
            )
        )


class CommentDeleteView(BaseDeleteView):
    model = Comment
    template_name = "blog/comment.html"
    success_url_name = "blog:post_detail"
    key_name = "comment_id"

    def get_success_url(self, object):
        return redirect(
            reverse(self.success_url_name, kwargs={"pk": object.post.pk})
        )
