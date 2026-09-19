"""
Smart Meeting Summarizer: Audio Recording & Dual-Sound Capture Engine
Handles dual-stream meeting audio recording (Microphone + System Audio Loopback),
auto-saving to disk via local receiver, and multi-format audio ingestion.
"""

import os
import wave
import json
import base64
import time
import threading
import http.server
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# Port for local browser-to-disk recording pipeline
LOCAL_RECEIVER_PORT = 8505
_server_started = False
_server_lock = threading.Lock()

class LocalAudioSaveHandler(http.server.BaseHTTPRequestHandler):
    """Local HTTP endpoint to accept recorded audio blobs and save directly to disk."""
    def log_message(self, format, *args):
        # Suppress noisy console logs
        pass

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            audio_data = self.rfile.read(content_length)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"live_meeting_{timestamp}.wav"
            target_path = os.path.join(RECORDINGS_DIR, filename)

            with open(target_path, "wb") as f:
                f.write(audio_data)

            response = {
                "status": "success",
                "filename": filename,
                "filepath": target_path,
                "size_bytes": len(audio_data),
                "timestamp": timestamp
            }

            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

def ensure_local_audio_receiver(port: int = LOCAL_RECEIVER_PORT):
    """Starts the background local HTTP receiver thread so live recordings save directly to disk."""
    global _server_started
    with _server_lock:
        if _server_started:
            return port
            
        try:
            server = http.server.HTTPServer(('127.0.0.1', port), LocalAudioSaveHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            _server_started = True
            return port
        except Exception:
            # If port 8505 is occupied, try alternative
            try:
                alt_port = port + 1
                server = http.server.HTTPServer(('127.0.0.1', alt_port), LocalAudioSaveHandler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                _server_started = True
                return alt_port
            except Exception:
                return port

def save_base64_audio(b64_data: str, filename_prefix: str = "meeting_recording") -> str:
    """Decodes base64 audio data from browser recording and saves as a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_path = os.path.join(RECORDINGS_DIR, f"{filename_prefix}_{timestamp}.wav")
    
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]
        
    audio_bytes = base64.b64decode(b64_data)
    with open(target_path, "wb") as f:
        f.write(audio_bytes)
        
    return target_path

def save_uploaded_file(uploaded_file) -> str:
    """Saves a Streamlit uploaded audio file to the recordings directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = os.path.splitext(uploaded_file.name)[0].replace(" ", "_")
    ext = os.path.splitext(uploaded_file.name)[1] or ".wav"
    target_path = os.path.join(RECORDINGS_DIR, f"{clean_name}_{timestamp}{ext}")
    
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return target_path

def get_audio_duration_seconds(file_path: str) -> float:
    """Calculates duration in seconds for WAV and standard audio files."""
    try:
        with wave.open(file_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return round(frames / float(rate), 1)
    except Exception:
        size_bytes = os.path.getsize(file_path)
        return max(5.0, round(size_bytes / 32000.0, 1))

def get_dual_recorder_html(receiver_port: int = LOCAL_RECEIVER_PORT):
    """
    Returns an HTML5 Web Audio component that captures BOTH:
    1. Your voice (Microphone)
    2. Remote participants' voices (System Audio from Zoom, Teams, Google Meet)
    Mixes both into high-fidelity audio and automatically saves directly to disk!
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ box-sizing: border-box; }}
    body {{
        background: #0d131f;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin: 0;
        padding: 12px;
        user-select: none;
    }}
    .recorder-card {{
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }}
    .header-title {{
        font-size: 16px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }}
    .subtext {{
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 18px;
    }}
    .sources-row {{
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 20px;
    }}
    .source-badge {{
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .badge-indicator {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #64748b;
    }}
    .indicator-active {{
        background: #22c55e;
        box-shadow: 0 0 8px #22c55e;
    }}
    .timer-display {{
        font-size: 36px;
        font-weight: 800;
        font-family: monospace;
        letter-spacing: 2px;
        color: #f8fafc;
        margin-bottom: 16px;
    }}
    .timer-recording {{
        color: #ef4444;
        animation: pulse 1.5s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    .btn-group {{
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-bottom: 16px;
    }}
    .rec-btn {{
        background: linear-gradient(135deg, #0284c7, #0369a1);
        color: white;
        border: none;
        padding: 10px 22px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .rec-btn:hover {{
        background: #0ea5e9;
        transform: translateY(-1px);
    }}
    .btn-stop {{
        background: #ef4444;
        display: none;
    }}
    .btn-stop:hover {{
        background: #dc2626;
    }}
    .volume-meters {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        background: #080c14;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }}
    .meter-label {{
        font-size: 11px;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }}
    .meter-track {{
        height: 10px;
        background: #1e293b;
        border-radius: 5px;
        overflow: hidden;
    }}
    .meter-fill {{
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #22c55e, #eab308, #ef4444);
        transition: width 0.05s linear;
    }}
    canvas {{
        width: 100%;
        height: 50px;
        background: #080c14;
        border-radius: 6px;
        margin-top: 12px;
        border: 1px solid #1e293b;
    }}
    .audio-player-box {{
        display: none;
        margin-top: 16px;
        background: #0f172a;
        padding: 14px;
        border-radius: 8px;
        border: 1px solid #334155;
    }}
    .disk-saved-alert {{
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #4ade80;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 12px;
        margin-top: 10px;
        text-align: left;
        display: none;
    }}
</style>
</head>
<body>

<div class="recorder-card">
    <div class="header-title">
        <span>🎙️ Dual-Sound Meeting Audio Recorder</span>
    </div>
    <div class="subtext">
        Captures <b>Both Sounds</b>: 1) Your voice from Microphone + 2) Remote attendees' voices from Zoom / Teams / Meet.
    </div>

    <div class="sources-row">
        <div class="source-badge">
            <span class="badge-indicator" id="micIndicator"></span>
            <span>🎤 Microphone (Your Voice)</span>
        </div>
        <div class="source-badge">
            <span class="badge-indicator" id="sysIndicator"></span>
            <span>🔊 System Audio (Remote Attendees)</span>
        </div>
    </div>

    <div class="timer-display" id="timer">00:00:00</div>

    <div class="btn-group">
        <button class="rec-btn" id="btnStart" onclick="startDualRecording()">
            🔴 Start Dual-Sound Meeting Recording
        </button>
        <button class="rec-btn btn-stop" id="btnStop" onclick="stopDualRecording()">
            ⏹ Stop Recording & Auto-Save to Disk
        </button>
    </div>

    <div class="volume-meters">
        <div>
            <div class="meter-label">
                <span>Microphone Volume</span>
                <span id="micVolVal">0%</span>
            </div>
            <div class="meter-track">
                <div class="meter-fill" id="micMeter"></div>
            </div>
        </div>
        <div>
            <div class="meter-label">
                <span>System/Meeting Volume</span>
                <span id="sysVolVal">0%</span>
            </div>
            <div class="meter-track">
                <div class="meter-fill" id="sysMeter"></div>
            </div>
        </div>
    </div>

    <canvas id="waveformCanvas" width="500" height="50"></canvas>

    <div class="audio-player-box" id="playerBox">
        <div style="font-size:13px; color:#38bdf8; margin-bottom:8px; font-weight:700;">
            ✅ Meeting Audio Captured & Ready for Immediate Playback:
        </div>
        <audio id="playbackAudio" controls style="width:100%; height:36px;"></audio>
        
        <div class="disk-saved-alert" id="savePathNotice">
            💾 <b>Auto-Saved to Hard Drive:</b> Saving file...
        </div>

        <div style="display:flex; justify-content:space-between; margin-top:10px;">
            <a id="downloadLink" style="font-size:12px; color:#34d399; text-decoration:none; font-weight:600;" download="meeting_recording.wav">
                📥 Manual Browser Download (.wav)
            </a>
            <span style="font-size:11px; color:#94a3b8;">Format: 16-Bit Stereo Mixed Audio</span>
        </div>
    </div>
</div>

<script>
    let micStream = null;
    let sysStream = null;
    let audioCtx = null;
    let mixedDest = null;
    let mediaRecorder = null;
    let recordedChunks = [];
    let timerInterval = null;
    let secondsElapsed = 0;
    let animId = null;
    let micAnalyser = null;
    let sysAnalyser = null;
    const receiverPort = {receiver_port};

    async function startDualRecording() {{
        try {{
            // 1. Capture Microphone
            micStream = await navigator.mediaDevices.getUserMedia({{ audio: true, video: false }});
            document.getElementById('micIndicator').classList.add('indicator-active');

            // 2. Capture System / Meeting Audio (Zoom/Teams tab or Screen with audio)
            try {{
                sysStream = await navigator.mediaDevices.getDisplayMedia({{
                    video: true,
                    audio: {{
                        echoCancellation: false,
                        noiseSuppression: false,
                        autoGainControl: false
                    }}
                }});
                document.getElementById('sysIndicator').classList.add('indicator-active');
            }} catch(e) {{
                console.log("System audio skipped or cancelled, recording Mic only.", e);
            }}

            // 3. AudioContext to mix both streams
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            mixedDest = audioCtx.createMediaStreamDestination();

            // Connect Mic
            const micSource = audioCtx.createMediaStreamSource(micStream);
            micAnalyser = audioCtx.createAnalyser();
            micAnalyser.fftSize = 128;
            micSource.connect(micAnalyser);
            micSource.connect(mixedDest);

            // Connect System Audio if present
            if (sysStream && sysStream.getAudioTracks().length > 0) {{
                const sysSource = audioCtx.createMediaStreamSource(sysStream);
                sysAnalyser = audioCtx.createAnalyser();
                sysAnalyser.fftSize = 128;
                sysSource.connect(sysAnalyser);
                sysSource.connect(mixedDest);
            }}

            // 4. Record the mixed destination stream
            recordedChunks = [];
            mediaRecorder = new MediaRecorder(mixedDest.stream);

            mediaRecorder.ondataavailable = (e) => {{
                if (e.data.size > 0) recordedChunks.push(e.data);
            }};

            mediaRecorder.onstop = exportAudioData;

            mediaRecorder.start(500); // 500ms chunks

            // UI updates
            document.getElementById('btnStart').style.display = 'none';
            document.getElementById('btnStop').style.display = 'inline-flex';
            document.getElementById('timer').classList.add('timer-recording');
            document.getElementById('playerBox').style.display = 'none';
            document.getElementById('savePathNotice').style.display = 'none';

            secondsElapsed = 0;
            timerInterval = setInterval(() => {{
                secondsElapsed++;
                const h = String(Math.floor(secondsElapsed / 3600)).padStart(2, '0');
                const m = String(Math.floor((secondsElapsed % 3600) / 60)).padStart(2, '0');
                const s = String(secondsElapsed % 60).padStart(2, '0');
                document.getElementById('timer').innerText = `${{h}}:${{m}}:${{s}}`;
            }}, 1000);

            visualizeMeters();

        }} catch(err) {{
            alert("Error initiating recording: " + err.message + "\\nPlease grant microphone/system audio permissions.");
            console.error(err);
        }}
    }}

    function visualizeMeters() {{
        const canvas = document.getElementById('waveformCanvas');
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        function update() {{
            // Update Mic Meter
            if (micAnalyser) {{
                const data = new Uint8Array(micAnalyser.frequencyBinCount);
                micAnalyser.getByteFrequencyData(data);
                const avg = data.reduce((a,b) => a+b, 0) / data.length;
                const pct = Math.min(100, Math.round((avg / 128) * 100));
                document.getElementById('micMeter').style.width = pct + '%';
                document.getElementById('micVolVal').innerText = pct + '%';
            }}

            // Update System Audio Meter
            if (sysAnalyser) {{
                const data = new Uint8Array(sysAnalyser.frequencyBinCount);
                sysAnalyser.getByteFrequencyData(data);
                const avg = data.reduce((a,b) => a+b, 0) / data.length;
                const pct = Math.min(100, Math.round((avg / 128) * 100));
                document.getElementById('sysMeter').style.width = pct + '%';
                document.getElementById('sysVolVal').innerText = pct + '%';
            }}

            // Draw simple waveform
            ctx.fillStyle = '#080c14';
            ctx.fillRect(0, 0, width, height);
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#38bdf8';
            ctx.beginPath();
            const slice = width / 64;
            let x = 0;
            for (let i = 0; i < 64; i++) {{
                const v = Math.random() * (micAnalyser ? 15 : 5);
                const y = (height / 2) + (i % 2 === 0 ? v : -v);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += slice;
            }}
            ctx.stroke();

            animId = requestAnimationFrame(update);
        }}
        update();
    }}

    function stopDualRecording() {{
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
            mediaRecorder.stop();
        }}
        if (micStream) micStream.getTracks().forEach(t => t.stop());
        if (sysStream) sysStream.getTracks().forEach(t => t.stop());
        if (timerInterval) clearInterval(timerInterval);
        if (animId) cancelAnimationFrame(animId);

        document.getElementById('micIndicator').classList.remove('indicator-active');
        document.getElementById('sysIndicator').classList.remove('indicator-active');
        document.getElementById('btnStart').style.display = 'inline-flex';
        document.getElementById('btnStop').style.display = 'none';
        document.getElementById('timer').classList.remove('timer-recording');
        document.getElementById('micMeter').style.width = '0%';
        document.getElementById('sysMeter').style.width = '0%';
    }}

    function exportAudioData() {{
        const blob = new Blob(recordedChunks, {{ type: 'audio/webm' }});
        const url = URL.createObjectURL(blob);
        const player = document.getElementById('playbackAudio');
        player.src = url;
        document.getElementById('downloadLink').href = url;
        document.getElementById('playerBox').style.display = 'block';

        // Auto-save directly to local Python recordings folder via local receiver endpoint
        const noticeEl = document.getElementById('savePathNotice');
        noticeEl.style.display = 'block';
        noticeEl.innerHTML = `⏳ <i>Saving recording directly to your computer's hard drive...</i>`;

        fetch(`http://127.0.0.1:${{receiverPort}}/save_recording`, {{
            method: 'POST',
            body: blob
        }})
        .then(res => res.json())
        .then(data => {{
            if (data.status === 'success') {{
                noticeEl.innerHTML = `✅ <b>Recording Auto-Saved to Disk:</b><br><code style="color:#38bdf8; font-size:11px;">${{data.filepath}}</code><br><span style="color:#94a3b8; font-size:10px;">Select this file in the dropdown below to generate your Point-Wise MoM!</span>`;
            }} else {{
                noticeEl.innerHTML = `⚠️ <i>Saved in browser. You can also click the download link below.</i>`;
            }}
        }})
        .catch(err => {{
            noticeEl.innerHTML = `💾 <b>Audio Ready:</b> You can play it above or click 'Manual Browser Download' below.`;
            console.log("Receiver notice:", err);
        }});
    }}
</script>
</body>
</html>
"""
