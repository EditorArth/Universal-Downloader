"""SQLite-backed download history with canonical website identifiers."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime

# Known yt-dlp extractor names are mapped to their stable public website identity.
EXTRACTOR_DOMAINS = {
    'youtube': 'youtube.com', 'youtubeclip': 'youtube.com', 'youtubeplaylist': 'youtube.com',
    'instagram': 'instagram.com', 'twitter': 'x.com', 'x': 'x.com', 'facebook': 'facebook.com',
    'fbwatch': 'facebook.com', 'tiktok': 'tiktok.com', 'reddit': 'reddit.com',
    'vimeo': 'vimeo.com', 'twitch': 'twitch.tv', 'dailymotion': 'dailymotion.com',
    'soundcloud': 'soundcloud.com', 'bilibili': 'bilibili.com', 'pinterest': 'pinterest.com',
    'linkedin': 'linkedin.com', 'rumble': 'rumble.com', 'odysee': 'odysee.com',
}
DISPLAY_NAMES = {
    'youtube.com': 'YouTube', 'youtu.be': 'YouTube', 'instagram.com': 'Instagram',
    'x.com': 'X', 'twitter.com': 'X', 't.co': 'X', 'facebook.com': 'Facebook',
    'fb.watch': 'Facebook', 'tiktok.com': 'TikTok', 'reddit.com': 'Reddit',
    'redd.it': 'Reddit', 'vimeo.com': 'Vimeo', 'twitch.tv': 'Twitch',
    'dailymotion.com': 'Dailymotion', 'soundcloud.com': 'SoundCloud', 'bilibili.com': 'Bilibili',
    'pinterest.com': 'Pinterest', 'linkedin.com': 'LinkedIn', 'rumble.com': 'Rumble',
    'odysee.com': 'Odysee', 'unknown': 'Unknown',
}

def _host_from(value: str) -> str:
    value = (value or '').strip()
    if not value: return ''
    # Accept both full URLs and host-only legacy source strings.
    parsed = urlsplit(value if '://' in value or value.startswith('//') else '//' + value)
    host = (parsed.hostname or '').encode('idna').decode('ascii').lower().rstrip('.')
    if host.startswith('www.'):
        host = host[4:]
    return host

def normalize_source(url: str = '', extractor: str | None = None) -> str:
    """Return canonical host identity; never use a display label as the identity."""
    key = (extractor or '').strip().lower()
    if key:
        key = key.removesuffix('ie')
        for extractor_name, domain in EXTRACTOR_DOMAINS.items():
            if key == extractor_name or key.startswith(extractor_name):
                return domain
    aliases = {'instagram': 'instagram.com', 'youtube': 'youtube.com', 'youtube.com': 'youtube.com',
               'twitter': 'x.com', 'x': 'x.com', 'facebook': 'facebook.com', 'tiktok': 'tiktok.com',
               'reddit': 'reddit.com', 'vimeo': 'vimeo.com', 'twitch': 'twitch.tv',
               'dailymotion': 'dailymotion.com', 'soundcloud': 'soundcloud.com', 'bilibili': 'bilibili.com',
               'unknown': 'unknown', 'website': 'unknown'}
    try:
        host = _host_from(url)
        if host in aliases: return aliases[host]
        if host in {'youtube.com', 'm.youtube.com', 'music.youtube.com'}: return 'youtube.com'
        if host == 'youtu.be': return 'youtube.com'
        if host in {'instagram.com', 'threads.net'}: return host
        if host in {'twitter.com', 't.co'}: return 'x.com'
        if host == 'x.com': return 'x.com'
        if host in {'facebook.com', 'm.facebook.com', 'fb.watch', 'fb.com'}: return 'facebook.com'
        if host.endswith('.youtube.com'): return 'youtube.com'
        if host.endswith('.instagram.com'): return 'instagram.com'
        if host.endswith('.tiktok.com'): return 'tiktok.com'
        if host.endswith('.reddit.com') or host == 'redd.it': return 'reddit.com'
        return host or 'unknown'
    except (ValueError, UnicodeError):
        return 'unknown'

def source_display_name(source: str) -> str:
    canonical = normalize_source(source)
    if canonical in DISPLAY_NAMES: return DISPLAY_NAMES[canonical]
    if canonical == 'unknown': return 'Unknown'
    first = canonical.split('.')[0]
    return first[:1].upper() + first[1:]

class HistoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL DEFAULT '', filename TEXT NOT NULL DEFAULT '',
                path TEXT NOT NULL DEFAULT '', source TEXT NOT NULL DEFAULT 'unknown', url TEXT NOT NULL DEFAULT '',
                downloaded_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Completed', format TEXT NOT NULL DEFAULT '',
                resolution TEXT NOT NULL DEFAULT '', thumbnail_path TEXT NOT NULL DEFAULT '', metadata_json TEXT NOT NULL DEFAULT '{}')''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_downloaded_at ON downloads(downloaded_at)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_source ON downloads(source)')
        self.migrate_sources()

    def _connect(self):
        db = sqlite3.connect(str(self.path), timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA busy_timeout=10000')
        return db

    def migrate_sources(self):
        """Idempotently canonicalize legacy source values without removing records."""
        with self._connect() as db:
            rows = db.execute('SELECT id,source,url,metadata_json FROM downloads').fetchall()
            for row in rows:
                canonical = normalize_source(row['url'], row['source'])
                # When source was already a canonical domain, URL-derived normalization is preferred
                # to avoid treating a legacy label such as "Instagram" as a hostname.
                url_source = normalize_source(row['url']) if row['url'] else 'unknown'
                source_value = row['source'] or ''
                if row['url'] and url_source != 'unknown': canonical = url_source
                elif source_value: canonical = normalize_source(source_value)
                try: metadata = json.loads(row['metadata_json'] or '{}')
                except (ValueError, TypeError): metadata = {}
                if canonical != row['source']:
                    db.execute('UPDATE downloads SET source=? WHERE id=?', (canonical, row['id']))
                # Keep metadata intact, but align its source field to the canonical identifier.
                if isinstance(metadata, dict) and metadata.get('source') != canonical:
                    metadata['source'] = canonical
                    db.execute('UPDATE downloads SET metadata_json=? WHERE id=?', (json.dumps(metadata, ensure_ascii=False), row['id']))

    def add(self, record: dict) -> int:
        path = str(record.get('path') or '')
        title = str(record.get('title') or Path(path).name or 'Untitled')
        date = str(record.get('downloaded_at') or record.get('date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        try:
            parsed = datetime.fromisoformat(date.replace('Z', '+00:00'))
            date = parsed.astimezone().replace(tzinfo=None).isoformat(timespec='seconds') if parsed.tzinfo else parsed.isoformat(timespec='seconds')
        except Exception: pass
        source = normalize_source(record.get('url', ''), record.get('extractor_key') or record.get('extractor') or record.get('source'))
        data = dict(record); data['source'] = source
        with self._connect() as db:
            cur = db.execute('''INSERT INTO downloads(title,filename,path,source,url,downloaded_at,status,format,resolution,thumbnail_path,metadata_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)''', (title, Path(path).name, path, source, str(record.get('url') or ''), date,
                str(record.get('status') or 'Completed'), str(record.get('format') or ''), str(record.get('resolution') or ''),
                str(record.get('thumbnail_path') or ''), json.dumps(data, ensure_ascii=False)))
            return int(cur.lastrowid)

    def import_records(self, records: list[dict]):
        if self.count(): return
        for item in reversed(records):
            try: self.add(item)
            except Exception: pass

    def count(self) -> int:
        with self._connect() as db: return int(db.execute('SELECT COUNT(*) FROM downloads').fetchone()[0])

    def sources(self) -> list[str]:
        with self._connect() as db:
            values = [normalize_source(r[0]) for r in db.execute('SELECT DISTINCT source FROM downloads')]
        return sorted(set(values), key=lambda value: source_display_name(value).casefold())

    def list(self, search: str = '', source: str = 'All Websites', order: str = 'Latest first') -> list[dict]:
        clauses, args = [], []
        if search.strip():
            needle = '%' + search.strip().replace('%', r'\%').replace('_', r'\_') + '%'
            clauses.append("(title LIKE ? ESCAPE '\\' OR filename LIKE ? ESCAPE '\\')")
            args.extend((needle, needle))
        if source and source not in ('All Websites', 'all'):
            clauses.append('source = ?'); args.append(normalize_source(source))
        where = (' WHERE ' + ' AND '.join(clauses)) if clauses else ''
        direction = 'ASC' if order in ('Oldest first', 'oldest') else 'DESC'
        with self._connect() as db:
            rows = db.execute(f'SELECT * FROM downloads{where} ORDER BY downloaded_at {direction}, id {direction}', args).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            try: original = json.loads(d.get('metadata_json') or '{}')
            except (ValueError, TypeError): original = {}
            original.update({k: d[k] for k in ('id','title','filename','path','source','url','downloaded_at','status','format','resolution','thumbnail_path')})
            original['source_label'] = source_display_name(d['source'])
            original['date'] = original.get('downloaded_at') or original.get('date','')
            result.append(original)
        return result

    def remove(self, record_id: int):
        with self._connect() as db: db.execute('DELETE FROM downloads WHERE id=?', (int(record_id),))

    def clear(self):
        with self._connect() as db: db.execute('DELETE FROM downloads')
