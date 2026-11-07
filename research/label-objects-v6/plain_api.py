"""Plain stateless vision requests. No tools, agents, history or transcript access.
Caller supplies exactly the allowlisted manual text and image. Credentials remain
in environment and are never written to a request receipt.
"""
from pathlib import Path
import json,hashlib,base64,os,time,urllib.request,urllib.error,subprocess,socket

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def http(url,body=None,key=None,timeout=180):
    headers={'Content-Type':'application/json'}
    if key:headers['Authorization']='Bearer '+key
    req=urllib.request.Request(url,data=None if body is None else json.dumps(body).encode(),headers=headers)
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)

def vision(provider,model,manual,image_path,out,base=None,max_tokens=2048):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if (out/'response.json').exists() or (out/'failure.json').exists():raise RuntimeError('Immutable call receipt; do not overwrite/retry silently')
    encoded=base64.b64encode(Path(image_path).read_bytes()).decode()
    mime='image/jpeg' if Path(image_path).suffix.lower() in ['.jpg','.jpeg'] else 'image/png'
    if provider=='zai':
        url='https://api.z.ai/api/paas/v4/chat/completions'
        body=dict(model=model,messages=[dict(role='user',content=[dict(type='text',text=manual),
            dict(type='image_url',image_url=dict(url='data:'+mime+';base64,'+encoded))])],
            stream=False,temperature=0,max_tokens=max_tokens,thinking=dict(type='disabled'))
        key=os.environ['Z_AI_API_KEY']
    elif provider=='ollama':
        if not base or ':11434' in base:raise ValueError('Local generation must use isolated CPU server')
        url=base+'/api/chat';key=None
        body=dict(model=model,messages=[dict(role='user',content=manual,images=[encoded])],stream=False,
            keep_alive=0,format='json',options=dict(num_gpu=0,num_ctx=2048,num_predict=max_tokens,temperature=0))
    else:raise ValueError('Unsupported provider')
    assert len(body['messages'])==1 and 'tools' not in body
    wire=json.dumps(body).encode();write(out/'request-receipt.json',dict(provider=provider,model=model,
        url=url,manual=manual,image_path=str(Path(image_path).resolve()),image_sha256=sha(image_path),
        request_sha256=hashlib.sha256(wire).hexdigest(),message_count=1,tools_supplied=False,agent_harness=False,
        stateless=True,transcription_supplied=False,max_tokens=max_tokens,runtime_options=body.get('options'),client_sha256=sha(__file__),started_epoch=time.time()))
    start=time.perf_counter()
    try:
        result=http(url,body,key)
        write(out/'response.json',result)
        if result.get('web_search'):raise ValueError('Unexpected search result in plain call')
        message=result['choices'][0]['message'] if provider=='zai' else result['message']
        if message.get('tool_calls'):raise ValueError('Unexpected tool request')
        content=message.get('content','')
        if not content:raise ValueError('Empty model response')
        write(out/'completion.json',dict(content=content,elapsed_seconds=time.perf_counter()-start,
            response_sha256=sha(out/'response.json'),model_returned=result.get('model')))
        return content
    except Exception as error:
        # Save bounded status only, never headers or credentials.
        info=dict(error_type=type(error).__name__,elapsed_seconds=time.perf_counter()-start)
        if isinstance(error,urllib.error.HTTPError):
            info['http_status']=error.code;info['provider_message']=error.read(1500).decode(errors='replace')
        write(out/'failure.json',info)
        raise RuntimeError(json.dumps(info)) from None

class IsolatedOllama:
    def __enter__(self):
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));self.port=sock.getsockname()[1]
        self.base=f'http://127.0.0.1:{self.port}';env=os.environ.copy()
        env.update(OLLAMA_HOST=f'127.0.0.1:{self.port}',OLLAMA_MODELS=str(Path.home()/'.ollama/models'),
            OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1')
        logs=HERE/'api-runtime';logs.mkdir(exist_ok=True)
        self.log=(logs/f'ollama-{self.port}.log').open('w',encoding='utf-8')
        self.proc=subprocess.Popen([str(Path.home()/'AppData/Local/Programs/Ollama/ollama.exe'),'serve'],env=env,
            stdout=self.log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        for attempt in range(100):
            if self.proc.poll() is not None:raise RuntimeError('Isolated Ollama server exited')
            try:http(self.base+'/api/tags',timeout=1);return self
            except (OSError,urllib.error.URLError):time.sleep(.1)
        self.__exit__(None,None,None);raise RuntimeError('Isolated server startup deadline')
    def __exit__(self,*args):
        self.proc.terminate()
        try:self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
        self.log.close()

def json_object(text):
    text=text.strip()
    if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0]
    return json.loads(text)
