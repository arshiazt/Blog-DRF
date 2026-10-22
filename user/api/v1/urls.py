from django.urls import path
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('profile/me/',views.ProfileRetrieveUpdateAPIView.as_view(),name='profile-retriev-update'),
    path('links/me/',views.LinkListCreateAPIView.as_view(),name='my-links'),
    path('links/me/<int:pk>/',views.LinkRetrieveUpdateDestroyAPIView.as_view(),name='edit-my-links'),
    path('profile/<str:user_name>/',views.ProfileRetrieveAPIView.as_view(),name='public-profile'),
]