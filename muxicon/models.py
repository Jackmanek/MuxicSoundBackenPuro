from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=200)
    file = models.FileField(upload_to='media/songs/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='songs')
    download_date = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.title


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, through='PlaylistSong')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order = 0
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ('playlist', 'song') 