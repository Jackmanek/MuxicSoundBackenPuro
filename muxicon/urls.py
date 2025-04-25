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
from .views import buscar_canciones

urlpatterns = [
    path('register/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('user/', views.user_profile, name='user_profile'),
    path('songs/', views.SongListView.as_view(), name='song_list'),
    path('songs/add/', add_song, name='add_song'),
    path('songs/download/', download_mp3, name='download_mp3'),
    path('songs/delete/<int:song_id>/', eliminar_song, name='eliminar_song'),
    path('songs/search/', buscar_canciones, name='buscar_canciones'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('playlists/', views.obtener_playlists, name='obtener_playlists'),
    path('playlists/create/', views.crear_playlist, name='crear_playlist'),
    path('playlists/delete/<int:playlist_id>/', views.eliminar_playlist, name='eliminar_playlist'),
    path('playlists/<int:playlist_id>/songs/', views.obtener_canciones_playlist, name='obtener_canciones_playlist'),
    path('playlists/<int:playlist_id>/add-song/', views.añadir_cancion_a_playlist, name='añadir_cancion_a_playlist'),
    path('playlists/<int:playlist_id>/remove-song/', views.eliminar_cancion_de_playlist, name='eliminar_cancion_de_playlist'),
    path('playlists/<int:playlist_id>/reorder/', views.reordenar_playlist, name='reordenar_playlist'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
