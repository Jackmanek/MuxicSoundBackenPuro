from rest_framework import serializers
from .models import Song, Playlist, PlaylistSong
from django.contrib.auth.models import User

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'url', 'file', 'user', 'download_date']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user', 'songs']

class PlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
        fields = ['id', 'playlist', 'song', 'added_date']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        print("Datos validados antes de crear usuario:", validated_data)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        print("Contraseña en la base de datos después de create_user:", user.password)
        return user
