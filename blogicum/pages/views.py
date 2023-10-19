"""Модуль приложения Pages."""

from django.shortcuts import render
from django.views.generic import TemplateView


def page_not_found(request, exception):
    """Ошибка страница не найдена."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Ошибка csrf token."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Ошибка сервера."""
    return render(request, 'pages/500.html', status=500)


class AboutView(TemplateView):
    """Вывод страницы О Нас."""

    template_name = "pages/about.html"


class RulesView(TemplateView):
    """Вывод страницы Наши Правила."""

    template_name = "pages/rules.html"
