"""Приложение Blog."""
from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Class Blog."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "Блог"
