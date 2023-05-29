from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import (
    CategoryView,
    IndexView,
    ProfileView,
    EditProfileView,
    PostDeleteView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView
)

app_name = 'blog'

urlpatterns = [
    path(
        '',
        IndexView.as_view(),
        name='index'
    ),
    path(
        'posts/<int:pk>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'category/<slug:slug>/',
        CategoryView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        ProfileView.as_view(),
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        EditProfileView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/create/',
        views.post_create,
        name='post_create'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.post_edit,
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/comment/',
        CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>/',
        CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete/',
        PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDeleteView.as_view(),
        name='delete_comment'
    ),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
