from django.views import generic
from django.shortcuts import render


class AboutView(generic.TemplateView):
    template_name = 'pages/about.html'


class RulesView(generic.TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason='', exception=None):
    return render(request, 'pages/403csrf.html', status=403)


def custom_error(request):
    return render(request, 'pages/500.html', status=500)
