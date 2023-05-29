from django.utils import timezone
from .models import Post


def get_posts_for_year(year):
    """
    Получает все посты для конкретного года.
    """
    posts = Post.published_posts.filter(pub_date__year=year)
    return posts


def get_days_until_publication(post):
    """
    Возвращает количество дней до публикации поста.
    Если время и день публикации наступило, то возвращает 0.
    """
    now = timezone.now()

    if post.pub_date > now:
        delta = post.pub_date - now
        return delta
    return 0
