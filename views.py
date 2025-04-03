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
import re
from django.http import HttpResponse
from yt_dlp import YoutubeDL
from .models import Song

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

def download_mp3(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')  # Obtener la URL del formulario
        
        if youtube_url:
            try:
                # Configuración de opciones de descarga con YoutubeDL
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'ffmpeg_location': '/usr/bin/ffmpeg',  # Ajustar según sea necesario
                    'outtmpl': os.path.join(settings.MEDIA_ROOT, 'songs', '%(title)s.%(ext)s'),
                    'verbose': True,
                }

                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                
                # Obtener el título normalizado del archivo MP3
                title = info['title']
                normalized_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)
                mp3_filename = f"{normalized_title}.mp3"

                # Ruta del archivo MP3 dentro de MEDIA_ROOT
                song_url = os.path.join('songs', mp3_filename)

                
                # Guardar la canción en la base de datos asociada al usuario actual
                user = request.user
                song = Song(title=mp3_filename, file=song_url, user=user)
                song.save()


                return render(request, 'pages/perfil.html', {'song_url': song_url})
            
            except Exception as e:
                # Manejar errores de descarga
                error_message = f"Error al descargar el video: {str(e)}"
                messages.error(request, error_message)
                return render(request, 'pages/perfil.html', {'error_message': error_message})
        
        else:
            # Manejar el caso en que no se proporciona ninguna URL
            error_message = "Debes proporcionar una URL de YouTube."
            
            return render(request, 'pages/perfil.html', {'error_message': error_message})

    # Si no es una solicitud POST, renderizar la página de perfil
    return render(request, 'pages/perfil.html')