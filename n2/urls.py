from django.conf.urls import include, url
from .views import n2Request
urlpatterns = [
    url(r'^v1/ubike-station/taipei/?$', n2Request.as_view()),
]
