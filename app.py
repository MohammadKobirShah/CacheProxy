#!/usr/bin/env python3
"""
🌐 Universal Caching Proxy Server - Cloud Deploy Version
Deploy on Render/Railway/Heroku
"""

import os
import json
import hashlib
import time
import gzip
import threading
from datetime import datetime
from flask import Flask, request, Response, render_template_string
import urllib.request
import urllib.parse

# Try to import brotli
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

app = Flask(__name__)

# Cache storage
cache = {}
cache_lock = threading.Lock()

# Stats
stats = {
    'requests': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'bytes_saved': 0,
    'start_time': time.time()
}

# Configuration
MAX_CACHE_SIZE = int(os.environ.get('MAX_CACHE_SIZE_MB', 500)) * 1024 * 1024
DEFAULT_TTL = int(os.environ.get('CACHE_TTL', 3600))
CACHEABLE_CONTENT_TYPES = [
    'text/html', 'text/css', 'text/javascript', 'application/javascript',
    'application/json', 'image/', 'font/', 'application/font'
]

class CacheEntry:
    """Represents a cached response."""
    def __init__(self, url, content, content_type, headers, status_code):
        self.url = url
        self.content = content
        self.content_type = content_type
        self.headers = headers
        self.status_code = status_code
        self.timestamp = time.time()
        self.hit_count = 0
        self.size = len(content)

def get_cache_key(url):
    """Generate cache key from URL."""
    parsed = urllib.parse.urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return hashlib.md5(normalized.encode()).hexdigest()

def get_from_cache(cache_key):
    """Get item from cache if valid."""
    with cache_lock:
        if cache_key in cache:
            entry = cache[cache_key]
            if time.time() - entry.timestamp < DEFAULT_TTL:
                entry.hit_count += 1
                return entry
            else:
                del cache[cache_key]
    return None

def add_to_cache(cache_key, entry):
    """Add item to cache with size management."""
    with cache_lock:
        current_size = sum(e.size for e in cache.values())
        if current_size + entry.size > MAX_CACHE_SIZE:
            evict_cache()
        cache[cache_key] = entry

def evict_cache():
    """Evict old cache entries using LRU."""
    if not cache:
        return
    sorted_entries = sorted(cache.items(), key=lambda x: x[1].timestamp)
    remove_count = max(1, len(sorted_entries) // 5)
    for key, _ in sorted_entries[:remove_count]:
        del cache[key]

def is_cacheable(content_type, url):
    """Check if response should be cached."""
    skip_patterns = ['login', 'signin', 'auth', 'session', 'cart', 'checkout', 'admin', 'api/v1/', 'graphql']
    url_lower = url.lower()
    for pattern in skip_patterns:
        if pattern in url_lower:
            return False
    if not content_type:
        return False
    for cacheable_type in CACHEABLE_CONTENT_TYPES:
        if content_type.startswith(cacheable_type):
            return True
    return False

@app.route('/health')
def health():
    """Health check endpoint for Render/Railway."""
    return {'status': 'healthy', 'uptime': time.time() - stats['start_time']}

@app.route('/stats')
def stats_page():
    """Statistics page."""
    uptime = time.time() - stats['start_time']
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    cache_size = sum(e.size for e in cache.values())
    cache_count = len(cache)
    hit_rate = (stats['cache_hits'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌐 Caching Proxy Stats</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 0 auto; padding: 20px; background: #0f172a; color: #e2e8f0; }
            .card { background: #1e293b; border-radius: 16px; padding: 24px; margin: 20px 0; 
                    border: 1px solid #334155; }
            h1 { color: #38bdf8; text-align: center; font-size: 2em; }
            h2 { color: #94a3b8; font-size: 1.2em; margin-top: 0; }
            .stat { display: flex; justify-content: space-between; padding: 12px 0; 
                    border-bottom: 1px solid #334155; }
            .stat:last-child { border-bottom: none; }
            .label { color: #94a3b8; }
            .value { font-weight: 600; }
            .success { color: #4ade80; }
            .warning { color: #fbbf24; }
            .info { color: #60a5fa; }
            .buttons { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
            button { padding: 12px 24px; border: none; border-radius: 10px; cursor: pointer; 
                     font-weight: 600; font-size: 14px; transition: all 0.2s; }
            .btn-primary { background: #3b82f6; color: white; }
            .btn-danger { background: #ef4444; color: white; }
            button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
            code { background: #334155; padding: 2px 8px; border-radius: 6px; font-size: 14px; }
            .setup-box { background: #0f172a; padding: 16px; border-radius: 10px; margin-top: 12px; }
            .emoji { font-size: 1.5em; }
        </style>
    </head>
    <body>
        <h1>🌐 Universal Caching Proxy</h1>
        
        <div class="card">
            <h2>📊 Live Statistics</h2>
            <div class="stat">
                <span class="label">⏱️ Uptime</span>
                <span class="value">""" + f"{hours}h {minutes}m" + """</span>
            </div>
            <div class="stat">
                <span class="label">📥 Total Requests</span>
                <span class="value info">""" + f"{stats['requests']:,}" + """</span>
            </div>
            <div class="stat">
                <span class="label">✅ Cache Hits</span>
                <span class="value success">""" + f"{stats['cache_hits']:,}" + """</span>
            </div>
            <div class="stat">
                <span class="label">❌ Cache Misses</span>
                <span class="value warning">""" + f"{stats['cache_misses']:,}" + """</span>
            </div>
            <div class="stat">
                <span class="label">📈 Hit Rate</span>
                <span class="value """ + ('success' if hit_rate > 50 else 'warning') + """">""" + f"{hit_rate:.1f}%" + """</span>
            </div>
            <div class="stat">
                <span class="label">💾 Data Saved</span>
                <span class="value success">""" + f"{stats['bytes_saved'] / (1024*1024):.2f} MB" + """</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🗂️ Cache Status</h2>
            <div class="stat">
                <span class="label">📦 Cached Items</span>
                <span class="value info">""" + f"{cache_count:,}" + """</span>
            </div>
            <div class="stat">
                <span class="label">💽 Cache Size</span>
                <span class="value">""" + f"{cache_size / (1024*1024):.2f} MB / {MAX_CACHE_SIZE / (1024*1024):.0f} MB" + """</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 Management</h2>
            <div class="buttons">
                <button class="btn-danger" onclick="fetch('/cache/clear').then(() => location.reload())">
                    🗑️ Clear Cache
                </button>
                <button class="btn-primary" onclick="location.reload()">
                    🔄 Refresh
                </button>
            </div>
        </div>
        
        <div class="card">
            <h2>📖 Browser Setup</h2>
            <div class="setup-box">
                <p><strong>Option 1: Browser Extension</strong></p>
                <p>Use <strong>Proxy SwitchyOmega</strong> (Chrome/Firefox) to easily switch proxy.</p>
                <br>
                <p><strong>Option 2: System Proxy</strong></p>
                <p>Set HTTP Proxy to your server address.</p>
                <br>
                <p><strong>Option 3: Command Line</strong></p>
                <code>export http_proxy=http://your-server-url</code>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/cache/clear')
def clear_cache():
    """Clear all cache."""
    with cache_lock:
        cache.clear()
    return {'status': 'cleared', 'message': 'Cache cleared successfully!'}

@app.route('/cache/list')
def list_cache():
    """List cached items."""
    entries = []
    with cache_lock:
        for key, entry in cache.items():
            entries.append({
                'url': entry.url,
                'size': entry.size,
                'hits': entry.hit_count,
                'age': int(time.time() - entry.timestamp),
                'content_type': entry.content_type
            })
    return {'cached_items': entries, 'count': len(entries)}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """Main proxy endpoint."""
    stats['requests'] += 1
    
    # Build target URL
    if path.startswith('http://') or path.startswith('https://'):
        target_url = path
    else:
        # Check if it's a direct request with full URL in query
        target_url = request.args.get('url')
        if not target_url:
            target_url = f"https://{path}" if path else "https://google.com"
    
    # Check cache
    cache_key = get_cache_key(target_url)
    cached = get_from_cache(cache_key)
    
    if cached:
        stats['cache_hits'] += 1
        stats['bytes_saved'] += cached.size
        
        response = Response(
            cached.content,
            status=cached.status_code,
            content_type=cached.content_type
        )
        response.headers['X-Cache'] = 'HIT'
        response.headers['X-Cache-Hits'] = str(cached.hit_count)
        return response
    
    # Fetch from origin
    stats['cache_misses'] += 1
    
    try:
        req = urllib.request.Request(target_url)
        req.add_header('Accept-Encoding', 'gzip, br' if HAS_BROTLI else 'gzip')
        req.add_header('User-Agent', 'CachingProxy/1.0')
        req.add_header('Accept', '*/*')
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', '')
            encoding = resp.headers.get('Content-Encoding')
            
            # Decompress
            if encoding == 'gzip':
                content = gzip.decompress(content)
            elif encoding == 'br' and HAS_BROTLI:
                content = brotli.decompress(content)
            
            # Cache if cacheable
            if is_cacheable(content_type, target_url):
                entry = CacheEntry(
                    url=target_url,
                    content=content,
                    content_type=content_type,
                    headers=dict(resp.headers),
                    status_code=resp.status
                )
                add_to_cache(cache_key, entry)
            
            response = Response(
                content,
                status=resp.status,
                content_type=content_type
            )
            response.headers['X-Cache'] = 'MISS'
            return response
            
    except Exception as e:
        return {'error': str(e)}, 502

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Starting Caching Proxy on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
