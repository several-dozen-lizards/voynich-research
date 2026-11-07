from plain_api import *
before=http('http://127.0.0.1:11434/api/ps',timeout=5)
try:
    with IsolatedOllama() as server:
        print(vision('ollama','moondream:latest','Return a JSON object with key visible_shape describing the single outline.',HERE/'api-smoke.png',HERE/'api-smoke-moondream',base=server.base,max_tokens=96),flush=True)
finally:
    after=http('http://127.0.0.1:11434/api/ps',timeout=5)
    write(HERE/'api-runtime/moondream-server-snapshots.json',dict(before=before,after=after,main_calls='GET /api/ps only',isolated_CPU_server_closed=True))
