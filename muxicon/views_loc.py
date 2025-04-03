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
import re
import unicodedata

def inicio(request):
    songs = Song.objects.all()

    return render(request, 'pages/inicio.html', {'songs': songs})

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view')
    else:
        form = UserCreationForm()
    return render(request, 'pages/registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_page = request.GET.get('next', 'inicio')
            return redirect(next_page)  # Redirige al usuario a la página principal después de iniciar sesión
    else:
        form = AuthenticationForm()
    return render(request, 'pages/login.html', {'form': form})

def perfil(request):
    songs = Song.objects.all()
    return render(request, 'pages/perfil.html', {'songs': songs})

"""
def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')  # Obtener la URL del formulario
        
        if youtube_url:
            # Configuración de opciones de descarga
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': 'C:/ffmpeg/bin',
                'outtmpl': os.path.join(settings.MEDIA_ROOT, 'songs', '%(title)s.%(ext)s'),
                'verbose': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

            # Generar la URL del archivo MP3
            mp3_filename = info['title'] + '.mp3'
            song_url = os.path.join('songs', mp3_filename)

            user = request.user
            song = Song(title=mp3_filename, file=song_url,user=user)
            song.save()

            return render(request, 'pages/perfil.html', {'song_url': song_url})
        else:
            # Manejar el caso en que no se proporciona ninguna URL
            error_message = "Debes proporcionar una URL de YouTube."
            return render(request, 'pages/perfil.html', {'error_message': error_message})

    return render(request, 'pages/perfil.html')

def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        
        if youtube_url:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': 'C:/ffmpeg/bin',  
                'outtmpl': os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.%(ext)s'),
                'verbose': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

            # Buscar el último número de track en la base de datos
            last_song = Song.objects.filter(user=request.user).order_by('-id').first()
            if last_song:
                last_track_number = int(last_song.title.replace('Track', '').replace('.mp3', ''))
                new_track_number = last_track_number + 1
            else:
                new_track_number = 1

            mp3_filename = f"Track{new_track_number}.mp3"
            song_url = os.path.join('songs', mp3_filename)

            # Renombrar el archivo descargado
            original_file_path = os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.mp3')
            new_file_path = os.path.join(settings.MEDIA_ROOT, song_url)

            if os.path.exists(original_file_path):
                os.rename(original_file_path, new_file_path)
            else:
                messages.error(request, 'El archivo no se descargó correctamente.')
                return redirect('perfil')

            # Guardar la canción en la base de datos
            user = request.user
            song = Song(title=mp3_filename, file=song_url, user=user)
            song.save()

            messages.success(request, 'Canción descargada correctamente.')
            return redirect('perfil')

        else:
            messages.error(request, "Debes proporcionar una URL de YouTube.")
            return redirect('perfil')

    return render(request, 'pages/perfil.html')


def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        
        if youtube_url:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': 'C:/ffmpeg/bin',  
                'outtmpl': os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.%(ext)s'),
                'verbose': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

            # Extraer el título de la canción y el artista
            title = info.get('title', 'Unknown Title')
            artist = info.get('artist', info.get('uploader', 'Unknown Artist'))

            # Limpiar y normalizar los nombres
            safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            safe_artist = re.sub(r'[^\w\s-]', '', artist).strip().replace(' ', '_')

            # Buscar el último número de track en la base de datos
            last_song = Song.objects.filter(user=request.user).order_by('-id').first()
            if last_song:
                # Extraer solo el número de pista del título, si es posible
                match = re.match(r'Track(\d+)', last_song.title)
                if match:
                    last_track_number = int(match.group(1))
                else:
                    last_track_number = 0
                new_track_number = last_track_number + 1
            else:
                new_track_number = 1

            # Crear el nombre del archivo MP3 y la URL
            mp3_filename = f"Track{new_track_number}_{safe_artist}_{safe_title}.mp3"
            song_url = os.path.join('songs', mp3_filename)

            # Renombrar el archivo descargado
            original_file_path = os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.mp3')
            new_file_path = os.path.join(settings.MEDIA_ROOT, song_url)

            if os.path.exists(original_file_path):
                os.rename(original_file_path, new_file_path)
            else:
                messages.error(request, 'El archivo no se descargó correctamente.')
                return redirect('perfil')

            # Guardar la canción en la base de datos con el nombre separado
            user = request.user
            song = Song(title=mp3_filename, artist=artist, file=song_url, user=user, url=title)
            song.save()

            messages.success(request, 'Canción descargada correctamente.')
            return redirect('perfil')

        else:
            messages.error(request, "Debes proporcionar una URL de YouTube.")
            return redirect('perfil')

    return render(request, 'pages/perfil.html')
"""
def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        
        if youtube_url:
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

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)

            # Extraer el título de la canción y el artista
            title = info.get('title', 'Unknown Title')
            artist = info.get('artist', info.get('uploader', 'Unknown Artist'))
            
            # Normalizar y limpiar el título y artista, para evitar problemas de codificación
            title = unicodedata.normalize('NFKD', title)
            artist = unicodedata.normalize('NFKD', artist)

            # Limpiar y normalizar los nombres
            safe_title = re.sub(r'[^\w\s\-ñÑáéíóúÁÉÍÓÚ\'´]', '', title).strip().replace(' ', '_')
            safe_artist = re.sub(r'[^\w\s\-ñÑáéíóúÁÉÍÓÚ\'´]', '', artist).strip().replace(' ', '_')
            # Agregar prefijo r_-_ al nombre del título
            safe_title = f"r_-_{safe_title}"

            # Codificar en UTF-8 para manejar correctamente caracteres Unicode
            safe_title = safe_title.encode('utf-8', errors='ignore').decode('utf-8')
            safe_artist = safe_artist.encode('utf-8', errors='ignore').decode('utf-8')

            # Buscar el último número de track en la base de datos
            last_song = Song.objects.filter(user=request.user).order_by('-id').first()
            if last_song:
                # Extraer solo el número de pista del título, si es posible
                match = re.match(r'Track(\d+)', last_song.title)
                if match:
                    last_track_number = int(match.group(1))
                else:
                    last_track_number = 0
                new_track_number = last_track_number + 1
            else:
                new_track_number = 1

            # Crear el nombre del archivo MP3 y la URL
            mp3_filename = f"Track{new_track_number}_{safe_artist}_{safe_title}.mp3"
            song_url = os.path.join('songs', mp3_filename)

            # Renombrar el archivo descargado
            original_file_path = os.path.join(settings.MEDIA_ROOT, 'songs', 'temp.mp3')
            new_file_path = os.path.join(settings.MEDIA_ROOT, song_url)

            if os.path.exists(original_file_path):
                os.rename(original_file_path, new_file_path)
            else:
                messages.error(request, 'El archivo no se descargó correctamente.')
                return redirect('perfil')

            # Guardar la canción en la base de datos con el nombre separado
            user = request.user
            song = Song(title=mp3_filename, artist=artist, file=song_url, user=user, url=title)
            song.save()

            messages.success(request, 'Canción descargada correctamente.')
            return redirect('perfil')

        else:
            messages.error(request, "Debes proporcionar una URL de YouTube.")
            return redirect('perfil')

    return render(request, 'pages/perfil.html')


def eliminar_song(request, song_id):
    song = Song.objects.get(id=song_id)
    song.delete()
    return redirect('perfil')