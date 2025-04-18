from rest_framework import serializers
from .models import Song, Playlist, PlaylistSong
from django.contrib.auth.models import User

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'url', 'file', 'user', 'download_date', 'duration']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'user', 'songs']

class PlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSong
        fields = ['id', 'playlist', 'song', 'added_date']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, error_messages={
        'min_length': 'La contraseña debe tener al menos 6 caracteres.',
        'blank': 'La contraseña no puede estar vacía.'
    })

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        if len(value.strip()) == 0:
            raise serializers.ValidationError('El nombre de usuario no puede estar vacío.')
        return value
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
