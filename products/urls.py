from django.urls import path
from .views import WriteOffView

urlpatterns = [
    path('write-off/', WriteOffView.as_view(), name='write-off'),
]