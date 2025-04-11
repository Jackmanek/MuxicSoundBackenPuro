
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Song
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth import authenticate
from .serializers import SongSerializer
import os
import re
import unicodedata
from django.conf import settings
from youtube_dl import YoutubeDL
from .models import Song
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from pytube import YouTube
from moviepy.editor import *
import os
import yt_dlp
from yt_dlp import YoutubeDL
from .models import Song
from .serializers import UserSerializer

@api_view(['GET'])
def inicio(request):
    songs = Song.objects.all()
    song_data = [{"title": song.title, "artist": song.artist, "url": song.url} for song in songs]
    return Response(song_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def registro(request):
    print("Datos recibidos:", request.data)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        print("Datos válidos:", serializer.validated_data)
        serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    else:
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token = RefreshToken.for_user(user)
        return Response({"access": str(token.access_token), "refresh": str(token)}, status=status.HTTP_200_OK)
    return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

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

        last_song = Song.objects.filter(user=request.user).order_by('-id').first()
        new_track_number = (int(re.match(r'Track(\d+)', last_song.title).group(1)) + 1) if last_song else 1

        mp3_filename = f"Track{new_track_number}_{safe_artist}_{safe_title}.mp3"
        song_url = os.path.join('songs', mp3_filename)

        original_file_path = os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.mp3')
        new_file_path = os.path.join(settings.MEDIA_ROOT, song_url)

        if os.path.exists(original_file_path):
            os.rename(original_file_path, new_file_path)
        else:
            return Response({"error": "El archivo no se descargó correctamente."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        song = Song(title=mp3_filename, artist=artist, file=song_url, user=request.user, url=title)
        song.save()

        return Response({"message": "Canción descargada correctamente.", "song": song_url}, status=status.HTTP_201_CREATED)

    except Exception as e:
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