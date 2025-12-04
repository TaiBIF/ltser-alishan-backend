from django.db import models


class Introduction(models.Model):
    TYPE_CHOICES = (
        ("ecology", "生態觀測"),
        ("environment", "環境觀測"),
        ("ecological-economics", "生態經濟"),
        ("ecological-culture", "經濟與文化面向"),
    )

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    content = models.TextField()
    content_en = models.TextField()
    media = models.ImageField(upload_to="introductionImage/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_introduction"
        verbose_name = "Introduction"
        verbose_name_plural = "Introductions"

    def __str__(self):
        type_display = dict(self.TYPE_CHOICES).get(self.type, self.type)
        return f"{self.id} - {type_display} - {self.name}"


class CouEventType(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "dashboard_cou_event_type"
        verbose_name = "CouEventType"
        verbose_name_plural = "CouEventTypes"

    def __str__(self):
        return self.name


class CouEvent(models.Model):
    types = models.ManyToManyField(
        CouEventType,
        related_name="cou_event_list",
        blank=True,
    )
    content = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        db_table = "dashboard_cou_event"
        verbose_name = "CouEvent"
        verbose_name_plural = "CouEvents"

    def __str__(self):
        type_names = ", ".join(t.name for t in self.types.all())
        return f"{self.date} - {type_names} - {self.location}"


class CouEventImage(models.Model):
    event = models.ForeignKey(
        CouEvent,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to="couEventImage/",
    )

    class Meta:
        db_table = "dashboard_cou_event_image"
        verbose_name = "CouEventImage"
        verbose_name_plural = "CouEventsImages"

    def __str__(self):
        return f"Image for Event {self.event_id}"


class NewsType(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "dashboard_news_type"
        verbose_name = "NewsType"
        verbose_name_plural = "NewsTypes"

    def __str__(self):
        return self.name


class News(models.Model):
    types = models.ManyToManyField(
        NewsType,
        related_name="news_list",
        blank=True,
    )
    title = models.TextField()
    content = models.TextField()
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        db_table = "dashboard_news"
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        type_names = ", ".join(t.name for t in self.types.all())
        return f"{self.date} - {type_names} - {self.title}"


class NewsCoverImage(models.Model):
    news_cover = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="cover_image",
    )
    image = models.ImageField(
        upload_to="newsCoverImage/",
    )

    class Meta:
        db_table = "dashboard_news_cover_image"
        verbose_name = "NewsCoverImage"
        verbose_name_plural = "NewsCoverImages"

    def __str__(self):
        return f"Cover Image for News {self.news_cover_id}"


class NewsImage(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to="newsImage/",
    )

    class Meta:
        db_table = "dashboard_news_image"
        verbose_name = "NewsImage"
        verbose_name_plural = "NewsImages"

    def __str__(self):
        return f"Cover Image for News {self.news_id}"


class FaqType(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "dashboard_faq_type"
        verbose_name = "FaqType"
        verbose_name_plural = "FaqTypes"

    def __str__(self):
        return self.name


class Faq(models.Model):
    types = models.ManyToManyField(
        FaqType,
        related_name="faq_list",
        blank=True,
    )
    question = models.TextField()
    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_faq"
        verbose_name = "Faq"
        verbose_name_plural = "Faqs"

    def __str__(self):
        type_names = ", ".join(t.name for t in self.types.all())
        return f"{type_names} - {self.question}"


class LiteratureType(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "dashboard_literature_type"
        verbose_name = "LiteratureType"
        verbose_name_plural = "LiteratureTypes"

    def __str__(self):
        return self.name


class Literature(models.Model):
    types = models.ManyToManyField(
        LiteratureType,
        related_name="literature_list",
        blank=True,
    )
    title = models.TextField()
    date = models.DateField()
    author = models.TextField()
    affiliation = models.TextField()
    link = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_literature"
        verbose_name = "Literature"
        verbose_name_plural = "Literatures"

    def __str__(self):
        type_names = ", ".join(t.name for t in self.types.all())
        return f"{type_names} - {self.title} - {self.date}"
