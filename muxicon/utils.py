import os
import subprocess
import json
from django.conf import settings

def get_audio_duration(file_path):
    try:
        ffprobe_path = os.path.join(settings.FFMPEG_PATH, 'ffprobe')  # para Windows agregamos .exe
        result = subprocess.run(
            [ffprobe_path, '-v', 'error', '-show_entries',
             'format=duration', '-of', 'json', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        output = result.stdout.decode('utf-8')
        duration = json.loads(output)['format']['duration']
        return float(duration)
    except Exception as e:
        print(f"Error obteniendo duración: {e}")
        return None