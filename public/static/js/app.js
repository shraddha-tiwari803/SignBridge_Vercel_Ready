(() => {
  const video = document.getElementById('camera');
  const canvas = document.getElementById('capture');
  const context = canvas.getContext('2d');
  const statusEl = document.getElementById('status');
  const cameraMessage = document.getElementById('cameraMessage');
  const startButton = document.getElementById('startCamera');
  const stopButton = document.getElementById('stopCamera');
  const gestureLabel = document.getElementById('gestureLabel');
  const confidence = document.getElementById('confidence');
  const caption = document.getElementById('caption');
  const gestureIcon = document.getElementById('gestureIcon');

  let stream = null;
  let cameraRunning = false;
  let requestPending = false;
  let lastCaptureAt = 0;

  const icons = {
    Open_Palm: '✋', Closed_Fist: '✊', Thumb_Up: '👍', Thumb_Down: '👎',
    Victory: '✌️', Pointing_Up: '☝️', ILoveYou: '🤟', 'No gesture': '👋'
  };

  function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.classList.toggle('error', isError);
  }

  async function checkModelStatus() {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Status check failed');
      if (data.model_found) {
        setStatus('Model file found · Ready to test');
      } else {
        setStatus('Model missing · add gesture_recognizer.task before deployment', true);
      }
    } catch (_error) {
      setStatus('Could not check server status · inspect deployment logs', true);
    }
  }

  async function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      cameraMessage.textContent = 'Camera access requires HTTPS or localhost and a supported browser.';
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false
      });
      video.srcObject = stream;
      await video.play();
      cameraRunning = true;
      startButton.disabled = true;
      stopButton.disabled = false;
      cameraMessage.textContent = 'Camera is running. Frames are sent to the Python service for recognition.';
      gestureLabel.textContent = 'Detecting…';
      requestAnimationFrame(captureLoop);
    } catch (error) {
      cameraMessage.textContent = `Could not start camera: ${error.message || 'permission denied'}. Check browser camera permissions.`;
    }
  }

  function stopCamera() {
    cameraRunning = false;
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    video.srcObject = null;
    startButton.disabled = false;
    stopButton.disabled = true;
    cameraMessage.textContent = 'Camera is off.';
    gestureLabel.textContent = 'Camera stopped';
    confidence.textContent = '—';
    caption.textContent = 'Start the camera and show a supported hand gesture.';
  }

  function captureLoop(now) {
    if (!cameraRunning) return;
    requestAnimationFrame(captureLoop);
    if (requestPending || now - lastCaptureAt < 950 || video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return;
    lastCaptureAt = now;
    requestPending = true;

    canvas.width = 320;
    canvas.height = 240;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const image = canvas.toDataURL('image/jpeg', 0.65);

    fetch('/api/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image })
    })
      .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
        gestureLabel.textContent = data.label || 'Unknown';
        confidence.textContent = `${Number(data.confidence_percent || 0).toFixed(1)}%`;
        caption.textContent = data.caption || 'No caption available.';
        gestureIcon.textContent = icons[data.label] || '🤚';
        cameraMessage.textContent = 'Prediction updated. Confidence is a model score, not a guarantee of correctness.';
      })
      .catch(error => {
        cameraMessage.textContent = error.message || 'Recognition request failed.';
      })
      .finally(() => { requestPending = false; });
  }

  startButton.addEventListener('click', startCamera);
  stopButton.addEventListener('click', stopCamera);
  window.addEventListener('pagehide', stopCamera);
  checkModelStatus();
})();
