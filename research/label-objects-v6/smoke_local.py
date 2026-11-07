from plain_api import *
from PIL import Image,ImageDraw

p=HERE/'api-smoke.png'
before=http('http://127.0.0.1:11434/api/ps',timeout=5)
with IsolatedOllama() as server:
    write(HERE/'api-runtime/isolation.json',dict(isolated_port=server.port,server_pid=server.proc.pid,main_server_read_only=True,CPU_only=True,
        installed_vision_models=['llava:7b','moondream:latest']))
    text=vision('ollama','llava:7b','Return a JSON object with key visible_shape describing the single outline in the image.',p,HERE/'api-smoke-llava',base=server.base,max_tokens=128)
    print('llava',text,flush=True)
after=http('http://127.0.0.1:11434/api/ps',timeout=5)
write(HERE/'api-runtime/main-server-snapshots.json',dict(before=before,after=after,own_calls='GET /api/ps only; no main-server generation, load, unload, or configuration mutation'))
print('Isolated server closed')
