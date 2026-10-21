"""Optional local-only preview. Does not deploy or publish anything."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'dist'
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
print('Local preview: http://127.0.0.1:18765', flush=True)
ThreadingHTTPServer(('127.0.0.1', 18765), handler).serve_forever()
