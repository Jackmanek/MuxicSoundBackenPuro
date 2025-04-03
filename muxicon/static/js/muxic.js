document.addEventListener("DOMContentLoaded", function() {
    const audioPlayer = document.getElementById('audio-player');
    const playlist = document.getElementById('playlist');
    const tracks = playlist.getElementsByTagName('li');
    let currentTrack = 0;

    function playTrack(index) {
        if (index >= 0 && index < tracks.length) {
            currentTrack = index;
            audioPlayer.src = tracks[index].getAttribute('data-src');
            audioPlayer.play();
            updatePlaylistHighlight();
        }
    }

    function updatePlaylistHighlight() {
        for (let i = 0; i < tracks.length; i++) {
            tracks[i].classList.remove('active');
        }
        tracks[currentTrack].classList.add('active');
    }

    playlist.addEventListener('click', function(e) {
        if (e.target && e.target.nodeName === 'LI') {
            for (let i = 0; i < tracks.length; i++) {
                if (tracks[i] === e.target) {
                    playTrack(i);
                    break;
                }
            }
        }
    });

    audioPlayer.addEventListener('ended', function() {
        currentTrack++;
        if (currentTrack < tracks.length) {
            playTrack(currentTrack);
        }
    });

    // Start playing the first track
    if (tracks.length > 0) {
        playTrack(0);
    }
});