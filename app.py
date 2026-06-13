import os
import urllib.request
import urllib.error
import json
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 3456))
KLING = "https://api-singapore.klingai.com"

ctx = ssl.create_default_context()

HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kling AI Video Generator</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0e0e11;--bg2:#18181c;--bg3:#222228;--border:rgba(255,255,255,0.08);--border-h:rgba(255,255,255,0.15);--text:#e8e8ec;--text2:#9898a4;--text3:#5c5c6a;--accent:#6366f1;--accent-h:#818cf8;--accent-bg:rgba(99,102,241,0.12);--green:#22c55e;--green-bg:rgba(34,197,94,0.12);--red:#ef4444;--red-bg:rgba(239,68,68,0.12);--radius:12px;--radius-sm:8px}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;justify-content:center;padding:2rem 1rem}
.app{width:100%;max-width:580px}
.header{display:flex;align-items:center;gap:12px;margin-bottom:2rem}
.logo{width:36px;height:36px;background:var(--accent);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:600;color:#fff}
.header h1{font-size:20px;font-weight:600}
.header .sub{font-size:12px;color:var(--text2);margin-top:2px}
.status-bar{display:inline-flex;align-items:center;gap:6px;font-size:11px;padding:4px 10px;border-radius:999px;background:var(--green-bg);color:var(--green);margin-bottom:1rem}
.status-bar .dot{width:6px;height:6px;border-radius:50%;background:var(--green)}
.field{margin-bottom:1rem}
.field label{display:block;font-size:12px;font-weight:500;color:var(--text2);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px}
textarea,select{width:100%;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--text);font-family:inherit;font-size:14px;padding:10px 12px;outline:none;transition:border-color .2s}
textarea:focus,select:focus{border-color:var(--accent)}
textarea{resize:vertical;min-height:80px}
select{cursor:pointer;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%239898a4'%3E%3Cpath d='M6 8L1 3h10z'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;padding-right:32px}
select option{background:var(--bg2);color:var(--text)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:1rem}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:1rem}
.upload-zone{border:1.5px dashed var(--border-h);border-radius:var(--radius);padding:1.5rem;text-align:center;cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.upload-zone:hover{border-color:var(--accent);background:var(--accent-bg)}
.upload-zone.has-image{border-style:solid;border-color:var(--accent);background:var(--bg2)}
.upload-zone input[type=file]{position:absolute;inset:0;opacity:0;cursor:pointer}
.upload-zone img{max-height:180px;max-width:100%;border-radius:var(--radius-sm);margin-bottom:8px}
.upload-icon{font-size:28px;margin-bottom:6px;opacity:.4}
.upload-text{font-size:13px;color:var(--text2)}
.upload-sub{font-size:11px;color:var(--text3);margin-top:4px}
.remove-btn{font-size:12px;color:var(--red);cursor:pointer;margin-top:8px;display:inline-block;position:relative;z-index:2;background:var(--red-bg);padding:3px 10px;border-radius:999px;border:none;font-family:inherit}
.mode-pill{display:inline-block;font-size:11px;padding:3px 10px;border-radius:999px;font-weight:500;margin-left:8px}
.pill-t2v{background:var(--bg3);color:var(--text2)}
.pill-i2v{background:var(--accent-bg);color:var(--accent-h)}
.btn-gen{width:100%;padding:12px;background:var(--accent);color:#fff;font-size:15px;font-weight:500;border:none;border-radius:var(--radius-sm);cursor:pointer;font-family:inherit;transition:background .2s,transform .1s}
.btn-gen:hover{background:var(--accent-h)}
.btn-gen:active{transform:scale(.98)}
.btn-gen:disabled{opacity:.5;cursor:not-allowed;transform:none}
.status-area{margin-top:1rem;min-height:24px}
.status-text{font-size:13px;color:var(--text2)}
.progress{height:3px;background:var(--bg3);border-radius:2px;margin-top:8px;overflow:hidden}
.progress-fill{height:100%;width:0%;background:var(--accent);border-radius:2px;transition:width .4s}
.error-text{font-size:13px;color:var(--red);margin-top:6px}
.video-result{margin-top:1.5rem;padding:1rem;background:var(--bg2);border-radius:var(--radius);border:1px solid var(--border)}
.video-result video{width:100%;border-radius:var(--radius-sm);background:#000}
.video-result a{display:inline-flex;align-items:center;gap:6px;margin-top:10px;font-size:13px;color:var(--accent-h);text-decoration:none}
.video-result a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div class="logo">K</div>
    <div><h1>Kling Video Generator</h1><div class="sub">Text-to-Video & Image-to-Video</div></div>
  </div>
  <div class="status-bar"><span class="dot"></span> Подключено</div>
  <span class="mode-pill pill-t2v" id="modePill">Text-to-Video</span>

  <div class="field" style="margin-top:1rem">
    <label>Картинка (image-to-video)</label>
    <div class="upload-zone" id="uploadZone">
      <input type="file" accept="image/*" id="imageInput" onchange="handleImage(this)">
      <img id="previewImg" style="display:none">
      <div id="uploadHint">
        <div class="upload-icon">🖼</div>
        <div class="upload-text">Нажми или перетащи картинку</div>
        <div class="upload-sub">JPG, PNG, WEBP · до 10MB</div>
      </div>
      <button class="remove-btn" id="removeBtn" style="display:none" onclick="removeImage(event)">✕ Убрать</button>
    </div>
  </div>

  <div class="field"><label>Промпт</label><textarea id="prompt" placeholder="A woman walking through a neon-lit Tokyo street at night, cinematic..."></textarea></div>
  <div class="field"><label>Негативный промпт</label><textarea id="negPrompt" style="min-height:50px" placeholder="blur, low quality, distorted..."></textarea></div>

  <div class="grid3">
    <div class="field"><label>Модель</label><select id="model"><option value="kling-v2-1">v2.1</option><option value="kling-v2-0">v2.0</option><option value="kling-v1-6">v1.6</option><option value="kling-v1-5">v1.5</option></select></div>
    <div class="field"><label>Длительность</label><select id="duration"><option value="5">5 сек</option><option value="10">10 сек</option></select></div>
    <div class="field"><label>Режим</label><select id="modeSelect"><option value="std">Standard</option><option value="pro">Pro</option></select></div>
  </div>
  <div class="grid2">
    <div class="field"><label>Соотношение</label><select id="aspect"><option value="16:9">16:9</option><option value="9:16">9:16 вертикал</option><option value="1:1">1:1 квадрат</option><option value="4:3">4:3</option><option value="3:4">3:4</option><option value="21:9">21:9 широкий</option></select></div>
    <div class="field"><label>CFG Scale</label><select id="cfg"><option value="0.5">0.5 свободно</option><option value="0.7" selected>0.7 баланс</option><option value="1.0">1.0 точно</option></select></div>
  </div>

  <button class="btn-gen" id="genBtn" onclick="generate()">▶ Сгенерировать видео</button>

  <div class="status-area">
    <div class="status-text" id="statusText"></div>
    <div class="progress" id="progressBar" style="display:none"><div class="progress-fill" id="progressFill"></div></div>
    <div class="error-text" id="errorText"></div>
  </div>
  <div class="video-result" id="videoResult" style="display:none">
    <video id="videoEl" controls playsinline></video>
    <a id="downloadLink" href="#" download="kling_video.mp4">⬇ Скачать видео</a>
  </div>
</div>
<script>
const AK='AeBHdraBhTBdbDCm9daeCFnt8MKgNFby',SK='P4HmeLkPGhkH3JRTE4DFNG9KPRGfdKpG';
const PROXY=location.origin+'/proxy';
let imageBase64=null;
function b64u(s){return btoa(unescape(encodeURIComponent(s))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
async function makeJWT(){
  const h=b64u(JSON.stringify({alg:'HS256',typ:'JWT'})),now=Math.floor(Date.now()/1000);
  const p=b64u(JSON.stringify({iss:AK,exp:now+1800,nbf:now-5})),msg=h+'.'+p;
  const enc=new TextEncoder(),key=await crypto.subtle.importKey('raw',enc.encode(SK),{name:'HMAC',hash:'SHA-256'},false,['sign']);
  const sig=await crypto.subtle.sign('HMAC',key,enc.encode(msg));
  return msg+'.'+btoa(String.fromCharCode(...new Uint8Array(sig))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
function handleImage(input){
  const f=input.files[0];if(!f)return;if(f.size>10*1024*1024){setError('Файл > 10MB');return}
  const r=new FileReader();r.onload=e=>{imageBase64=e.target.result;
    document.getElementById('previewImg').src=imageBase64;document.getElementById('previewImg').style.display='block';
    document.getElementById('uploadHint').style.display='none';document.getElementById('removeBtn').style.display='inline-block';
    document.getElementById('uploadZone').classList.add('has-image');
    document.getElementById('modePill').textContent='Image-to-Video';document.getElementById('modePill').className='mode-pill pill-i2v';
  };r.readAsDataURL(f);
}
function removeImage(e){
  e.stopPropagation();e.preventDefault();imageBase64=null;
  document.getElementById('previewImg').style.display='none';document.getElementById('uploadHint').style.display='block';
  document.getElementById('removeBtn').style.display='none';document.getElementById('uploadZone').classList.remove('has-image');
  document.getElementById('imageInput').value='';
  document.getElementById('modePill').textContent='Text-to-Video';document.getElementById('modePill').className='mode-pill pill-t2v';
}
function setStatus(m,p){document.getElementById('statusText').textContent=m;const b=document.getElementById('progressBar'),f=document.getElementById('progressFill');if(p!==undefined){b.style.display='block';f.style.width=p+'%'}else b.style.display='none'}
function setError(m){document.getElementById('errorText').textContent=m}
async function generate(){
  const prompt=document.getElementById('prompt').value.trim();if(!prompt){setError('Введи промпт!');return}
  setError('');document.getElementById('videoResult').style.display='none';document.getElementById('genBtn').disabled=true;
  setStatus('Генерирую JWT...',5);
  try{
    const token=await makeJWT(),model=document.getElementById('model').value,isV2=model.startsWith('kling-v2'),isImg=!!imageBase64;
    const body={model_name:model,prompt,negative_prompt:document.getElementById('negPrompt').value.trim(),duration:document.getElementById('duration').value};
    if(!isImg)body.aspect_ratio=document.getElementById('aspect').value;
    if(!isV2){body.mode=document.getElementById('modeSelect').value;body.cfg_scale=parseFloat(document.getElementById('cfg').value)}
    if(isImg)body.image=imageBase64.split(',')[1];
    const ep=isImg?'/v1/videos/image2video':'/v1/videos/text2video';
    setStatus('Отправляю в Kling...',15);
    const res=await fetch(PROXY+ep,{method:'POST',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(body)});
    const data=await res.json();if(data.code!==0)throw new Error(data.message||JSON.stringify(data));
    setStatus('Задача создана — жду результат...',25);pollTask(data.data.task_id,isImg);
  }catch(e){setError(e.message);setStatus('');document.getElementById('genBtn').disabled=false}
}
function pollTask(tid,isImg){
  let n=0;const ep=isImg?'/v1/videos/image2video/':'/v1/videos/text2video/';
  const poll=async()=>{n++;setStatus('Генерирую видео... '+n*5+'с',Math.min(25+n*.6,92));
    try{const token=await makeJWT(),res=await fetch(PROXY+ep+tid,{headers:{'Authorization':'Bearer '+token}});
      const data=await res.json();if(data.code!==0)throw new Error(data.message);
      const st=data.data?.task_status;
      if(st==='succeed'){const url=data.data.task_result.videos[0].url;setStatus('Готово! 🎬',100);
        document.getElementById('videoEl').src=url;document.getElementById('downloadLink').href=url;
        document.getElementById('videoResult').style.display='block';document.getElementById('genBtn').disabled=false}
      else if(st==='failed')throw new Error(data.data?.task_status_msg||'Провалилась');
      else if(n<120)setTimeout(poll,5000);else throw new Error('Таймаут');
    }catch(e){setError(e.message);setStatus('');document.getElementById('genBtn').disabled=false}
  };setTimeout(poll,5000);
}
</script>
</body></html>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/proxy/'):
            self._proxy('GET')
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path.startswith('/proxy/'):
            self._proxy('POST')
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')

    def _proxy(self, method):
        path = self.path[6:]
        url = KLING + path
        headers = {'Content-Type': 'application/json'}
        auth = self.headers.get('Authorization')
        if auth:
            headers['Authorization'] = auth
        body = None
        if method == 'POST':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Running on port {PORT}")
    server.serve_forever()
