"""FFprobe inspection and codec-aware MP4 conversion helpers."""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path

class MediaToolError(RuntimeError): pass

def probe_media(path: str | Path) -> dict:
    ffprobe = shutil.which('ffprobe')
    if not ffprobe: raise MediaToolError('FFprobe was not found. Install a full FFmpeg build and add its bin folder to PATH.')
    p = subprocess.run([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
    if p.returncode: raise MediaToolError((p.stderr or 'FFprobe could not read this file.')[-2000:])
    try: return json.loads(p.stdout)
    except ValueError as exc: raise MediaToolError('FFprobe returned invalid metadata.') from exc

def encoder_available(name: str) -> bool:
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg: return False
    p = subprocess.run([ffmpeg, '-hide_banner', '-encoders'], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
    return p.returncode == 0 and name in p.stdout

def choose_mp4_strategy(metadata: dict) -> dict:
    streams = metadata.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), {})
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), {})
    vcodec, pix = video.get('codec_name',''), video.get('pix_fmt','')
    acodec = audio.get('codec_name','')
    # Conservative Premiere-oriented MP4 compatibility. Unusual bit depth/pixel formats are normalized.
    video_copy = vcodec == 'h264' and pix in ('yuv420p', 'yuvj420p')
    audio_copy = not audio or acodec == 'aac'
    if video_copy and audio_copy: mode = 'stream-copy'
    elif video_copy: mode = 'audio-re-encode'
    else: mode = 'full-re-encode'
    return {'mode': mode, 'video_copy': video_copy, 'audio_copy': audio_copy,
            'video_codec': vcodec or 'unknown', 'audio_codec': acodec or ('none' if not audio else 'unknown'),
            'resolution': f"{video.get('width','?')}x{video.get('height','?')}" if video else 'unknown'}

def available_hardware_encoders() -> list[str]:
    return [label for label, name in [('NVIDIA NVENC','h264_nvenc'), ('Intel Quick Sync','h264_qsv'), ('AMD AMF','h264_amf')] if encoder_available(name)]
