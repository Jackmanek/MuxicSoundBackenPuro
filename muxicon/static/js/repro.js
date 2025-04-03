let btnS = document.querySelector('.start');
let cont=0


btnS.addEventListener('click', function(){
    if(cont % 2 == 0){
        document.querySelector('.btnStart').style.display ="none";
        document.querySelector('audio').play();
        document.querySelector('.btnPause').style.display ="flex";
    }else{
        document.querySelector('.btnPause').style.display ="none";
        document.querySelector('audio').pause();
        document.querySelector('.btnStart').style.display ="flex";
    }
    cont ++;

});

document.addEventListener("DOMContentLoaded", function() {
    const audioPlayer = document.getElementById("audio-player");
    const progressBar = document.getElementById("progress-bar");
    const timeRemaining = document.getElementById("time-remaining");
    const volumeSlider = document.getElementById("volume-slider");
    const playlist = document.getElementById("playlist").getElementsByTagName("li");
    const toggleLoopButton = document.getElementById("toggle-loop");
    const prevButton = document.querySelector(".rev");
    const nextButton = document.querySelector(".few");
    let currentTrack = 0;
    let isLooping = false;

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }
    function loadTrack(index) {
        audioPlayer.src = playlist[index].getAttribute("data-src");
       
    }

    audioPlayer.addEventListener("timeupdate", function() {
        const duration = audioPlayer.duration;
        const currentTime = audioPlayer.currentTime;

        if (duration > 0) {
            const percent = (currentTime / duration) * 100;
            progressBar.style.width = percent + "%";

            const remainingTime = duration - currentTime;
            timeRemaining.textContent = formatTime(remainingTime) + " / "+ formatTime(duration);
        }
    });
    volumeSlider.addEventListener("input", function() {
        audioPlayer.volume = volumeSlider.value;
    });

    audioPlayer.addEventListener("ended", function() {
        if (isLooping) {
            currentTrack = (currentTrack + 1) % playlist.length;
            loadTrack(currentTrack);
            audioPlayer.play();
        } else {
            if (currentTrack < playlist.length - 1) {
                currentTrack++;
                loadTrack(currentTrack);
                audioPlayer.play();
            }
        }
    });
    toggleLoopButton.addEventListener("click", function() {
        isLooping = !isLooping;
        toggleLoopButton.className = isLooping ? "changesOff" : "changesOn";
    });
    prevButton.addEventListener("click", function() {
        if (currentTrack > 0) {
            currentTrack--;
        } else {
            currentTrack = playlist.length - 1; // Ir al final de la lista si estamos al principio
        }
        loadTrack(currentTrack);
        audioPlayer.play(); 
    });

    nextButton.addEventListener("click", function() {
        if (currentTrack < playlist.length - 1) {
            currentTrack++;
        } else {
            currentTrack = 0; // Ir al principio de la lista si estamos al final
        }
        loadTrack(currentTrack);
        audioPlayer.play();
    });

    // Initial load
    loadTrack(currentTrack);

});


let rev = document.querySelector('.rev')

rev.addEventListener('click', atras);
function atras(){
    
}

