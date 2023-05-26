from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, CreateView, UpdateView
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views import View
from django.utils import timezone

POSTS_ON_INDEX_PAGE = 10


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.id])


class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'blog/profile.html'
    context_object_name = 'user'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = Post.objects.filter(author=self.object)
        paginator = Paginator(user_posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class EditProfileView(UpdateView):
    model = get_user_model()
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        return Post.published_posts.all()


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs.get(self.slug_url_kwarg), is_published=True)
        return Post.published_posts.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    queryset = Post.published_posts.all()

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.comment_count = post.comments.count()
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)
        return context


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.id])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.object.post.id])


class PostDeleteView(View):
    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if request.user != post.author:
            raise PermissionDenied
        return render(request, 'blog/index.html', {'post': post})

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if request.user != post.author:
            raise PermissionDenied
        post.delete()
        return redirect(reverse('blog:profile'))


class CommentDeleteView(UserPassesTestMixin, View):
    def test_func(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return self.request.user == comment.author

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return render(request, 'blog/comment.html', {'comment': comment})

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        comment.delete()
        return HttpResponseRedirect(reverse_lazy('blog:post_detail', kwargs={'pk': comment.post.id}))

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.author:
            raise PermissionDenied
        success_url = reverse_lazy('blog:post_detail', kwargs={'pk': comment.post.id})
        comment.delete()
        return HttpResponseRedirect(success_url)
