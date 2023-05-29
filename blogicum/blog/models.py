from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PostWithCommentsCountManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(comments_count=models.Count("comments"))
        )


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .select_related("category", "author", "location")
        )


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Добавлено"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Снимите галочку," " чтобы скрыть публикацию.",
        verbose_name="Опубликовано",
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    slug = models.SlugField(
        unique=True,
        help_text="Идентификатор страницы для URL;"
        " разрешены символы латиницы, цифры,"
        " дефис и подчёркивание.",
        verbose_name="Идентификатор",
    )
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        help_text="Если установить дату и время в будущем — "
        "можно делать отложенные публикации.",
        verbose_name="Дата и время публикации",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор публикации"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",
    )
    objects = models.Manager()
    published_posts = PublishedPostManager()

    image = models.ImageField(upload_to="post_images/", blank=True)

    @property
    def image_exists(self):
        return bool(self.image)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.text
