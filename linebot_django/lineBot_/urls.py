from django.conf.urls import include, url
from . import views
# 用來串接callback主程式
urlpatterns = [
    url('^callback/', views.callback),
]

