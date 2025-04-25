from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Song, Playlist, PlaylistSong
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .serializers import SongSerializer
import os
import re
import unicodedata
from django.conf import settings
from youtube_dl import YoutubeDL
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from pytube import YouTube
from moviepy.editor import *
import yt_dlp
from yt_dlp import YoutubeDL
from .serializers import UserSerializer
from django.db.models import Q
from .utils import get_audio_duration

@api_view(['GET'])
def inicio(request):
    songs = Song.objects.all()
    song_data = [{"title": song.title, "artist": song.artist, "url": song.url} for song in songs]
    return Response(song_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def registro(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    else:
        formatted_errors = {
        field: ' '.join(errors) for field, errors in serializer.errors.items()
        }
        return Response({"errors": formatted_errors}, status=status.HTTP_400_BAD_REQUEST)
            
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token = RefreshToken.for_user(user)
        return Response({"access": str(token.access_token), "refresh": str(token)}, status=status.HTTP_200_OK)
    return Response({"message": "Nombre de Usuario o contraseña no validos"}, status=status.HTTP_400_BAD_REQUEST)

class SongListView(APIView):
    permission_classes = [IsAuthenticated]  # Solo permite acceso a usuarios autenticados

    def get(self, request):
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def song_list(request):
    return JsonResponse({"message": "Lista de canciones"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_song(request):
    serializer = SongSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # Asigna la canción al usuario autenticado
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_mp3(request):
    youtube_url = request.data.get('youtube_url')  # Cambiado para API

    if not youtube_url:
        return Response({"error": "Debes proporcionar una URL de YouTube."}, status=status.HTTP_400_BAD_REQUEST)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': '/usr/local/bin/ffmpeg',
        'outtmpl': os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.%(ext)s'),
        'verbose': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        title = info.get('title', 'Unknown Title')
        artist = info.get('artist', info.get('uploader', 'Unknown Artist'))

        title = unicodedata.normalize('NFKD', title)
        artist = unicodedata.normalize('NFKD', artist)

        safe_title = re.sub(r'[^\w\s\-ñÑáéíóúÁÉÍÓÚ\'´]', '', title).strip().replace(' ', '_')
        safe_artist = re.sub(r'[^\w\s\-ñÑáéíóúÁÉÍÓÚ\'´]', '', artist).strip().replace(' ', '_')
        safe_title = f"r_-_{safe_title}"

        safe_title = safe_title.encode('utf-8', errors='ignore').decode('utf-8')
        safe_artist = safe_artist.encode('utf-8', errors='ignore').decode('utf-8')

        def get_next_track_number(user):
            last_songs = Song.objects.filter(user=user).order_by('-id')[:10]
            for song in last_songs:
                match = re.match(r'Track(\d+)', song.title)
                if match:
                    return int(match.group(1)) + 1
            return 1
        new_track_number = get_next_track_number(request.user)
        """
        last_song = Song.objects.filter(user=request.user).order_by('-id').first()
        new_track_number = (int(re.match(r'Track(\d+)', last_song.title).group(1)) + 1) if last_song else 1
        """
        
        mp3_filename = f"Track{new_track_number}_{safe_artist}_{safe_title}.mp3"
        song_url = os.path.join('songs', mp3_filename)

        original_file_path = os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.mp3')
        new_file_path = os.path.join(settings.MEDIA_ROOT, song_url)
        
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        if os.path.exists(original_file_path):
            os.rename(original_file_path, new_file_path)
        else:
            return Response({"error": "El archivo no se descargó correctamente."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not os.path.exists(new_file_path):
            return Response({"error": "Archivo MP3 no encontrado después del rename."}, status=500)
        duration = get_audio_duration(new_file_path)
        song = Song(title=mp3_filename, artist=artist, file=song_url, user=request.user, url=title, download_date=timezone.now(), duration=duration)
        song.save()

        return Response({"message": "Canción descargada correctamente.", "song":  SongSerializer(song).data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_song(request, song_id):
    try:
        song = Song.objects.get(id=song_id, user=request.user)  # Asegurar que solo el dueño puede eliminar
        song.delete()
        return Response({"message": "Canción eliminada correctamente."}, status=status.HTTP_200_OK)
    except Song.DoesNotExist:
        return Response({"error": "Canción no encontrada o no tienes permiso para eliminarla."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def buscar_canciones(request):
    query = request.GET.get('q', '')
    try:
        if query:
            canciones = Song.objects.filter(
                Q(title__icontains=query) |
                Q(artist__icontains=query) |
                Q(url__icontains=query) |
                Q(file__icontains=query)
            )
        else:
            canciones = Song.objects.all()

        serializer = SongSerializer(canciones, many=True)
        return Response(serializer.data)

    except Exception as e:
        print("ERROR EN BUSQUEDA:", str(e))
        return Response({'error': 'Ocurrió un error interno'}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_playlist(request):
    """Crear una nueva playlist"""
    name = request.data.get('name')
    if not name:
        return Response({'error': 'El nombre es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    playlist = Playlist.objects.create(name=name, user=request.user)
    return Response({'id': playlist.id, 'name': playlist.name}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_playlist(request, playlist_id):
    """Eliminar una playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        playlist.delete()
        return Response({'message': 'Playlist eliminada correctamente'}, status=status.HTTP_200_OK)
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def añadir_cancion_a_playlist(request, playlist_id):
    """Añadir una canción a una playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        song_id = request.data.get('song_id')
        
        if not song_id:
            return Response({'error': 'ID de canción requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            song = Song.objects.get(id=song_id)
            
            # Verificar si la canción ya está en la playlist
            if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
                return Response({'error': 'La canción ya está en la playlist'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el orden más alto actual y añadir la canción al final
            last_order = PlaylistSong.objects.filter(playlist=playlist).order_by('-order').first()
            new_order = 1 if not last_order else last_order.order + 1
            
            playlist_song = PlaylistSong.objects.create(playlist=playlist, song=song, order=new_order)
            
            return Response({
                'message': 'Canción añadida correctamente',
                'song': {
                    'id': song.id,
                    'title': song.title,
                    'artist': song.artist,
                    'order': playlist_song.order
                }
            }, status=status.HTTP_201_CREATED)
            
        except Song.DoesNotExist:
            return Response({'error': 'Canción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def eliminar_cancion_de_playlist(request, playlist_id):
    """Eliminar una canción de una playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        song_id = request.data.get('song_id')
        
        if not song_id:
            return Response({'error': 'ID de canción requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            song = Song.objects.get(id=song_id)
            
            try:
                playlist_song = PlaylistSong.objects.get(playlist=playlist, song=song)
                playlist_song.delete()
                
                # Reordenar las canciones restantes
                remaining_songs = PlaylistSong.objects.filter(playlist=playlist).order_by('order')
                for i, ps in enumerate(remaining_songs, 1):
                    ps.order = i
                    ps.save()
                
                return Response({'message': 'Canción eliminada correctamente'}, status=status.HTTP_200_OK)
            except PlaylistSong.DoesNotExist:
                return Response({'error': 'La canción no está en la playlist'}, status=status.HTTP_404_NOT_FOUND)
                
        except Song.DoesNotExist:
            return Response({'error': 'Canción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_playlists(request):
    """Obtener todas las playlists del usuario autenticado"""
    playlists = Playlist.objects.filter(user=request.user)
    data = [{'id': playlist.id, 'name': playlist.name} for playlist in playlists]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reordenar_playlist(request, playlist_id):
    """Reordenar las canciones de una playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        song_ids = request.data.get('song_ids', [])
        
        if not song_ids or not isinstance(song_ids, list):
            return Response({'error': 'La lista de IDs de canciones es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que todas las canciones están en la playlist
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist)
        playlist_song_ids = set(ps.song.id for ps in playlist_songs)
        
        if not all(song_id in playlist_song_ids for song_id in song_ids):
            return Response({'error': 'Una o más canciones no están en la playlist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar el orden de las canciones
        for i, song_id in enumerate(song_ids, 1):
            song = Song.objects.get(id=song_id)
            playlist_song = PlaylistSong.objects.get(playlist=playlist, song=song)
            playlist_song.order = i
            playlist_song.save()
        
        return Response({'message': 'Playlist reordenada correctamente'}, status=status.HTTP_200_OK)
        
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_canciones_playlist(request, playlist_id):
    """Obtener todas las canciones de una playlist"""
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=request.user)
        
        # Obtener canciones ordenadas por su posición en la playlist
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist).order_by('order')
        songs = []
        
        for ps in playlist_songs:
            song = ps.song
            songs.append({
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'order': ps.order
            })
        
        return Response(songs)
    except Playlist.DoesNotExist:
        return Response({'error': 'Playlist no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
    })