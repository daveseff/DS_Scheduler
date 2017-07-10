from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from console import views


favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    # Authentication stuff
    url(r'^accounts/login/$', auth_views.LoginView.as_view()),
    url(r'^auth/',         views.auth_view),
    url(r'^accounts/logout/',       views.logout),
    url(r'^iaccounts/nvalid/',      views.invalid_login),

    # App
    url(r'^admin/',                 admin.site.urls),
    url(r'^favicon\.ico$',          favicon_view),
    url(r'^$',                      views.index),
    url(r'^log',                    views.log),
    url(r'^render_status',          views.render_status),

]
