"""Universal Downloader — modern Qt UI with Premiere-friendly H.264/AAC MP4 output.
Install: python -m pip install -U PySide6 yt-dlp
Also install a full FFmpeg build (ffmpeg.exe and ffprobe.exe on PATH) for MP4 conversion/audio extraction.
"""
import os, sys, json, shutil, subprocess, tempfile, threading, urllib.request, urllib.parse, time, traceback
from pathlib import Path
from datetime import datetime
from history_store import HistoryStore, normalize_source
from media_engine import probe_media, choose_mp4_strategy, available_hardware_encoders
from localization import LANGUAGES, translate

from PySide6.QtCore import Qt, QThread, Signal, QSize, QUrl, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QDesktopServices
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog,
    QMessageBox, QScrollArea, QSizePolicy, QStackedWidget, QToolButton, QSpacerItem, QGroupBox, QListWidget, QListWidgetItem, QInputDialog, QGraphicsOpacityEffect
)

# Python 3.15 may expose concurrent.futures.ThreadPoolExecutor as a lazy-import
# proxy that some yt-dlp versions attempt to call directly. Resolve the real
# implementation before yt-dlp starts fragment downloads.
try:
    import concurrent.futures as _concurrent_futures
    import concurrent.futures.thread as _futures_thread
    if not callable(_concurrent_futures.ThreadPoolExecutor):
        _concurrent_futures.ThreadPoolExecutor = _futures_thread.ThreadPoolExecutor
except (ImportError, AttributeError):
    pass

try:
    import yt_dlp
    from yt_dlp.utils import sanitize_filename
except ImportError:
    yt_dlp = None
    sanitize_filename = None


def get_site_auth_options(url: str) -> dict:
    """Return Chrome-cookie options for Reddit and Pinterest URLs.

    Browser cookies are read by yt-dlp at runtime; no cookie data is stored
    in the app's settings or written to its diagnostic log.
    """
    try:
        # The UI accepts pasted links without a scheme, e.g. reddit.com/r/... .
        # urlsplit() treats that as a path, so add https:// before extracting host.
        candidate = (url or "").strip()
        if candidate and not urllib.parse.urlsplit(candidate).scheme:
            candidate = "https://" + candidate.lstrip("/")
        host = (urllib.parse.urlsplit(candidate).hostname or "").lower().rstrip(".")
    except (ValueError, AttributeError):
        return {}

    is_reddit = host == "reddit.com" or host.endswith(".reddit.com") or host == "redd.it"
    is_pinterest = (
        host == "pinterest.com"
        or host.endswith(".pinterest.com")
        or host == "pin.it"
    )
    if is_reddit or is_pinterest:
        return {"cookiesfrombrowser": ("chrome", None, None, None)}
    return {}

APP_DIR = Path.home() / ".universal_downloader"
CONFIG_FILE = APP_DIR / "settings.json"
HISTORY_FILE = APP_DIR / "history.json"
DATABASE_FILE = APP_DIR / "downloads.sqlite3"
QUEUE_FILE = APP_DIR / "queue.json"
FORMATS = ["MP4 (Premiere-friendly)", "MP3 (audio only)", "MKV", "WEBM", "M4A (audio only)"]
QUALITIES = {"Best available": None, "8K (4320p)": 4320, "4K (2160p)": 2160,
             "1440p": 1440, "1080p": 1080, "720p": 720, "480p": 480, "360p": 360}

DARK_QSS = r"""
* { font-family: 'Segoe UI', 'Inter', sans-serif; }
QMainWindow, QWidget#root, QWidget#content, QScrollArea, QWidget#scrollBody { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #07131f, stop:0.52 #0b1b2a, stop:1 #07131f); color: #eff6ff; }
QFrame#sidebar { background: #08111c; border-right: 1px solid #1b2a3a; }
QFrame#brandMark { background: transparent; }
QLabel#logo { color: #35d6b1; font-size: 30px; font-weight: 900; }
QLabel#brand { color: #f2f7fc; font-size: 14px; font-weight: 700; }
QLabel#pageTitle { color: #f5f8fc; font-size: 29px; font-weight: 750; }
QLabel#subtitle { color: #7890aa; font-size: 14px; }
QLabel#sectionLabel { color: #d8e5f2; font-size: 14px; font-weight: 600; }
QLabel#muted { color: #8ea5bb; font-size: 12px; }
QLabel#tinyMuted { color: #7890aa; font-size: 11px; }
QFrame#card, QFrame#fieldCard, QFrame#historyCard { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #102235, stop:0.55 #0d1b2a, stop:1 #0a1724); border: 1px solid #20374a; border-radius: 15px; }
QFrame#fieldCard { border-radius: 14px; }
QLineEdit, QComboBox { background: #101f2e; border: 1px solid #2a4358; border-radius: 10px; color: #eef6ff; padding: 10px 12px; selection-background-color: #126454; min-height: 20px; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #35d6b1; }
QComboBox::drop-down { border: 0; width: 26px; }
QComboBox QAbstractItemView { background: #102235; color: #eff6ff; selection-background-color: #125548; border: 1px solid #2a4358; }
QPushButton { background: #132438; color: #eaf2fb; border: 1px solid #20374a; border-radius: 10px; padding: 10px 13px; font-size: 12px; }
QPushButton:hover { background: #1a3045; border-color: #31556c; }
QPushButton:pressed { background: #0f2535; padding-top: 11px; padding-bottom: 9px; }
QPushButton:disabled { color: #6f8294; background: #15202b; }
QPushButton#nav { text-align: left; border: 0; background: transparent; color: #8ea5bb; padding: 13px 14px; font-size: 13px; }
QPushButton#nav:hover { background: #102a31; color: #d9fff4; }
QPushButton#nav[active="true"] { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0c514b, stop:1 #0a3439); color: #eafff9; border-radius: 12px; font-weight: 650; }
QPushButton#paste { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #11a98b, stop:1 #076b60); color: #effffb; border: 1px solid #11977d; font-weight: 650; }
QPushButton#paste:hover { background: #0a927b; }
QPushButton#primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #35e0bb, stop:0.55 #26d0ad, stop:1 #16b99d); color: #031b17; border: 1px solid #43e1bf; border-radius: 12px; padding: 16px; font-size: 15px; font-weight: 750; }
QPushButton#primary:hover { background: #4ae2bf; }
QPushButton#theme { border-radius: 12px; padding: 10px 15px; }
QPushButton#iconButton { padding: 7px 10px; min-width: 28px; }
QProgressBar { background: #152a3b; border: 0; border-radius: 4px; height: 7px; text-align: center; color: transparent; }
QProgressBar::chunk { background: #35d6b1; border-radius: 4px; }
QScrollBar:vertical { background: #07131f; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #284155; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QListWidget { background: transparent; border: 1px solid #20374a; border-radius: 12px; padding: 5px; outline: 0; }
QListWidget::item { background: #102235; border: 1px solid #20374a; border-radius: 8px; padding: 10px 12px; margin: 3px 1px; color: #dce8f5; }
QListWidget::item:hover { background: #153047; border-color: #31556c; }
QListWidget::item:selected { background: #103d3a; border-color: #35d6b1; color: #f2fffb; }
QLabel#eyebrow { color: #35d6b1; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
QLabel#infoCardTitle { color: #eaf3fc; font-size: 18px; font-weight: 750; }
QLabel#infoCardTitleSmall { color: #eaf3fc; font-size: 16px; font-weight: 750; }
QLabel#infoStepTitle { color: #e5effa; font-size: 12px; font-weight: 750; }
QLabel#infoStepDescription { color: #8ea5bb; font-size: 11px; }
QLabel#stepNumber { color: #35d6b1; font-weight: 800; font-size: 12px; padding-top: 3px; }
QFrame#featureTile { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #102235,stop:1 #0b1a29); border:1px solid #20374a; border-radius:12px; }
QFrame#infoIconWrap { background: #10283a; border:1px solid #1d3b50; border-radius:21px; }
QFrame#featureIconWrap { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #103a3d,stop:1 #102b38); border:1px solid #1c4b50; border-radius:11px; }
QLabel#avatar { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0b4c4b,stop:1 #0b2c3b); color:#35d6b1; border:1px solid #17645d; border-radius:35px; font-size:31px; font-weight:800; }
QFrame#infoDivider { background: #20364a; border:0; }

"""
LIGHT_QSS = r"""
* { font-family: 'Segoe UI', 'Inter', sans-serif; }
QMainWindow, QWidget#root, QWidget#content, QScrollArea, QWidget#scrollBody { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f5f9fd, stop:0.48 #edf4fa, stop:1 #f7fafc); color: #172b42; }
QFrame#sidebar { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f9fbfe, stop:1 #eaf1f8); border-right: 1px solid #d6e2ee; }
QLabel#logo { color: #008e78; font-size: 30px; font-weight: 900; }
QLabel#brand { color: #14283f; font-size: 14px; font-weight: 700; }
QLabel#pageTitle { color: #14283f; font-size: 29px; font-weight: 750; }
QLabel#subtitle, QLabel#tinyMuted { color: #667f99; font-size: 12px; }
QLabel#sectionLabel { color: #1b3048; font-size: 14px; font-weight: 600; }
QLabel#muted { color: #526b85; font-size: 12px; }
QLabel#eyebrow { color: #008e78; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
QFrame#card, QFrame#fieldCard, QFrame#historyCard { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:0.52 #f7fbfe, stop:1 #edf4fa); border: 1px solid #d5e2ee; border-radius: 15px; }
QFrame#fieldCard { border-radius: 14px; }
QLineEdit, QComboBox { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f3f8fc); border: 1px solid #d2dfeb; border-radius: 10px; color: #172b42; padding: 10px 12px; selection-background-color: #bcefe3; min-height: 20px; }
QLineEdit:focus, QComboBox:focus { border: 1px solid #10a98e; }
QComboBox::drop-down { border: 0; width: 26px; }
QComboBox QAbstractItemView { background: #ffffff; color: #172b42; selection-background-color: #d5f5ec; border: 1px solid #d2dfeb; }
QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #edf4fa); color: #1a3048; border: 1px solid #d1dfeb; border-radius: 10px; padding: 10px 13px; font-size: 12px; }
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #edfff9, stop:1 #e0f0f8); border-color: #9edccc; }
QPushButton:pressed { background: #d5eee7; padding-top: 11px; padding-bottom: 9px; }
QPushButton:disabled { color: #92a4b5; background: #edf2f7; }
QPushButton#nav { text-align: left; border: 0; background: transparent; color: #60778e; padding: 13px 14px; font-size: 13px; }
QPushButton#nav:hover { background: #e8f7f4; color: #075e51; }
QPushButton#nav[active="true"] { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d5f8ef, stop:1 #c7f0e7); color: #075c4e; border-radius: 12px; font-weight: 650; }
QPushButton#paste { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #16b99a, stop:1 #078570); color: #ffffff; border: 1px solid #0fa88d; font-weight: 650; }
QPushButton#paste:hover { background: #079b81; }
QPushButton#primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #48dfbc, stop:0.52 #26cdaa, stop:1 #0eb99a); color: #06271f; border: 1px solid #19bc9b; border-radius: 12px; padding: 16px; font-size: 15px; font-weight: 750; }
QPushButton#primary:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #62e8c9, stop:1 #20c6a4); }
QPushButton#theme { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #eaf2f9); border: 1px solid #d3e0eb; border-radius: 15px; padding: 10px 15px; }
QPushButton#iconButton { padding: 7px 10px; min-width: 28px; }
QProgressBar { background: #e1ebf3; border: 1px solid #d3e1ec; border-radius: 5px; height: 8px; text-align: center; color: #36536d; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #50e4c1, stop:0.55 #20cbaa, stop:1 #0aa98b); border-radius: 4px; }
QScrollBar:vertical { background: #edf3f8; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #c4d3e0; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QListWidget { background: transparent; border: 1px solid #d5e2ee; border-radius: 12px; padding: 5px; outline: 0; }
QListWidget::item { background: #ffffff; border: 1px solid #dbe6ef; border-radius: 8px; padding: 10px 12px; margin: 3px 1px; color: #1a3048; }
QListWidget::item:hover { background: #edf9f6; border-color: #9edccc; }
QListWidget::item:selected { background: #d5f8ef; border-color: #10a98e; color: #075c4e; }
QFrame#featureTile { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f0f7fb); border: 1px solid #d9e5ef; border-radius: 12px; }
QFrame#infoIconWrap { background: #edf5fb; border: 1px solid #d9e6f0; border-radius: 21px; }
QFrame#featureIconWrap { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0faf3, stop:1 #d6f1ed); border: 1px solid #c8ebe2; border-radius: 11px; }
QLabel#avatar { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d8f8ef, stop:1 #cceeea); color: #008e78; border: 1px solid #b6e7db; border-radius: 35px; font-size: 31px; font-weight: 800; }
QFrame#infoDivider { background: #dce6ef; border: 0; }
QLabel#infoCardTitle { color: #172b42; font-size: 18px; font-weight: 750; }
QLabel#infoCardTitleSmall { color: #172b42; font-size: 16px; font-weight: 750; }
QLabel#infoStepTitle { color: #213850; font-size: 12px; font-weight: 750; }
QLabel#infoStepDescription { color: #58718a; font-size: 11px; }
QLabel#stepNumber { color: #008e78; font-weight: 800; font-size: 12px; padding-top: 3px; }

"""

# Clean line icons matching the supplied sprite sheet. Icons are embedded as SVG,
# so they remain crisp at different Windows DPI/scaling settings.
ICON_PATHS = {
    "home": '<path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9M9 20v-6h6v6"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5M12 15V3"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.7 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.7-1l-1.7.7-1.4-2.4 1.4-1.1a7 7 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.7-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.7 1l1.7-.7 1.4 2.4-1.4 1.1a7 7 0 0 1 0 2Z"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.1 0l3-3A5 5 0 0 0 13 2.9l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.1 0l-3 3A5 5 0 0 0 11 21.1l1.7-1.7"/>',
    "paste": '<rect x="8" y="3" width="8" height="4" rx="1"/><path d="M8 5H5v16h14V5h-3M9 12h6M9 16h6"/>',
    "inspect": '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "video": '<rect x="3" y="5" width="13" height="14" rx="2"/><path d="m16 10 5-3v10l-5-3"/><path d="m8 9 4 3-4 3z"/>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3l-5.6 2.9 1.1-6.2L3 9.6l6.2-.9z"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M3 10h18"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "play": '<path d="m7 4 13 8-13 8z" fill="currentColor" stroke="none"/>',
    "pause": '<path d="M8 5h3v14H8zM15 5h3v14h-3z" fill="currentColor" stroke="none"/>',
    "stop": '<rect x="5" y="5" width="14" height="14" rx="2" fill="currentColor" stroke="none"/>',
    "audio": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    "edit": '<path d="m15 5 4 4M4 20l4-.8L19 8a2.8 2.8 0 0 0-4-4L4 15z"/>',
    "delete": '<path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14M10 10v6M14 10v6"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5M12 3v12"/>',
    "more": '<circle cx="5" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="19" cy="12" r="1" fill="currentColor"/>',
    "moon": '<path d="M20.5 14A8.5 8.5 0 0 1 10 3.5 8.5 8.5 0 1 0 20.5 14Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7h.01"/>',
    "shield": '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M2 14h4M10 8h4M18 16h4"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.3 17a10 10 0 1 1 17.4 0"/><path d="M6 19h12"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
}

def make_icon(name, color="#35d6b1", size=20):
    body = ICON_PATHS.get(name, ICON_PATHS["info"])
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" color="{color}">{body.replace("currentColor", color)}</g></svg>'.encode()
    renderer = QSvgRenderer(svg)
    pixmap = QPixmap(size, size); pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap); renderer.render(painter); painter.end()
    return QIcon(pixmap)

def icon_label(name, text, object_name="sectionLabel", color="#35d6b1"):
    widget = QWidget(); row = QHBoxLayout(widget); row.setContentsMargins(0,0,0,0); row.setSpacing(9)
    glyph = QLabel(); glyph.setPixmap(make_icon(name, color, 20).pixmap(QSize(20,20))); glyph.setFixedSize(20,20)
    label = QLabel(text); label.setObjectName(object_name)
    row.addWidget(glyph); row.addWidget(label); row.addStretch()
    return widget

def read_json(path, fallback):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError): return fallback

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def fmt_bytes(value):
    if not value: return "Size unknown"
    value = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB": return f"{value:.1f} {unit}"
        value /= 1024

def duration_text(seconds):
    if not seconds: return "Duration unavailable"
    seconds = int(seconds)
    return f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}"

def source_label(url, info=None):
    """Return a readable source name for the completed-download card."""
    info = info or {}
    extractor = str(info.get("extractor_key") or info.get("extractor") or "").lower()
    mapping = {
        "youtube": "YouTube", "youtubeclip": "YouTube", "instagram": "Instagram",
        "twitter": "X", "x": "X", "facebook": "Facebook", "fbwatch": "Facebook",
        "tiktok": "TikTok", "reddit": "Reddit", "pinterest": "Pinterest",
        "vimeo": "Vimeo", "twitch": "Twitch",
        "dailymotion": "Dailymotion", "soundcloud": "SoundCloud", "bilibili": "Bilibili",
    }
    for key, label in mapping.items():
        if extractor == key or extractor.startswith(key):
            return label
    try:
        host = (urllib.parse.urlparse(url).hostname or "").lower()
        host = host.removeprefix("www.")
        if "youtube.com" in host or host == "youtu.be": return "YouTube"
        if "instagram.com" in host: return "Instagram"
        if host in ("x.com", "twitter.com", "t.co"): return "X"
        if "facebook.com" in host or "fb.watch" in host: return "Facebook"
        if "tiktok.com" in host: return "TikTok"
        if "reddit.com" in host or host == "redd.it": return "Reddit"
        if "pinterest.com" in host or host == "pin.it": return "Pinterest"
        if "vimeo.com" in host: return "Vimeo"
        if "twitch.tv" in host: return "Twitch"
        if host: return host.split(".")[0].capitalize()
    except Exception:
        pass
    return "Website"

def cache_thumbnail(info, url):
    """Best-effort thumbnail cache. Download failures never fail the media download."""
    try:
        video_id = str(info.get("id") or "item")
        thumb_url = info.get("thumbnail")
        thumbs = info.get("thumbnails") or []
        if thumbs:
            candidates = [t for t in thumbs if t.get("url")]
            if candidates:
                thumb_url = (candidates[-1] if len(candidates) == 1 else max(candidates, key=lambda t: (t.get("width") or 0) * (t.get("height") or 0))).get("url")
        if not thumb_url:
            return ""
        thumb_dir = APP_DIR / "thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)
        # Use a safe, deterministic filename and JPEG extension; Qt detects the actual image format.
        target = thumb_dir / (''.join(c for c in video_id if c.isalnum() or c in '-_')[:100] + '.thumb')
        if not target.exists() or target.stat().st_size == 0:
            request = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0 UniversalDownloader/1.0"})
            with urllib.request.urlopen(request, timeout=8) as response, target.open('wb') as out:
                out.write(response.read(8 * 1024 * 1024))
        return str(target) if target.exists() and target.stat().st_size else ""
    except Exception:
        return ""

class WorkThread(QThread):
    progress = Signal(float, str)
    status = Signal(str)
    inspected = Signal(dict)
    succeeded = Signal(dict)
    failed = Signal(str)
    def __init__(self, mode, **kwargs):
        super().__init__(); self.mode = mode; self.kwargs = kwargs
    def run(self):
        try:
            if yt_dlp is None: raise RuntimeError("yt-dlp is not installed. Run: python -m pip install -U yt-dlp")
            if self.mode == "inspect": self._inspect()
            else: self._download()
        except Exception as e:
            # Keep a full traceback for errors raised inside yt-dlp, which often
            # hides the useful call stack behind a short GUI error message.
            try:
                APP_DIR.mkdir(parents=True, exist_ok=True)
                log_path = APP_DIR / "debug.log"
                with log_path.open("a", encoding="utf-8") as log:
                    log.write("\n" + "=" * 80 + "\n")
                    log.write(f"Timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
                    log.write(f"Mode: {self.mode}\nURL: {self.kwargs.get('url', '')}\n")
                    log.write(traceback.format_exc())
                    log.write("\n")
                self.failed.emit(f"{e}\n\nFull diagnostic log saved to:\n{log_path}")
            except Exception:
                self.failed.emit(f"{e}\n\nCould not write diagnostic log.\n{traceback.format_exc()}")
    def _inspect(self):
        url = self.kwargs['url']
        opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
        }
        opts.update(get_site_auth_options(url))
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        seen, rows = set(), []
        for f in info.get("formats", []):
            h, ext = f.get("height"), f.get("ext", "?")
            video = f.get("vcodec") not in (None, "none")
            audio = f.get("acodec") not in (None, "none")
            if video and h:
                key = (h, ext, audio)
                if key not in seen:
                    seen.add(key); rows.append((h, ext, audio, f.get("filesize") or f.get("filesize_approx")))
        rows.sort(key=lambda x: x[0], reverse=True)
        self.inspected.emit({"title": info.get("title", "Untitled"), "uploader": info.get("uploader") or info.get("channel") or "Unknown uploader", "duration": info.get("duration"), "views": info.get("view_count"), "formats": rows[:12], "extractor_key": info.get("extractor_key") or info.get("extractor") or ""})
    def _download(self):
        url, folder, quality, outformat = self.kwargs['url'], Path(self.kwargs['folder']), self.kwargs['quality'], self.kwargs['outformat']
        folder.mkdir(parents=True, exist_ok=True)
        limit = QUALITIES[quality]
        mp3, m4a, mp4 = outformat.startswith("MP3"), outformat.startswith("M4A"), outformat.startswith("MP4")
        ext = "mp4" if mp4 else "mp3" if mp3 else "m4a" if m4a else "mkv" if outformat.startswith("MKV") else "webm"
        ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
        if (mp4 or mp3 or m4a) and not ffmpeg:
            raise RuntimeError("This output format requires FFmpeg. Install a full FFmpeg build, add its bin folder to PATH, and restart the app. Download: https://ffmpeg.org/download.html")
        fmt = "bestaudio/best" if (mp3 or m4a) else ("bestvideo*+bestaudio/best" if limit is None else f"bestvideo*[height<={limit}]+bestaudio/best[height<={limit}]/best[height<={limit}]")
        temp = Path(tempfile.mkdtemp(prefix="universal_downloader_", dir=str(folder))) if mp4 else None
        outtmpl = str(temp / "%(title).160B [%(id)s].%(ext)s") if temp else str(folder / "%(title).160B [%(id)s].%(ext)s")
        last_emit = {"time": 0.0, "pct": -1.0, "max_pct": 0.0}
        def hook(d):
            if d.get('status') == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate'); got = d.get('downloaded_bytes', 0)
                raw_pct = got / total * 100 if total else 0.0
                # Estimates can change during a download. Keep the displayed bar monotonic
                # and throttle UI signals so Qt isn't flooded with tiny progress updates.
                last_emit["max_pct"] = max(last_emit["max_pct"], raw_pct)
                pct = min(74.0, last_emit["max_pct"] * 0.74)
                now = time.monotonic()
                speed, eta = d.get('speed'), d.get('eta')
                text = f"{pct:.1f}%"
                if speed: text += f"  •  {speed/1048576:.2f} MB/s"
                if eta is not None: text += f"  •  ETA {eta}s"
                if pct - last_emit["pct"] >= 0.25 or now - last_emit["time"] >= 0.35:
                    self.progress.emit(pct, text)
                    last_emit["time"], last_emit["pct"] = now, pct
            elif d.get('status') == 'finished':
                self.progress.emit(75.0, "Download transferred — preparing output…")
                self.status.emit("Download transferred — preparing output…")
        opts = {"format": fmt, "outtmpl": outtmpl, "noplaylist": True, "progress_hooks": [hook], "quiet": True, "no_warnings": True, "windowsfilenames": True, "overwrites": False, "continuedl": True, "concurrent_fragment_downloads": 8, "retries": 10, "fragment_retries": 10, "socket_timeout": 30, "buffersize": 1024 * 1024}
        # Reddit and Pinterest may require a signed-in browser session.
        # Only those sites receive Chrome cookie options.
        opts.update(get_site_auth_options(url))
        # Optional aria2c acceleration for direct HTTP downloads; ordinary yt-dlp remains the fallback.
        aria2c = shutil.which("aria2c")
        if aria2c:
            opts["external_downloader"] = {"http": aria2c, "https": aria2c}
            opts["external_downloader_args"] = {"aria2c": ["-x", "16", "-s", "16", "-k", "1M"]}
        if mp3: opts['postprocessors'] = [{"key":"FFmpegExtractAudio", "preferredcodec":"mp3", "preferredquality":"0"}]
        elif m4a: opts['postprocessors'] = [{"key":"FFmpegExtractAudio", "preferredcodec":"m4a"}]
        elif mp4: opts['merge_output_format'] = 'mkv'
        elif ext in ('mkv','webm'): opts['merge_output_format'] = ext
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                prepared = Path(ydl.prepare_filename(info))
            if mp4:
                ignored = {'.part','.ytdl','.json','.jpg','.jpeg','.png','.webp','.vtt','.srt'}
                candidates = [p for p in temp.iterdir() if p.is_file() and p.suffix.lower() not in ignored]
                if not candidates: raise RuntimeError("Download finished, but no media file was found for conversion.")
                source = max(candidates, key=lambda p:p.stat().st_size)
                safe = sanitize_filename(info.get('title') or 'video', restricted=False) if sanitize_filename else 'video'
                base = f"{safe[:140]} [{info.get('id') or 'download'}]"
                dest = folder / f"{base}.mp4"; n = 2
                while dest.exists(): dest = folder / f"{base} ({n}).mp4"; n += 1
                if not ffprobe:
                    raise RuntimeError("FFprobe is missing; install a full FFmpeg build that includes ffprobe.exe.")
                # Probe codecs first. Compatible H.264 sources can be remuxed instead of re-encoded,
                # which is dramatically faster and avoids needless quality loss.
                media_info = probe_media(source)
                strategy = choose_mp4_strategy(media_info)
                copy_video = strategy['video_copy']
                mode_label = {'stream-copy':'Remuxing compatible streams (fast, no re-encode)', 'audio-re-encode':'Copying video; converting audio to AAC', 'full-re-encode':'Converting video to H.264 and audio to AAC'}[strategy['mode']]
                self.status.emit(mode_label)
                cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-map', '0:v:0?', '-map', '0:a:0?']
                if strategy['video_copy']:
                    cmd += ['-c:v', 'copy']
                else:
                    # Software fallback is deliberately reliable; hardware encoders are detected in Settings/diagnostics only.
                    cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-threads', '0', '-pix_fmt', 'yuv420p']
                if strategy['audio_copy']:
                    cmd += ['-c:a', 'copy']
                else:
                    cmd += ['-c:a', 'aac', '-b:a', '192k']
                cmd += ['-movflags', '+faststart', '-progress', 'pipe:1', '-nostats', str(dest)]
                # Parse FFmpeg progress live so the UI remains responsive during long conversions.
                with tempfile.TemporaryFile(mode='w+b') as err_file:
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err_file, text=True, encoding='utf-8', errors='replace', bufsize=1)
                    duration_us = max(1, int(float(info.get('duration') or 0) * 1_000_000))
                    for line in proc.stdout:
                        if line.startswith('out_time_ms='):
                            try:
                                done_us = int(line.split('=', 1)[1].strip())
                                ratio = max(0.0, min(1.0, done_us / duration_us))
                                pct = 75.0 + ratio * 24.0
                                self.progress.emit(pct, f'Converting to H.264 MP4… {ratio * 100:.0f}%')
                            except ValueError:
                                pass
                    proc.wait()
                    err_file.seek(0)
                    ffmpeg_error = err_file.read().decode('utf-8', errors='replace')
                if proc.returncode or not dest.exists() or not dest.stat().st_size:
                    dest.unlink(missing_ok=True); raise RuntimeError("H.264 MP4 conversion failed.\n\n" + (ffmpeg_error or "FFmpeg could not create the output.")[-2200:])
                verify = subprocess.run([ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(dest)], capture_output=True, text=True, encoding='utf-8', errors='replace')
                if verify.returncode or verify.stdout.strip().lower() != 'h264':
                    dest.unlink(missing_ok=True); raise RuntimeError(f"MP4 verification failed: expected H.264, found {verify.stdout.strip() or 'unknown'}.")
                final = dest
            else:
                final = Path(info.get('filepath') or prepared)
                if not final.exists():
                    options = [p for p in folder.glob(f"*{info.get('id','')}*") if p.is_file()]
                    if options: final = max(options, key=lambda p:p.stat().st_mtime)
                if not final.exists(): raise RuntimeError("The download completed but the final file could not be located.")
            thumb_path = cache_thumbnail(info, url)
            record = {"title": info.get('title', final.name), "path": str(final), "url": url,
                      "source": normalize_source(url, info.get("extractor_key") or info.get("extractor")), "thumbnail_path": thumb_path,
                      "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "downloaded_at": datetime.now().isoformat(timespec="seconds"), "format": ext.upper(), "resolution": str(info.get("height") or "") + ("p" if info.get("height") else "") }
            self.succeeded.emit(record)
        finally:
            if temp: shutil.rmtree(temp, ignore_errors=True)

class DownloadRow(QFrame):
    remove_requested = Signal(int)
    def __init__(self, record, parent=None):
        super().__init__(parent); self.record = record; self.window_ref = parent if hasattr(parent, 'show_toast') else None; self.setObjectName('historyCard')
        row = QHBoxLayout(self); row.setContentsMargins(16, 13, 16, 13); row.setSpacing(14)
        self.thumb = QToolButton(); self.thumb.setFixedSize(88, 58); self.thumb.setCursor(Qt.PointingHandCursor)
        self.thumb.setToolTip('Play video / open downloaded file'); self.thumb.setIcon(make_icon('play', '#35d6b1', 20)); self.thumb.setIconSize(QSize(20,20))
        self.thumb.setStyleSheet('QToolButton { background: #193247; border: 1px solid #24445a; border-radius: 8px; padding: 0; } QToolButton:hover { border: 1px solid #35d6b1; }')
        thumb_path = record.get('thumbnail_path', '')
        if thumb_path and Path(thumb_path).exists():
            pix = QPixmap(thumb_path)
            if not pix.isNull():
                self.thumb.setIcon(QIcon(pix.scaled(88, 58, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
                self.thumb.setIconSize(QSize(88,58))
        self.thumb.clicked.connect(self.open_file)
        row.addWidget(self.thumb)
        info = QVBoxLayout(); info.setSpacing(7)
        title = QLabel(f"[{record.get('format','MP4')}]  {record.get('title','Untitled')}"); title.setObjectName('sectionLabel'); title.setWordWrap(True)
        info.addWidget(title)
        source = record.get('source_label') or source_label(record.get('url', ''))
        if not record.get('source_label') and record.get('source'):
            from history_store import source_display_name
            source = source_display_name(record.get('source'))
        meta = QLabel(f"▦  {record.get('date','')}    ▣  {record.get('format','?')}    ✓  Completed    •  {source}")
        meta.setObjectName('muted'); meta.setWordWrap(True); info.addWidget(meta); row.addLayout(info, 1)
        play = QPushButton(); play.setIcon(make_icon('play', '#9bb4cf', 17)); play.setObjectName('iconButton'); play.setToolTip('Open file'); play.clicked.connect(self.open_file); row.addWidget(play)
        folder = QPushButton(); folder.setIcon(make_icon('folder', '#9bb4cf', 17)); folder.setObjectName('iconButton'); folder.setToolTip('Open containing folder'); folder.clicked.connect(self.open_folder); row.addWidget(folder)
        copy_url = QPushButton(); copy_url.setIcon(make_icon('copy', '#9bb4cf', 17)); copy_url.setObjectName('iconButton'); copy_url.setToolTip('Copy source URL'); copy_url.clicked.connect(self.copy_source_url); row.addWidget(copy_url)
        remove = QPushButton(); remove.setIcon(make_icon('delete', '#9bb4cf', 17)); remove.setObjectName('iconButton'); remove.setToolTip('Remove from history (keeps the file)'); remove.clicked.connect(lambda: self.remove_requested.emit(int(self.record.get('id', 0)))); row.addWidget(remove)
        more = QPushButton(); more.setIcon(make_icon('more', '#9bb4cf', 17)); more.setObjectName('iconButton'); more.setToolTip('Show file path'); more.clicked.connect(self.show_path); row.addWidget(more)
    def copy_source_url(self):
        if self.window_ref: self.window_ref.copy_text(self.record.get('url',''), 'Source URL copied')
        else: QApplication.clipboard().setText(self.record.get('url',''))
    def open_file(self):
        p = Path(self.record.get('path',''))
        if not p.exists(): QMessageBox.warning(self, translate('File not found', self.window_ref.language if self.window_ref else 'en'), translate('File is no longer at:', self.window_ref.language if self.window_ref else 'en')+f"\n{p}"); return
        open_path(p)
    def open_folder(self):
        p = Path(self.record.get('path','')).parent
        p.mkdir(parents=True, exist_ok=True); open_path(p)
    def show_path(self): QMessageBox.information(self, translate('Saved file', self.window_ref.language if self.window_ref else 'en'), self.record.get('path',''))

def open_path(path):
    path = str(path)
    try:
        if sys.platform == 'win32': os.startfile(path)
        elif sys.platform == 'darwin': subprocess.Popen(['open', path])
        else: subprocess.Popen(['xdg-open', path])
    except Exception as e: QMessageBox.warning(None, 'Could not open', str(e))

class ToastNotification(QFrame):
    """Non-blocking, theme-aware toast anchored to the app content window."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toastNotification")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setVisible(False)
        self.setMinimumHeight(44)
        self.setMaximumWidth(520)
        row = QHBoxLayout(self); row.setContentsMargins(15, 9, 17, 9); row.setSpacing(10)
        self.icon_label = QLabel("✓"); self.icon_label.setObjectName("toastIcon")
        self.message_label = QLabel(""); self.message_label.setWordWrap(True); self.message_label.setObjectName("toastMessage")
        row.addWidget(self.icon_label); row.addWidget(self.message_label, 1)
        self.effect = QGraphicsOpacityEffect(self); self.effect.setOpacity(0.0); self.setGraphicsEffect(self.effect)
        self._group = None; self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.timeout.connect(self.dismiss)
        self._dark = True; self._generation = 0

    def show_message(self, message, kind="success", duration=2500, dark=True):
        self._generation += 1
        self._timer.stop()
        if self._group:
            self._group.stop(); self._group.deleteLater(); self._group = None
        palette = {"success": ("✓", "#25c5a2"), "info": ("i", "#50a7ef"), "warning": ("!", "#e5aa43"), "error": ("×", "#ef6b73")}
        symbol, accent = palette.get(kind, palette["info"])
        self.icon_label.setText(symbol); self.icon_label.setStyleSheet(f"color:{accent}; font-size:16px; font-weight:800;")
        bg, border, fg = ("#132538", "#29475d", "#f1f7fd") if dark else ("#ffffff", "#d6e3ee", "#172b42")
        self.setStyleSheet(f"QFrame#toastNotification {{ background:{bg}; border:1px solid {border}; border-radius:13px; }} QLabel#toastMessage {{ color:{fg}; font-size:12px; font-weight:600; }}")
        self.message_label.setText(message); self.adjustSize()
        self.setFixedWidth(min(520, max(220, self.sizeHint().width())))
        self._position(); self.setVisible(True); self.raise_()
        start = self.pos() + QPoint(0, 12); end = self.pos()
        self.move(start); self.effect.setOpacity(0.0)
        group = QParallelAnimationGroup(self); self._group = group
        fade = QPropertyAnimation(self.effect, b"opacity", group); fade.setDuration(220); fade.setStartValue(0.0); fade.setEndValue(1.0); fade.setEasingCurve(QEasingCurve.OutCubic)
        slide = QPropertyAnimation(self, b"pos", group); slide.setDuration(220); slide.setStartValue(start); slide.setEndValue(end); slide.setEasingCurve(QEasingCurve.OutCubic)
        group.start(); self._timer.start(max(700, int(duration)))

    def _position(self):
        if not self.parentWidget(): return
        parent = self.parentWidget(); self.adjustSize()
        self.move(max(12, (parent.width() - self.width()) // 2), max(12, parent.height() - self.height() - 22))

    def reposition(self):
        if self.isVisible(): self._position(); self.raise_()

    def dismiss(self):
        if not self.isVisible(): return
        if self._group: self._group.stop(); self._group.deleteLater(); self._group = None
        group = QParallelAnimationGroup(self); self._group = group
        fade = QPropertyAnimation(self.effect, b"opacity", group); fade.setDuration(190); fade.setStartValue(self.effect.opacity()); fade.setEndValue(0.0); fade.setEasingCurve(QEasingCurve.InCubic)
        slide = QPropertyAnimation(self, b"pos", group); slide.setDuration(190); slide.setStartValue(self.pos()); slide.setEndValue(self.pos() + QPoint(0, 8)); slide.setEasingCurve(QEasingCurve.InCubic)
        generation = self._generation
        group.finished.connect(lambda g=generation: self.hide() if g == self._generation else None)
        group.start()


class DownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(translate('Universal Downloader', getattr(self, 'language', 'en'))); self.resize(1280, 850); self.setMinimumSize(620, 480)
        self.logo_path = Path(__file__).with_name('universal_downloader_logo.png')
        self.icon_path = Path(__file__).with_name('universal_downloader_logo.ico')
        if self.icon_path.exists(): self.setWindowIcon(QIcon(str(self.icon_path)))
        elif self.logo_path.exists(): self.setWindowIcon(QIcon(str(self.logo_path)))
        self.settings = read_json(CONFIG_FILE, {}); self.language = self.settings.get('language', 'en') if self.settings.get('language') in LANGUAGES else 'en'; self.history_store = HistoryStore(DATABASE_FILE)
        legacy_history = read_json(HISTORY_FILE, [])
        if isinstance(legacy_history, list): self.history_store.import_records(legacy_history)
        self.history = self.history_store.list(order='Latest first')
        self.dark = self.settings.get('theme','dark') != 'light'; self.busy = False; self.worker = None
        self.download_queue = read_json(QUEUE_FILE, []) if isinstance(read_json(QUEUE_FILE, []), list) else []
        self.current_queue_item = None
        for _item in self.download_queue:
            if _item.get('status') == 'Downloading': _item['status'] = 'Queued'
        save_json(QUEUE_FILE, self.download_queue)
        self.save_dir = self.settings.get('save_dir', str(Path.home()/'Videos'/'Universal Downloader'))
        self.current_page = 'download'; self._build(); self.toast = ToastNotification(self.centralWidget()); self.apply_theme(); self.refresh_history(); self.apply_language()
    def _build(self):
        root = QWidget(); root.setObjectName('root'); self.setCentralWidget(root)
        outer = QHBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        self.sidebar = QFrame(); self.sidebar.setObjectName('sidebar'); self.sidebar.setMinimumWidth(66); self.sidebar.setMaximumWidth(218); self.sidebar.setFixedWidth(198)
        side = QVBoxLayout(self.sidebar); side.setContentsMargins(16,20,16,18); side.setSpacing(6)
        brand = QHBoxLayout(); brand.setSpacing(9)
        logo = QLabel(); logo.setFixedSize(42,42); logo.setAlignment(Qt.AlignCenter)
        if self.logo_path.exists(): logo.setPixmap(QPixmap(str(self.logo_path)).scaled(42,42,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        else: logo.setPixmap(make_icon('play', '#35d6b1', 34).pixmap(QSize(34,34)))
        brand.addWidget(logo)
        name = QLabel('Universal\nDownloader'); name.setObjectName('brand'); self.brand_name = name; self.sidebar_logo = logo; brand.addWidget(name); brand.addStretch()
        side.addLayout(brand); side.addSpacing(24)
        self.nav_download = QPushButton('Download'); self.nav_download.setIcon(make_icon('download', '#35d6b1', 20)); self.nav_download.setIconSize(QSize(20,20)); self.nav_download.setObjectName('nav'); self.nav_download.clicked.connect(lambda:self.show_page('download')); side.addWidget(self.nav_download)
        self.nav_history = QPushButton('Completed'); self.nav_history.setIcon(make_icon('check-circle', '#9bb4cf', 20)); self.nav_history.setIconSize(QSize(20,20)); self.nav_history.setObjectName('nav'); self.nav_history.clicked.connect(lambda:self.show_page('history')); side.addWidget(self.nav_history)
        self.nav_info = QPushButton('About & Features'); self.nav_info.setIcon(make_icon('info', '#9bb4cf', 20)); self.nav_info.setIconSize(QSize(20,20)); self.nav_info.setObjectName('nav'); self.nav_info.clicked.connect(lambda:self.show_page('info')); side.addWidget(self.nav_info)
        side.addStretch()
        self.side_layout = side
        self.nav_buttons = [(self.nav_download, 'Download', 'download'), (self.nav_history, 'Completed', 'check-circle'), (self.nav_info, 'About & Features', 'info')]
        outer.addWidget(self.sidebar)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.NoFrame); self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded); self.scroll.setAlignment(Qt.AlignTop)
        self.body = QWidget(); self.body.setObjectName('scrollBody'); self.body_layout = QVBoxLayout(self.body); self.body_layout.setContentsMargins(28,24,28,22); self.body_layout.setSpacing(0)
        self.scroll.setWidget(self.body); outer.addWidget(self.scroll,1)
        # Page header
        header = QHBoxLayout(); header.setContentsMargins(0,0,0,24)
        header_logo = QLabel(); header_logo.setFixedSize(56,56); header_logo.setAlignment(Qt.AlignCenter)
        if self.logo_path.exists(): header_logo.setPixmap(QPixmap(str(self.logo_path)).scaled(56,56,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        else: header_logo.setPixmap(make_icon('play', '#35d6b1', 42).pixmap(QSize(42,42)))
        header.addWidget(header_logo); header.addSpacing(12)
        titlebox = QVBoxLayout(); titlebox.setSpacing(4)
        title = QLabel('Universal Downloader'); title.setObjectName('pageTitle'); self.header_title = title; titlebox.addWidget(title)
        subtitle = QLabel('Download   •   Convert   •   Organize'); subtitle.setObjectName('subtitle'); titlebox.addWidget(subtitle)
        header.addLayout(titlebox); header.addStretch()
        self.language_combo = QComboBox(); self.language_combo.setObjectName('languageSelector'); self.language_combo.setToolTip('Language & Region')
        for code, label in LANGUAGES.items(): self.language_combo.addItem(label, code)
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(self.language))); self.language_combo.currentIndexChanged.connect(self.change_language); header.addWidget(self.language_combo, 0, Qt.AlignTop)
        self.theme_btn = QPushButton('Dark mode'); self.theme_btn.setIcon(make_icon('moon', '#c6d6e8', 17)); self.theme_btn.setObjectName('theme'); self.theme_btn.clicked.connect(self.toggle_theme); header.addWidget(self.theme_btn,0,Qt.AlignTop)
        self.body_layout.addLayout(header)
        self.pages = QStackedWidget(); self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum); self.pages.setMinimumHeight(0); self.body_layout.addWidget(self.pages, 0, Qt.AlignTop)
        self.download_page = QWidget(); self.download_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum); self.download_layout = QVBoxLayout(self.download_page); self.download_layout.setContentsMargins(0,0,0,0); self.download_layout.setSpacing(14); self.download_layout.setAlignment(Qt.AlignTop)
        self.history_page = QWidget(); self.history_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum); self.history_layout = QVBoxLayout(self.history_page); self.history_layout.setContentsMargins(0,0,0,0); self.history_layout.setSpacing(14); self.history_layout.setAlignment(Qt.AlignTop)
        self.info_page = QWidget(); self.info_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum); self.info_layout = QVBoxLayout(self.info_page); self.info_layout.setContentsMargins(0,0,0,0); self.info_layout.setSpacing(18); self.info_layout.setAlignment(Qt.AlignTop)
        self.info_layout.setContentsMargins(2, 2, 2, 8)
        self.pages.addWidget(self.download_page); self.pages.addWidget(self.history_page); self.pages.addWidget(self.info_page)
        self._build_download_page(); self._build_history_page(); self._build_info_page(); self.show_page('download')
    def _card(self, parent_layout, name='card', padding=20):
        frame = QFrame(); frame.setObjectName(name); layout = QVBoxLayout(frame); layout.setContentsMargins(padding,padding,padding,padding); layout.setSpacing(12); parent_layout.addWidget(frame); return frame, layout
    def _build_download_page(self):
        card, lay = self._card(self.download_layout, padding=22)
        lab = icon_label('link', 'Video URL'); lay.addWidget(lab)
        urlrow = QGridLayout(); urlrow.setHorizontalSpacing(10); urlrow.setVerticalSpacing(8); self.url_grid = urlrow
        self.url_input = QLineEdit(); self.url_input.setPlaceholderText('Paste a video URL here…'); self.url_input.returnPressed.connect(self.inspect)
        self.paste_btn = QPushButton('Paste'); self.paste_btn.setIcon(make_icon('paste', '#effffb', 17)); self.paste_btn.setObjectName('paste'); self.paste_btn.clicked.connect(self.paste_url)
        self.inspect_btn = QPushButton('Inspect'); self.inspect_btn.setIcon(make_icon('inspect', '#9bb4cf', 17)); self.inspect_btn.clicked.connect(self.inspect); self.url_controls = (self.url_input, self.paste_btn, self.inspect_btn); self._set_url_layout(False)
        lay.addLayout(urlrow)
        fields = QGridLayout(); fields.setHorizontalSpacing(12); fields.setVerticalSpacing(10)
        self.format_combo = QComboBox()
        for _value in FORMATS: self.format_combo.addItem(_value, _value)
        self.format_combo.currentTextChanged.connect(self.format_changed)
        self.quality_combo = QComboBox()
        for _value in QUALITIES: self.quality_combo.addItem(_value, _value)
        self.location_input = QLineEdit(self.save_dir); self.location_input.setToolTip('Download destination folder')
        f1, l1 = self._field(fields, 'video', 'Output Format'); l1.addWidget(self.format_combo)
        f2, l2 = self._field(fields, 'star', 'Max Resolution'); l2.addWidget(self.quality_combo)
        f3, l3 = self._field(fields, 'folder', 'Save Location'); self.field_cards = (f1, f2, f3); self.fields_layout = fields; locrow = QHBoxLayout(); locrow.setSpacing(6); locrow.addWidget(self.location_input,1)
        browse = QPushButton(); browse.setIcon(make_icon('folder', '#9bb4cf', 17)); browse.setObjectName('iconButton'); browse.setToolTip('Choose folder'); browse.clicked.connect(self.browse); locrow.addWidget(browse)
        more = QPushButton(); more.setIcon(make_icon('more', '#9bb4cf', 17)); more.setObjectName('iconButton'); more.setToolTip('Open save folder'); more.clicked.connect(self.open_download_folder); locrow.addWidget(more); l3.addLayout(locrow)
        self._set_fields_columns(3)
        lay.addLayout(fields)
        info_card, info = self._card(self.download_layout, padding=17)
        ilab = icon_label('video', 'Video Details'); info.addWidget(ilab)
        self.meta_label = QLabel('Inspect a link to see its title, duration, uploader and available formats.'); self.meta_label.setObjectName('muted'); self.meta_label.setWordWrap(True); info.addWidget(self.meta_label)
        self.formats_label = QLabel(''); self.formats_label.setObjectName('tinyMuted'); self.formats_label.setWordWrap(True); info.addWidget(self.formats_label)
        action_row = QHBoxLayout(); action_row.setSpacing(10)
        self.download_btn = QPushButton('Add to Queue & Start'); self.download_btn.setIcon(make_icon('download', '#031b17', 20)); self.download_btn.setObjectName('primary'); self.download_btn.clicked.connect(self.start_download); action_row.addWidget(self.download_btn, 2)
        self.add_urls_btn = QPushButton('Add Multiple URLs'); self.add_urls_btn.setToolTip('Paste multiple URLs, one per line'); self.add_urls_btn.clicked.connect(self.add_multiple_urls); action_row.addWidget(self.add_urls_btn, 1)
        self.download_layout.addLayout(action_row)
        queue_head = QHBoxLayout(); queue_title = QLabel('Download queue'); queue_title.setObjectName('sectionLabel'); queue_head.addWidget(queue_title); queue_head.addStretch()
        self.queue_status = QLabel('0 queued'); self.queue_status.setObjectName('muted'); queue_head.addWidget(self.queue_status)
        self.clear_queue_btn = QPushButton('Clear queued'); self.clear_queue_btn.clicked.connect(self.clear_queue); queue_head.addWidget(self.clear_queue_btn); self.download_layout.addLayout(queue_head)
        self.queue_list = QListWidget(); self.queue_list.setMinimumHeight(76); self.queue_list.setMaximumHeight(170); self.queue_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self.queue_list.setUniformItemSizes(True); self.queue_list.setSpacing(2); self.queue_list.setToolTip('Queued URLs are saved locally and restored when the app restarts.'); self.download_layout.addWidget(self.queue_list)
        self.refresh_queue_view()
        self.queue_list.itemDoubleClicked.connect(self.retry_queue_item)
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); self.download_layout.addWidget(self.progress)
        self.status_label = QLabel('Ready — paste a video link to begin'); self.status_label.setObjectName('tinyMuted'); self.download_layout.addWidget(self.status_label)
        disclaimer = QLabel('Download only content you own or have permission to save. Private, DRM-protected or access-restricted media isn’t supported.'); disclaimer.setObjectName('tinyMuted'); disclaimer.setWordWrap(True); disclaimer.setContentsMargins(2,3,0,0); self.download_layout.addWidget(disclaimer)
        self.download_layout.addSpacing(18)
        # The reference puts the completed downloads section directly below the download form.
        histhead = QHBoxLayout(); htitle = QLabel('Completed downloads'); htitle.setObjectName('pageTitle'); htitle.setStyleSheet('font-size:22px;'); histhead.addWidget(htitle); histhead.addStretch()
        open_btn = QPushButton('Open downloads folder'); open_btn.setIcon(make_icon('folder', '#9bb4cf', 17)); open_btn.clicked.connect(self.open_download_folder); histhead.addWidget(open_btn)
        self.clear_inline_btn = QPushButton('Clear history'); self.clear_inline_btn.setIcon(make_icon('delete', '#9bb4cf', 16)); self.clear_inline_btn.clicked.connect(self.clear_history); histhead.addWidget(self.clear_inline_btn); self.download_layout.addLayout(histhead)
        self.inline_history = QVBoxLayout(); self.inline_history.setSpacing(10); self.download_layout.addLayout(self.inline_history)
        foot = QHBoxLayout(); self.history_count = QLabel('✓  0 downloads completed'); self.history_count.setObjectName('muted'); foot.addWidget(self.history_count); foot.addStretch()
        allcaught = QLabel('✦  All caught up!'); allcaught.setObjectName('tinyMuted'); foot.addWidget(allcaught); self.download_layout.addLayout(foot)
    def _field(self, row, icon_name, title):
        frame = QFrame(); frame.setObjectName('fieldCard'); layout = QVBoxLayout(frame); layout.setContentsMargins(14,12,14,13); layout.setSpacing(8)
        label = icon_label(icon_name, title, 'muted'); layout.addWidget(label); return frame, layout
    def _build_history_page(self):
        head = QHBoxLayout(); title = QLabel('Completed downloads'); title.setObjectName('pageTitle'); title.setStyleSheet('font-size:24px;'); head.addWidget(title); head.addStretch()
        btn = QPushButton('Open downloads folder'); btn.setIcon(make_icon('folder', '#9bb4cf', 17)); btn.clicked.connect(self.open_download_folder); head.addWidget(btn)
        clear = QPushButton('Clear history'); clear.setIcon(make_icon('delete', '#9bb4cf', 16)); clear.clicked.connect(self.clear_history); head.addWidget(clear); self.history_layout.addLayout(head)
        desc = QLabel('Search and filter your local download library. Removing an entry never deletes the actual video.'); desc.setObjectName('muted'); self.history_layout.addWidget(desc)
        filters = QHBoxLayout(); filters.setSpacing(10)
        self.library_search = QLineEdit(); self.library_search.setPlaceholderText('Search titles or filenames…'); self.library_search.setClearButtonEnabled(True); self.library_search.textChanged.connect(self.refresh_history)
        self.source_filter = QComboBox(); self.source_filter.setMinimumWidth(150); self.source_filter.currentTextChanged.connect(self.refresh_history)
        self.sort_filter = QComboBox(); self.sort_filter.addItem('Latest first', 'Latest first'); self.sort_filter.addItem('Oldest first', 'Oldest first'); self.sort_filter.currentTextChanged.connect(self.refresh_history)
        self.clear_filters_btn = QPushButton('Clear filters'); self.clear_filters_btn.clicked.connect(self.clear_library_filters)
        filters.addWidget(self.library_search, 1); filters.addWidget(self.source_filter); filters.addWidget(self.sort_filter); filters.addWidget(self.clear_filters_btn); self.history_layout.addLayout(filters)
        self.library_count = QLabel(''); self.library_count.setObjectName('muted'); self.history_layout.addWidget(self.library_count)
        self.full_history = QVBoxLayout(); self.full_history.setSpacing(10); self.history_layout.addLayout(self.full_history); self.history_layout.addStretch()
    def _build_info_page(self):
        # Reference-inspired About page: editorial heading, two-column cards,
        # compact feature tiles, workflow timeline, creator credit and footer.
        self.info_layout.setSpacing(18)
        self.info_layout.setContentsMargins(2, 2, 2, 8)

        eyebrow = QLabel('A B O U T')
        eyebrow.setObjectName('eyebrow')
        
        self.info_layout.addWidget(eyebrow)

        hero_title = QLabel('A simpler way to save media')
        hero_title.setObjectName('pageTitle')
        
        self.info_layout.addWidget(hero_title)

        intro_copy = QLabel('Universal Downloader helps you fetch, convert and organize your media files —\nquickly, easily and without unnecessary steps.')
        intro_copy.setObjectName('muted')
        
        intro_copy.setWordWrap(True)
        self.info_layout.addWidget(intro_copy)

        columns = QHBoxLayout()
        self.info_columns = columns
        columns.setSpacing(18)
        left_col = QVBoxLayout(); left_col.setSpacing(14); self.info_left_col = left_col
        right_col = QVBoxLayout(); right_col.setSpacing(14); self.info_right_col = right_col
        columns.addLayout(left_col, 13)
        columns.addLayout(right_col, 10)
        self.info_layout.addLayout(columns, 1)

        # Left: brand introduction.
        intro_card, intro_box = self._card(left_col, padding=22)
        intro_row = QHBoxLayout(); intro_row.setSpacing(20)
        mark = QLabel(); mark.setFixedSize(94,94); mark.setAlignment(Qt.AlignCenter)
        if self.logo_path.exists():
            mark.setPixmap(QPixmap(str(self.logo_path)).scaled(88,88,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        else:
            mark.setPixmap(make_icon('download', '#35d6b1', 54).pixmap(QSize(54,54)))
        intro_row.addWidget(mark, 0, Qt.AlignVCenter)
        intro_text = QVBoxLayout(); intro_text.setSpacing(8)
        intro_heading = QLabel('Made to make saving media simpler')
        intro_heading.setObjectName('infoCardTitle')
        intro_desc = QLabel('Universal Downloader brings link inspection, format selection, downloading, conversion and file organization into one clean desktop workspace. The goal is to reduce repetitive steps and help you get to your saved media faster.')
        intro_desc.setObjectName('muted'); intro_desc.setWordWrap(True)
        intro_text.addWidget(intro_heading); intro_text.addWidget(intro_desc)
        intro_row.addLayout(intro_text, 1); intro_box.addLayout(intro_row)

        # Left: numbered workflow.
        workflow, workflow_box = self._card(left_col, padding=22)
        workflow_title = QLabel('Built for your workflow')
        workflow_title.setObjectName('sectionLabel'); workflow_title.setStyleSheet('font-size:18px; font-weight:750;')
        workflow_box.addWidget(workflow_title)
        workflow_items = [
            ('link', 'Paste & inspect link', 'Paste a supported public video or media URL. The app uses yt-dlp to identify the source and available media formats.'),
            ('shield', 'Inspect before downloading', 'View the title, uploader, duration, views when available, and a selection of available resolutions and formats.'),
            ('sliders', 'Choose format and quality', 'MP4 conversion probes codecs first: compatible streams are copied, audio-only conversion is used when possible, and video is re-encoded only when needed.'),
            ('gauge', 'Track progress', 'Progress updates are throttled to keep the interface smooth. Speed and ETA appear when the source provides them.'),
            ('folder', 'Keep downloads organized', 'Completed items show a title, thumbnail when available, date, format and detected website. Click the thumbnail to open the saved video or use the folder action to locate it.'),
            ('clock', 'Your history stays local', 'Preferences, download history and cached thumbnails are stored on your computer. Clearing history removes its records, not the downloaded media files.'),
        ]
        for idx, (icon_name, title_text, desc_text) in enumerate(workflow_items, 1):
            item_row = QHBoxLayout(); item_row.setSpacing(13)
            icon_wrap = QFrame(); icon_wrap.setObjectName('infoIconWrap'); icon_wrap.setFixedSize(42,42)
            icon_layout = QVBoxLayout(icon_wrap); icon_layout.setContentsMargins(0,0,0,0)
            icon_label_widget = QLabel(); icon_label_widget.setAlignment(Qt.AlignCenter); icon_label_widget.setPixmap(make_icon(icon_name, '#9bb8d6', 21).pixmap(QSize(21,21))); icon_layout.addWidget(icon_label_widget)
            item_row.addWidget(icon_wrap, 0, Qt.AlignTop)
            number = QLabel(f'{idx:02d}'); number.setFixedWidth(32); number.setObjectName('stepNumber')
            item_row.addWidget(number, 0, Qt.AlignTop)
            text_col = QVBoxLayout(); text_col.setSpacing(3)
            item_title = QLabel(title_text); item_title.setObjectName('infoStepTitle')
            item_desc = QLabel(desc_text); item_desc.setObjectName('infoStepDescription'); item_desc.setWordWrap(True)
            text_col.addWidget(item_title); text_col.addWidget(item_desc); item_row.addLayout(text_col, 1)
            workflow_box.addLayout(item_row)
            if idx != len(workflow_items):
                line = QFrame(); line.setFixedHeight(1); line.setObjectName('infoDivider')
                workflow_box.addWidget(line)

        # Right: feature overview tiles.
        glance, glance_box = self._card(right_col, padding=20)
        glance_title = QLabel('At a glance'); glance_title.setObjectName('infoCardTitle')
        glance_box.addWidget(glance_title)
        tiles = QGridLayout(); tiles.setSpacing(12)
        tile_items = [
            ('link', 'Link inspection', 'Check details before you download.'),
            ('file', 'Format selection', 'MP4, WebM, MKV and more.'),
            ('clock', 'Download tracking', 'Progress, speed and ETA.'),
            ('folder', 'Local history', 'Access your downloads anytime.'),
        ]
        for i, (icon_name, tile_title, tile_desc) in enumerate(tile_items):
            tile = QFrame(); tile.setObjectName('featureTile')
            
            tile_layout = QHBoxLayout(tile); tile_layout.setContentsMargins(12,12,12,12); tile_layout.setSpacing(10)
            tile_icon_frame = QFrame(); tile_icon_frame.setObjectName('featureIconWrap'); tile_icon_frame.setFixedSize(42,42)
            tile_icon_layout = QVBoxLayout(tile_icon_frame); tile_icon_layout.setContentsMargins(0,0,0,0)
            tile_icon = QLabel(); tile_icon.setAlignment(Qt.AlignCenter); tile_icon.setPixmap(make_icon(icon_name, '#20d8ba', 22).pixmap(QSize(22,22))); tile_icon_layout.addWidget(tile_icon)
            tile_layout.addWidget(tile_icon_frame, 0, Qt.AlignTop)
            tile_text = QVBoxLayout(); tile_text.setSpacing(5)
            tl = QLabel(tile_title); tl.setObjectName('infoStepTitle')
            td = QLabel(tile_desc); td.setObjectName('infoStepDescription'); td.setWordWrap(True)
            tile_text.addWidget(tl); tile_text.addWidget(td); tile_layout.addLayout(tile_text, 1)
            tiles.addWidget(tile, i//2, i%2)
        glance_box.addLayout(tiles)

        # Right: developer story and Instagram follow link.
        credit, credit_box = self._card(right_col, padding=22)
        credit_title = QLabel('Created by Arth Awasthi'); credit_title.setObjectName('infoCardTitle')
        credit_box.addWidget(credit_title)
        credit_row = QHBoxLayout(); credit_row.setContentsMargins(0, 2, 0, 2); credit_row.setSpacing(14)
        avatar = QLabel('A'); avatar.setObjectName('avatar'); avatar.setFixedSize(70,70); avatar.setAlignment(Qt.AlignCenter)
        credit_row.addWidget(avatar, 0, Qt.AlignTop)
        credit_copy_col = QVBoxLayout(); credit_copy_col.setSpacing(7)
        credit_name = QLabel('Created by Arth Awasthi'); credit_name.setObjectName('infoCardTitleSmall')
        credit_text = QLabel('Universal Downloader was developed by Arth Awasthi to make everyday video-saving workflows quicker and less cumbersome. Instead of jumping between separate websites and conversion tools, it brings link inspection, quality selection, downloading, conversion and history together in one place — helping you spend less time managing files and more time using your media.')
        credit_text.setObjectName('muted'); credit_text.setWordWrap(True)
        credit_copy_col.addWidget(credit_name); credit_copy_col.addWidget(credit_text); credit_row.addLayout(credit_copy_col, 1)
        credit_box.addLayout(credit_row)
        divider = QFrame(); divider.setObjectName('infoDivider'); divider.setFixedHeight(1); credit_box.addWidget(divider)
        socials = QHBoxLayout(); socials.setSpacing(10)
        insta_icon = QLabel(); insta_icon.setPixmap(make_icon('instagram', '#20d8ba', 22).pixmap(QSize(22,22))); socials.addWidget(insta_icon)
        follow = QLabel('Follow me @arth_lives'); follow.setObjectName('muted'); socials.addWidget(follow); socials.addStretch()
        insta = QPushButton('Instagram  ↗'); insta.setObjectName('paste'); insta.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://www.instagram.com/arth_lives/'))); socials.addWidget(insta)
        credit_box.addLayout(socials)

        footer_line = QFrame(); footer_line.setObjectName('infoDivider'); footer_line.setFixedHeight(1)
        self.info_layout.addWidget(footer_line)
        footer = QHBoxLayout(); footer.setContentsMargins(2, 4, 2, 0); footer.setSpacing(9)
        shield_icon = QLabel(); shield_icon.setPixmap(make_icon('shield', '#9bb8d6', 17).pixmap(QSize(17,17))); footer.addWidget(shield_icon)
        footer_text = QLabel('Only download content you own or have permission to save. Respect creators’ rights.')
        footer_text.setObjectName('tinyMuted'); footer.addWidget(footer_text); footer.addStretch()
        version = QLabel('v1.0.0'); version.setObjectName('tinyMuted'); footer.addWidget(version)
        self.info_layout.addLayout(footer)

    def apply_theme(self):
        self.setStyleSheet((DARK_QSS if self.dark else LIGHT_QSS) + '\nQComboBox#languageSelector { min-width: 95px; padding: 8px 10px; }')
        if hasattr(self, 'toast'): self.toast._dark = self.dark
        self.theme_btn.setText(('' if self.width() < 900 else translate('Light mode' if self.dark else 'Dark mode', self.language))); self.theme_btn.setIcon(make_icon('sun' if self.dark else 'moon', '#c6d6e8' if self.dark else '#29435c', 17))
        self.nav_download.setProperty('active', self.current_page=='download'); self.nav_history.setProperty('active', self.current_page=='history'); self.nav_info.setProperty('active', self.current_page=='info')
        for b in (self.nav_download,self.nav_history,self.nav_info): b.style().unpolish(b); b.style().polish(b)
    def show_page(self, page):
        self.current_page=page
        target = {'download': self.download_page, 'history': self.history_page, 'info': self.info_page}.get(page, self.download_page)
        if self.pages.currentWidget() is not target:
            self.pages.setCurrentWidget(target)
            # Every page starts at its top; avoids reopening a page halfway down after scrolling.
            QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(0))
            effect = QGraphicsOpacityEffect(target); target.setGraphicsEffect(effect); effect.setOpacity(0.0)
            anim = QPropertyAnimation(effect, b'opacity', target); anim.setDuration(180); anim.setStartValue(0.0); anim.setEndValue(1.0); anim.setEasingCurve(QEasingCurve.OutCubic)
            target._page_fade = anim
            anim.finished.connect(lambda page=target, fx=effect: page.setGraphicsEffect(None) if page.graphicsEffect() is fx else None)
            anim.start()
        self.apply_theme()
    def toggle_theme(self):
        self.dark = not self.dark; self.settings.update(theme='dark' if self.dark else 'light', save_dir=self.location_input.text() if hasattr(self,'location_input') else self.save_dir, language=self.language); save_json(CONFIG_FILE,self.settings); self.apply_theme()
    def copy_text(self, text, message=None):
        try:
            value = str(text or '')
            QApplication.clipboard().setText(value)
            if QApplication.clipboard().text() != value: raise RuntimeError('Clipboard did not confirm the copied text.')
            self.show_toast(message or 'Link copied', 'success')
            return True
        except Exception as exc:
            self.show_toast(f'Copy failed: {exc}', 'error'); return False
    def show_toast(self, message, kind='success', duration=2500):
        if hasattr(self, 'toast'): self.toast.show_message(translate(message, self.language), kind, duration, self.dark)
    def paste_url(self):
        try: text=QApplication.clipboard().text().strip()
        except Exception as exc:
            self.show_toast(f'Paste failed: {exc}', 'error'); return
        if text:
            self.url_input.setText(text); self.url_input.setFocus(); self.url_input.setCursorPosition(len(text))
            self.show_toast('Link pasted', 'success')
        else:
            self.status_label.setText('Clipboard is empty.'); self.show_toast('Clipboard is empty.', 'warning')
    def change_language(self, index):
        if not hasattr(self, 'language_combo'): return
        code = self.language_combo.itemData(index) or 'en'
        if code == self.language: return
        self.language = code
        self.settings['language'] = code
        save_json(CONFIG_FILE, self.settings)
        self.refresh_queue_view()
        self.refresh_history()
        self.apply_language()
        self.show_toast('Language changed', 'info', 1800)

    def apply_language(self):
        # Retranslate existing widgets in-place, preserving user data and selection.
        if not hasattr(self, 'language_combo'): return
        widgets = [self] + self.findChildren(QWidget)
        for widget in widgets:
            if isinstance(widget, QComboBox) and widget is self.language_combo: continue
            if isinstance(widget, QLabel):
                current = widget.text(); original = widget.property('_source_text'); last = widget.property('_translated_text')
                if original is None or (current != last and current != translate(str(original), self.language)):
                    original = current; widget.setProperty('_source_text', original)
                result = translate(str(original), self.language); widget.setText(result); widget.setProperty('_translated_text', result)
            elif isinstance(widget, QPushButton):
                current = widget.text(); original = widget.property('_source_text'); last = widget.property('_translated_text')
                if original is None or (current != last and current != translate(str(original), self.language)):
                    original = current; widget.setProperty('_source_text', original)
                result = translate(str(original), self.language); widget.setText(result); widget.setProperty('_translated_text', result)
                tip = widget.property('_source_tooltip')
                if tip is None: tip = widget.toolTip(); widget.setProperty('_source_tooltip', tip)
                if tip: widget.setToolTip(translate(tip, self.language))
            elif isinstance(widget, QToolButton):
                tip = widget.property('_source_tooltip')
                if tip is None: tip = widget.toolTip(); widget.setProperty('_source_tooltip', tip)
                if tip: widget.setToolTip(translate(tip, self.language))
            elif isinstance(widget, QLineEdit):
                current = widget.placeholderText(); original = widget.property('_source_placeholder')
                if original is None or (current != widget.property('_translated_placeholder') and current != translate(str(original), self.language)):
                    original = current; widget.setProperty('_source_placeholder', original)
                result = translate(str(original), self.language); widget.setPlaceholderText(result); widget.setProperty('_translated_placeholder', result)
                tip = widget.property('_source_tooltip')
                if tip is None: tip = widget.toolTip(); widget.setProperty('_source_tooltip', tip)
                if tip: widget.setToolTip(translate(tip, self.language))
            elif isinstance(widget, QComboBox):
                if widget is getattr(self, 'source_filter', None): continue
                if widget is getattr(self, 'format_combo', None) or widget is getattr(self, 'quality_combo', None) or widget is getattr(self, 'sort_filter', None):
                    originals = [widget.itemData(i) or widget.itemText(i) for i in range(widget.count())]
                else:
                    originals = widget.property('_localizable_items')
                    if originals is None:
                        originals = [widget.itemText(i) for i in range(widget.count())]; widget.setProperty('_localizable_items', originals)
                selected = widget.currentData(); widget.blockSignals(True)
                for i, original in enumerate(originals): widget.setItemText(i, translate(str(original), self.language))
                if selected is not None:
                    idx = widget.findData(selected)
                    if idx >= 0: widget.setCurrentIndex(idx)
                widget.blockSignals(False)
        self.setWindowTitle(translate('Universal Downloader', self.language))
        self.language_combo.setToolTip(translate('Language & Region', self.language))
        self.language_combo.setAccessibleName(translate('Language', self.language))
        self.language_combo.setItemText(self.language_combo.findData('en'), 'English')
        self.language_combo.setItemText(self.language_combo.findData('hi'), 'हिन्दी')
        self.language_combo.setItemText(self.language_combo.findData('es'), 'Español')

    def browse(self):
        start=self.location_input.text().strip() or str(Path.home())
        folder=QFileDialog.getExistingDirectory(self,translate('Choose download folder', self.language),start)
        if folder: self.location_input.setText(folder); self.save_settings()
    def save_settings(self):
        self.settings.update(theme='dark' if self.dark else 'light',save_dir=self.location_input.text().strip(), language=self.language); save_json(CONFIG_FILE,self.settings)
    def open_download_folder(self):
        folder=Path(self.location_input.text().strip() or self.save_dir).expanduser(); folder.mkdir(parents=True,exist_ok=True); open_path(folder)
    def format_changed(self, text): self.quality_combo.setEnabled(not text.startswith(('MP3','M4A')))
    def valid_url(self):
        url=self.url_input.text().strip()
        if not url.startswith(('https://','http://')): QMessageBox.warning(self, translate('Enter a URL', self.language), translate('Paste a full video URL beginning with https://', self.language)); return None
        if yt_dlp is None: QMessageBox.critical(self, translate('yt-dlp is missing', self.language), translate('Run this command:', self.language)+'\npython -m pip install -U yt-dlp'); return None
        return url
    def attach_worker(self, worker):
        self.worker=worker; worker.progress.connect(self.on_progress); worker.status.connect(self.on_worker_status); worker.inspected.connect(self.on_inspected); worker.succeeded.connect(self.on_success); worker.failed.connect(self.on_failed); worker.finished.connect(self.on_worker_finished); worker.start()
    def inspect(self):
        url=self.valid_url()
        if not url or self.busy: return
        self.inspect_btn.setEnabled(False); self.status_label.setText(translate('Inspecting source and available formats…', self.language))
        self.attach_worker(WorkThread('inspect',url=url))
    def on_inspected(self, data):
        views=f"{data['views']:,} views" if data.get('views') else 'Views unavailable'
        self.meta_label.setText(f"{data['title']}\n{data['uploader']}   •   {duration_text(data.get('duration'))}   •   {views}")
        rows=[f"{h}p {ext.upper()} {'video + audio' if audio else 'video only'} · {fmt_bytes(size)}" for h,ext,audio,size in data['formats']]
        self.formats_label.setText('AVAILABLE VIDEO FORMATS\n'+'   |   '.join(rows) if rows else '')
        self.status_label.setText(translate('Inspection complete.', self.language))
    def start_download(self):
        url=self.valid_url()
        if not url: return
        if not self.location_input.text().strip(): QMessageBox.warning(self, translate('Choose a folder', self.language), translate('Please choose a save location first.', self.language)); return
        self.enqueue_urls([url])
        self.process_next_queue_item()
    def add_multiple_urls(self):
        text, ok = QInputDialog.getMultiLineText(self, translate('Add multiple URLs', self.language), translate('Paste one video URL per line:', self.language))
        if ok:
            urls = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]
            self.enqueue_urls(urls)
            self.process_next_queue_item()
    def enqueue_urls(self, urls):
        added = 0
        for url in urls:
            if not url.startswith(('https://','http://')): continue
            if any(item.get('url') == url and item.get('status') in ('Queued','Downloading') for item in self.download_queue): continue
            self.download_queue.append({'id': f'{time.time_ns()}-{added}', 'url': url, 'status': 'Queued'})
            added += 1
        save_json(QUEUE_FILE, self.download_queue); self.refresh_queue_view(animate=added > 0)
        if urls and not added: self.status_label.setText(translate('No new valid URLs were added (duplicates are skipped).', self.language))
    def refresh_queue_view(self, animate=False):
        if not hasattr(self, 'queue_list'): return
        self.queue_list.clear()
        for item in self.download_queue:
            status = item.get('status','Queued')
            status_text = translate(status, self.language)
            url = item.get('url','')
            label = f"{status_text}  •  {url}"
            widget = QListWidgetItem(label); widget.setToolTip(url); widget.setData(Qt.UserRole, item.get('id')); self.queue_list.addItem(widget)
        active = 1 if self.busy else 0
        self.queue_status.setText(f'{active} {translate("active", self.language)} · {sum(1 for x in self.download_queue if x.get("status")=="Queued")} {translate("queued", self.language)}')
        if animate:
            effect = QGraphicsOpacityEffect(self.queue_list); self.queue_list.setGraphicsEffect(effect); effect.setOpacity(0.0)
            animation = QPropertyAnimation(effect, b'opacity', self.queue_list); animation.setDuration(160); animation.setStartValue(0.0); animation.setEndValue(1.0); animation.setEasingCurve(QEasingCurve.OutCubic)
            self.queue_list._appearance_animation = animation
            animation.finished.connect(lambda fx=effect: self.queue_list.setGraphicsEffect(None) if self.queue_list.graphicsEffect() is fx else None)
            animation.start()
    def process_next_queue_item(self):
        if self.busy: return
        item = next((x for x in self.download_queue if x.get('status') == 'Queued'), None)
        if not item:
            save_json(QUEUE_FILE, self.download_queue); self.refresh_queue_view()
            self.download_btn.setEnabled(True); self.inspect_btn.setEnabled(True)
            return
        folder=self.location_input.text().strip() or self.save_dir
        self.save_settings(); self.busy=True; self.current_queue_item=item; item['status']='Downloading'
        save_json(QUEUE_FILE, self.download_queue); self.refresh_queue_view()
        self.download_btn.setEnabled(False); self.inspect_btn.setEnabled(False); self.progress.setValue(0); self.status_label.setText(translate('Starting queued download…', self.language))
        self.attach_worker(WorkThread('download',url=item['url'],folder=folder,quality=self.quality_combo.currentData() or self.quality_combo.currentText(),outformat=self.format_combo.currentData() or self.format_combo.currentText()))
    def retry_queue_item(self, list_item):
        index = self.queue_list.row(list_item)
        if 0 <= index < len(self.download_queue):
            item = self.download_queue[index]
            if item.get('status') in ('Failed','Cancelled','Completed'):
                item['status'] = 'Queued'; item.pop('error', None); item.pop('output_path', None)
                save_json(QUEUE_FILE, self.download_queue); self.refresh_queue_view(); self.process_next_queue_item()
    def clear_queue(self):
        if self.busy:
            QMessageBox.information(self, translate('Download in progress', self.language), translate('The active download cannot be cancelled safely yet. Only waiting items will be removed.', self.language))
        self.download_queue = [x for x in self.download_queue if x.get('status') == 'Downloading']
        save_json(QUEUE_FILE, self.download_queue); self.refresh_queue_view()
    def on_worker_status(self, text):
        self.status_label.setText(translate(text, self.language))
    def on_progress(self,pct,text):
        target = max(self.progress.value(), max(0, min(100, int(pct))))
        if target != self.progress.value(): self.progress.setValue(target)
        shown = text
        for source_text in ('Download transferred — preparing output…', 'Converting to H.264 MP4…'):
            if source_text in shown:
                shown = shown.replace(source_text, translate(source_text, self.language))
        if self.status_label.text() != shown: self.status_label.setText(shown)
    def on_success(self,record):
        self.busy=False; self.progress.setValue(100); self.status_label.setText(translate('Download complete.', self.language))
        self.history_store.add(record); self.history=self.history_store.list(order='Latest first'); self.refresh_history()
        if self.current_queue_item:
            self.current_queue_item['status']='Completed'; self.current_queue_item['output_path']=record.get('path','')
            self.current_queue_item=None; save_json(QUEUE_FILE,self.download_queue); self.refresh_queue_view()
        if not any(x.get('status') == 'Queued' for x in self.download_queue):
            QMessageBox.information(self, translate('Download complete', self.language), translate('Saved successfully:', self.language)+f"\n{record['path']}")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(250, self.process_next_queue_item)
    def on_failed(self,error):
        self.busy=False; self.status_label.setText(translate('Download failed — see error details.', self.language))
        if self.current_queue_item:
            self.current_queue_item['status']='Failed'; self.current_queue_item['error']=error[:1000]; self.current_queue_item=None
            save_json(QUEUE_FILE,self.download_queue); self.refresh_queue_view()
        QMessageBox.critical(self,translate('Download failed', self.language),error[:4000])
        from PySide6.QtCore import QTimer
        QTimer.singleShot(250, self.process_next_queue_item)
    def on_worker_finished(self):
        if not self.busy:
            self.inspect_btn.setEnabled(True); self.download_btn.setEnabled(True)
    def refresh_history(self, *_):
        self.history = self.history_store.list(order='Latest first')
        if hasattr(self, 'source_filter'):
            current = self.source_filter.currentData() if self.source_filter.count() else 'All Websites'
            sources = self.history_store.sources()
            self.source_filter.blockSignals(True); self.source_filter.clear()
            self.source_filter.addItem(translate('All Websites', self.language), 'All Websites')
            from history_store import source_display_name
            for canonical in sources: self.source_filter.addItem(source_display_name(canonical), canonical)
            idx = self.source_filter.findData(current if current in sources or current == 'All Websites' else 'All Websites')
            self.source_filter.setCurrentIndex(max(0, idx)); self.source_filter.blockSignals(False)
        for layout in (getattr(self,'inline_history',None),getattr(self,'full_history',None)):
            if layout is None: continue
            while layout.count():
                item=layout.takeAt(0); w=item.widget()
                if w: w.deleteLater()
            if layout is self.inline_history:
                records = self.history[:3]
            else:
                query = self.library_search.text() if hasattr(self,'library_search') else ''
                source = self.source_filter.currentData() if hasattr(self,'source_filter') else 'All Websites'
                order = self.sort_filter.currentData() if hasattr(self,'sort_filter') else 'Latest first'
                records = self.history_store.list(query, source, order)
            if not records:
                empty=QFrame(); empty.setObjectName('historyCard'); box=QVBoxLayout(empty); box.setContentsMargins(18,22,18,22)
                label=QLabel('No downloads match these filters.' if layout is self.full_history and self.history else 'Your completed downloads will appear here.')
                label.setObjectName('muted'); label.setWordWrap(True); box.addWidget(label); layout.addWidget(empty)
            else:
                for record in records:
                    row = DownloadRow(record, self)
                    row.remove_requested.connect(self.remove_history_record)
                    layout.addWidget(row)
        if hasattr(self,'history_count'): self.history_count.setText(f'✓  {len(self.history)} {translate("downloads completed", self.language)}')
        if hasattr(self,'library_count'):
            shown = len(self.history_store.list(self.library_search.text(), self.source_filter.currentData(), self.sort_filter.currentData()))
            self.library_count.setText(f'{shown} {translate("of", self.language)} {len(self.history)} {translate("downloads", self.language)}')
        if hasattr(self, 'language_combo'): self.apply_language()
    def remove_history_record(self, record_id):
        if not record_id: return
        self.history_store.remove(record_id)
        self.refresh_history()
    def clear_library_filters(self):
        self.library_search.clear(); self.source_filter.setCurrentIndex(max(0,self.source_filter.findData('All Websites'))); self.sort_filter.setCurrentIndex(max(0,self.sort_filter.findData('Latest first')))
    def clear_history(self):
        if QMessageBox.question(self,translate('Clear history', self.language),translate('Remove all items from the app history? Downloaded files will not be deleted.', self.language),QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.history_store.clear(); self.history=[]; save_json(HISTORY_FILE,[]); self.refresh_history()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'toast'): QTimer.singleShot(0, self.toast.reposition)
        # A resized viewport can retain an obsolete scroll offset, leaving the header
        # clipped and making the page appear to contain a large empty gap. Re-anchor
        # the page at the top after Qt completes its pending geometry calculations.
        if hasattr(self, 'scroll') and not getattr(self, '_resize_scroll_pending', False):
            self._resize_scroll_pending = True
            def _restore_scroll_top():
                self._resize_scroll_pending = False
                if hasattr(self, 'scroll'):
                    self.scroll.verticalScrollBar().setValue(0)
            QTimer.singleShot(0, _restore_scroll_top)
        width = self.width()
        content_width = self.scroll.viewport().width() if hasattr(self, 'scroll') else width
        # Give content more room as the window narrows; collapse the sidebar to icon-only mode on small windows.
        if width < 900:
            self.sidebar.setFixedWidth(68)
            self.side_layout.setContentsMargins(7, 14, 7, 14)
            self.brand_name.hide()
            self.sidebar_logo.setFixedSize(34, 34)
            self.header_title.setStyleSheet('font-size:21px; font-weight:750;')
            for button, label, icon_name in self.nav_buttons:
                button.setText('')
                button.setToolTip(translate(label, self.language))
                button.setStyleSheet('text-align:center; padding:13px 0;')
            self.body_layout.setContentsMargins(14, 16, 14, 16)
            self.theme_btn.setText('')
            self.theme_btn.setToolTip(translate('Toggle light/dark theme', self.language))
        elif width < 1120:
            self.sidebar.setFixedWidth(176)
            self.side_layout.setContentsMargins(12, 18, 12, 16)
            self.brand_name.show()
            self.sidebar_logo.setFixedSize(38, 38)
            self.header_title.setStyleSheet('font-size:25px; font-weight:750;')
            for button, label, icon_name in self.nav_buttons:
                button.setText(translate(label, self.language))
                button.setToolTip(translate(label, self.language))
                button.setStyleSheet('')
            self.body_layout.setContentsMargins(20, 20, 20, 18)
            self.theme_btn.setText('' if width < 900 else translate('Light mode' if self.dark else 'Dark mode', self.language))
            self.theme_btn.setToolTip(translate('Toggle light/dark theme', self.language))
        else:
            self.sidebar.setFixedWidth(198)
            self.side_layout.setContentsMargins(16, 20, 16, 18)
            self.brand_name.show()
            self.sidebar_logo.setFixedSize(42, 42)
            self.header_title.setStyleSheet('font-size:29px; font-weight:750;')
            for button, label, icon_name in self.nav_buttons:
                button.setText(translate(label, self.language))
                button.setToolTip('')
                button.setStyleSheet('')
            self.body_layout.setContentsMargins(28, 24, 28, 22)
            self.theme_btn.setText('' if width < 900 else translate('Light mode' if self.dark else 'Dark mode', self.language))
            self.theme_btn.setToolTip(translate('Toggle light/dark theme', self.language))
        # The about page switches to a single column on compact windows.
        if hasattr(self, 'info_columns'):
            compact = content_width < 900
            if compact != getattr(self, '_info_stacked', False):
                self._set_info_columns_stacked(compact)
        # Let download option cards breathe on compact screens.
        if hasattr(self, 'queue_list'):
            # Keep the queue compact on short windows so completed downloads remain reachable.
            self.queue_list.setMaximumHeight(max(76, min(170, int(self.height() * 0.20))))
        if hasattr(self, 'fields_layout'):
            field_columns = 1 if content_width < 600 else 2 if content_width < 920 else 3
            if field_columns != getattr(self, '_field_columns', 3):
                self._set_fields_columns(field_columns)
        if hasattr(self, 'url_grid'):
            compact_url = content_width < 690
            if compact_url != getattr(self, '_url_compact', False):
                self._set_url_layout(compact_url)

    def _set_info_columns_stacked(self, stacked):
        columns = self.info_columns
        if stacked:
            # Preserve the original insertion point, then place the two column layouts
            # vertically so cards never get squeezed into unreadable narrow columns.
            self._info_columns_index = self.info_layout.indexOf(columns)
            self.info_layout.takeAt(self._info_columns_index)
            while columns.count():
                columns.takeAt(0)
            idx = self._info_columns_index
            self.info_layout.insertLayout(idx, self.info_left_col)
            self.info_layout.insertLayout(idx + 1, self.info_right_col)
            self._info_stacked = True
        else:
            # Remove the standalone column layouts and restore the original side-by-side row.
            for layout in (self.info_left_col, self.info_right_col):
                for i in range(self.info_layout.count()):
                    item = self.info_layout.itemAt(i)
                    if item and item.layout() is layout:
                        self.info_layout.takeAt(i)
                        break
            columns.addLayout(self.info_left_col, 13)
            columns.addLayout(self.info_right_col, 10)
            self.info_layout.insertLayout(min(getattr(self, '_info_columns_index', 3), self.info_layout.count()), columns)
            self._info_stacked = False

    def _set_url_layout(self, compact):
        layout = self.url_grid
        while layout.count():
            layout.takeAt(0)
        url_input, paste_btn, inspect_btn = self.url_controls
        if compact:
            layout.addWidget(url_input, 0, 0, 1, 3)
            layout.addWidget(paste_btn, 1, 0)
            layout.addWidget(inspect_btn, 1, 1, 1, 2)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 1)
            layout.setColumnStretch(2, 1)
        else:
            layout.addWidget(url_input, 0, 0)
            layout.addWidget(paste_btn, 0, 1)
            layout.addWidget(inspect_btn, 0, 2)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 0)
            layout.setColumnStretch(2, 0)
        self._url_compact = compact

    def _set_fields_columns(self, columns):
        """Reflow format, quality and destination cards to 3/2/1 columns."""
        layout = self.fields_layout
        while layout.count():
            item = layout.takeAt(0)
            # The cards are retained and reinserted; do not delete their widgets.
        layout.setHorizontalSpacing(12 if columns >= 2 else 0)
        layout.setVerticalSpacing(10)
        # Clear old stretch values when moving from 3 columns to 2 or 1.
        for col in range(3):
            layout.setColumnStretch(col, 0)
        for row in range(3):
            layout.setRowStretch(row, 0)
        for index, card in enumerate(self.field_cards):
            row, col = divmod(index, columns)
            layout.addWidget(card, row, col)
            layout.setColumnStretch(col, 1)
        self._field_columns = columns



def main():
    """Launch the Universal Downloader desktop application."""
    print("[Universal Downloader] Starting application...", flush=True)
    app = QApplication(sys.argv)
    app.setApplicationName("Universal Downloader")
    app.setOrganizationName("Arth Awasthi")
    # Set the application-level icon as well as the main-window icon so Windows
    # can use the supplied branding for the taskbar and window switcher.
    app_icon_path = Path(__file__).with_name('universal_downloader_logo.ico')
    app_png_path = Path(__file__).with_name('universal_downloader_logo.png')
    if app_icon_path.exists():
        app.setWindowIcon(QIcon(str(app_icon_path)))
    elif app_png_path.exists():
        app.setWindowIcon(QIcon(str(app_png_path)))
    app.setQuitOnLastWindowClosed(True)
    window = DownloaderWindow()
    window.show()
    window.raise_()
    window.activateWindow()
    print("[Universal Downloader] Window created. Entering Qt event loop.", flush=True)
    result = app.exec()
    print(f"[Universal Downloader] Qt event loop exited with code {result}.", flush=True)
    return result


if __name__ == "__main__":
    print("[Universal Downloader] Python entry point reached.", flush=True)
    try:
        sys.exit(main())
    except Exception as exc:
        # Keep startup failures visible when launched from a terminal or .bat file.
        import traceback
        traceback.print_exc()
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Universal Downloader could not start",
                                 f"{exc}\n\nRun the app from Run_Universal_Downloader.bat to see setup errors.")
        except Exception:
            pass
        sys.exit(1)
