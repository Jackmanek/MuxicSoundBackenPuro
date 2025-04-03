from django.urls import path
from . import views
from django.urls import path
from .views import SongListView 
from .views import add_song
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import song_list
from django.urls import path
from .views import download_mp3, eliminar_song

urlpatterns = [
    path('register/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('songs/', views.SongListView.as_view(), name='song_list'),
    path('songs/add/', add_song, name='add_song'),
    path('songs/download/', download_mp3, name='download_mp3'),
    path('songs/delete/<int:song_id>/', eliminar_song, name='eliminar_song'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
