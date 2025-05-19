
let songIndex = 0;
let audioElement = new Audio(`/static/${songs[songIndex].file_url}`);

const masterPlay = document.getElementById('masterPlay');
const ProgressBar = document.getElementById('ProgressBar');
const volumeBar = document.getElementById('volumeBar');
const volumeIcon = document.getElementById('volumeIcon');
const masterSongName = document.getElementById('masterSongName');
const songItems = document.querySelectorAll('.songItem');
const gif = document.getElementById('gif');
const nextBtn = document.getElementById('next');
const prevBtn = document.getElementById('previous');
const voiceBtn = document.getElementById('voiceBtn');
const searchBar = document.getElementById('searchBar');

songItems.forEach((element, i) => {
  const songName = element.querySelector('.songName');
  songName.innerText = songs[i].name;
});

function attachEventListeners() {
  masterPlay.addEventListener('click', togglePlayPause);

  volumeBar.addEventListener('input', () => {
    audioElement.volume = volumeBar.value;
    audioElement.muted = false;
    updateVolumeIcon();
  });

  volumeIcon.addEventListener('click', () => {
    audioElement.muted = !audioElement.muted;
    volumeBar.value = audioElement.muted ? 0 : audioElement.volume;
    updateVolumeIcon();
  });

  audioElement.addEventListener('timeupdate', () => {
    ProgressBar.value = audioElement.duration
      ? (audioElement.currentTime / audioElement.duration) * 100
      : 0;
  });

  ProgressBar.addEventListener('input', () => {
    audioElement.currentTime = (ProgressBar.value / 100) * audioElement.duration;
  });

  audioElement.addEventListener('ended', () => {
    playSong((songIndex + 1) % songs.length);
  });

  nextBtn.addEventListener('click', () => playSong((songIndex + 1) % songs.length));
  prevBtn.addEventListener('click', () => playSong((songIndex - 1 + songs.length) % songs.length));

  songItems.forEach((_, i) => {
    const playBtn = document.getElementById(`play-${i}`);
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        if (songIndex === i && !audioElement.paused) {
          audioElement.pause();
          updateMasterIcon();
          resetAllPlayButtons();
        } else {
          playSong(i);
        }
      });
    }
  });

  searchBar.addEventListener('input', (e) => {
    filterSongs(e.target.value);
  });

  voiceBtn.addEventListener('click', startVoiceSearch);
}

function togglePlayPause() {
  if (audioElement.paused || audioElement.currentTime <= 0) {
    audioElement.play();
    updateMasterIcon();
    const playBtn = document.getElementById(`play-${songIndex}`);
    if (playBtn) playBtn.classList.replace('fa-play-circle', 'fa-pause-circle');
  } else {
    audioElement.pause();
    updateMasterIcon();
    resetAllPlayButtons();
  }
}

function updateMasterIcon() {
  masterPlay.classList.toggle('fa-play-circle', audioElement.paused);
  masterPlay.classList.toggle('fa-pause-circle', !audioElement.paused);
  gif.style.opacity = audioElement.paused ? 0 : 1;
}

function resetAllPlayButtons() {
  songItems.forEach((_, i) => {
    const icon = document.getElementById(`play-${i}`);
    if (icon) icon.classList.replace('fa-pause-circle', 'fa-play-circle');
  });
}

function updateVolumeIcon() {
  const volume = audioElement.muted ? 0 : audioElement.volume;
  volumeIcon.className = 'fas';
  if (volume === 0) volumeIcon.classList.add('fa-volume-mute');
  else if (volume <= 0.5) volumeIcon.classList.add('fa-volume-down');
  else volumeIcon.classList.add('fa-volume-up');
}

function playSong(i) {
  resetAllPlayButtons();
  songIndex = i;
  audioElement.src = `/static/${songs[i].file_url}`;
  masterSongName.innerText = songs[i].name;
  audioElement.currentTime = 0;
  audioElement.play();
  updateMasterIcon();
  const playBtn = document.getElementById(`play-${i}`);
  if (playBtn) playBtn.classList.replace('fa-play-circle', 'fa-pause-circle');
}

function filterSongs(query) {
  songItems.forEach((item) => {
    const name = item.querySelector('.songName').innerText.toLowerCase();
    item.style.display = name.includes(query.toLowerCase()) ? 'flex' : 'none';
  });
}

function startVoiceSearch() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return alert('Speech Recognition not supported.');

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.start();
  recognition.onresult = (event) => {
    const command = event.results[0][0].transcript.toLowerCase();
    searchBar.value = command;
    filterSongs(command);
    processVoiceCommand(command);
  };
  recognition.onerror = (event) => {
    console.error('Voice error:', event.error);
  };
}

function processVoiceCommand(command) {
  command = command.toLowerCase().trim();

  // Handle: "volume to 50", "volume 50 percent", "volume upto 50"
  const volumeMatch = command.match(/volume (to |upto )?(\d{1,3}) ?(percent|%|)/);
  if (volumeMatch) {
    let vol = Math.max(0, Math.min(100, parseInt(volumeMatch[2])));
    audioElement.volume = vol / 100;
    audioElement.muted = false;
    volumeBar.value = audioElement.volume;
    updateVolumeIcon();
    return;
  }

  // Handle: "volume up"
  if (command.includes("volume up")) {
    let newVolume = Math.min(1, audioElement.volume + 0.1);
    audioElement.volume = newVolume;
    audioElement.muted = false;
    volumeBar.value = newVolume;
    updateVolumeIcon();
    return;
  }

  // Handle: "volume down"
  if (command.includes("volume down")) {
    let newVolume = Math.max(0, audioElement.volume - 0.1);
    audioElement.volume = newVolume;
    audioElement.muted = false;
    volumeBar.value = newVolume;
    updateVolumeIcon();
    return;
  }

  // Handle: "mute"
  if (command.includes("mute")) {
    audioElement.muted = true;
    volumeBar.value = 0;
    updateVolumeIcon();
    return;
  }

  // Handle: "unmute"
  if (command.includes("unmute")) {
    audioElement.muted = false;
    volumeBar.value = audioElement.volume;
    updateVolumeIcon();
    return;
  }

  // Play specific song
  if (command.startsWith('play ')) {
    const name = command.replace('play ', '').trim();
    const index = songs.findIndex(s => s.name.toLowerCase().includes(name));
    if (index !== -1) {
      playSong(index);
      return;
    }
  }

  // Play or resume
  if (command === 'play' || command === 'play a song' || command === 'play song') {
    if (audioElement.paused || audioElement.currentTime === 0) {
      audioElement.play();
      updateMasterIcon();
      const playBtn = document.getElementById(`play-${songIndex}`);
      if (playBtn) playBtn.classList.replace('fa-play-circle', 'fa-pause-circle');
    }
    return;
  }

  if (command.includes('pause')) {
    audioElement.pause();
    updateMasterIcon();
  } else if (command.includes('resume')) {
    audioElement.play();
    updateMasterIcon();
  } else if (command.includes('next')) {
    playSong((songIndex + 1) % songs.length);
  } else if (command.includes('previous') || command.includes('back')) {
    playSong((songIndex - 1 + songs.length) % songs.length);
  } else if (command.includes('stop')) {
    audioElement.pause();
    audioElement.currentTime = 0;
    updateMasterIcon();
  }
}


attachEventListeners();
