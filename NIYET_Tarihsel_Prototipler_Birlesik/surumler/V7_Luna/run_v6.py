#!/usr/bin/env python3
# NİYET V6.2 local server: built only with Python standard library.
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, sys, getpass, urllib.request, urllib.error, webbrowser, threading

ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'; PORT=int(os.getenv('NIYET_PORT','8000'))
MODEL=os.getenv('OPENAI_MODEL','gpt-5.6')
API_KEY=os.getenv('OPENAI_API_KEY','').strip()
PERSONAS={
'sila':('Sıla Demir','sakin, yapıcı ve uzlaştırıcı','Psikoloji öğrencisi; kitaplar, eğitim ve günlük yaşam.'),
'ahmet':('Ahmet Yılmaz','net, doğrudan ve tartışmacı ama saygılı','Mühendislik öğrencisi; şehir, teknoloji ve ulaşım.'),
'mert':('Mert Kaya','hafif ironik, esprili ve sivri; doğrudan hakaret etmez','Gündem, teknoloji ve mizah.'),
'elif':('Elif Aydın','analitik, veri odaklı ve meraklı','Veri bilimi meraklısı; iddiaların kaynağını konuşmayı sever.'),
'can':('Can Aras','kısa, gündelik ve duygusal','Spor, müzik ve gündelik hayat.'),
'zeynep':('Zeynep Koç','uzlaştırıcı, karşı görüşe açık ve dengeli','Hukuk öğrencisi; farklı görüşlerin bir arada kalmasıyla ilgileniyor.'),
'ayse':('Ayşe Kara','nazik, meraklı ve yaratıcı','Eğitim teknolojileri ve tasarım.'),
'burak':('Burak Şen','doğrudan, teknik ve gündelik','Yazılım, oyun ve dijital kültür.'),
'deniz':('Deniz Eren','sorgulayıcı ve bilimsel','Bilim, çevre ve şehir yaşamı.'),
'ece':('Ece Toprak','pozitif, görsel düşünen ve sıcak','Sanat, fotoğraf ve sürdürülebilir yaşam.'),
'emre':('Emre Akın','eleştirel ve ekonomi odaklı','Ekonomi ve teknoloji gündemi.'),
'irem':('İrem Çelik','empatik ve düşünceli','Psikoloji, gençlik ve sosyal medya.'),
'kaan':('Kaan Öz','rekabetçi, enerjik ama saygılı','Spor, teknoloji ve girişimcilik.'),
'lara':('Lara Tunç','yaratıcı ve görsel anlatımı seven','Görsel tasarım, AI ve kısa videolar.'),
'mehmet':('Mehmet Aslan','ölçülü ve geleneksel','Tarih, şehir kültürü ve gündem.'),
'naz':('Naz Ergin','mizahi, hızlı ve gündelik','Gündelik hayat ve internet kültürü.'),
'okan':('Okan Yıldız','analitik ve teknik','Mühendislik, enerji ve verimlilik.'),
'pelin':('Pelin Güneş','sakin ve kültür odaklı','Kitap, sinema ve eğitim.'),
'selim':('Selim Baran','iddialı ve girişimci','Teknoloji politikaları ve girişimler.'),
'yasemin':('Yasemin Uçar','dengeleyici ve sosyal psikoloji odaklı','Sosyal psikoloji ve dijital topluluklar.')}

def instructions(pid):
    name,style,bio=PERSONAS[pid]
    return f'''Sen {name} adlı NİYET sosyal medya prototipindeki sentetik kullanıcı karakterisin.
Üslup: {style}. Profil: {bio}
Türkçe, doğal, gündelik ve kısa konuş; çoğu cevap 1-3 kısa cümle olsun.
Önceki mesajları dikkatle takip et. Kullanıcının kısa takip mesajlarını bağlamdan anla.
Kullanıcı sadece “selam” derse doğal biçimde selam ver ve halini sor. “İyi sen?” gibi yanıta önceki hal-hatır bağlamına uygun cevap ver.
Kullanıcı bir konu açarsa konu üzerinde kal; sebepsiz konu değiştirme. Soru sorarsa önce doğrudan cevap ver.
Karakteri abartma: Mert her mesajda şaka yapmasın, Elif her mesajda veri istemesin.
Sert mesajda sakin sınır koyabilirsin ama vaaz verme. NİYET skoru hesaplama; skor motoru uygulamada ayrıdır.
Markdown/madde işareti kullanma. Doğrudan AI olup olmadığın sorulursa sentetik prototip karakteri olduğunu açıkça söyle.'''

def extract_text(data):
    parts=[]
    for item in data.get('output',[]):
        if item.get('type')=='message':
            for c in item.get('content',[]):
                if c.get('type')=='output_text' and c.get('text'): parts.append(c['text'])
    return '\n'.join(parts).strip()

def validate_api_key(key):
    req=urllib.request.Request('https://api.openai.com/v1/models',headers={'Authorization':f'Bearer {key}'},method='GET')
    try:
        with urllib.request.urlopen(req,timeout=20) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        body=e.read().decode('utf-8','replace')
        try: detail=json.loads(body).get('error',{}).get('message',body)
        except Exception: detail=body
        raise RuntimeError(f'OpenAI API anahtarı doğrulanamadı ({e.code}): {detail}')

def ask_openai(pid,history,opening=False):
    if not API_KEY: raise RuntimeError('OPENAI_API_KEY tanımlı değil')
    dev=instructions(pid)
    if opening:
        dev += "\nBu konuşmanın ilk mesajını sen başlat. Kısa, doğal ve karakterine uygun bir selamlaşma yaz; genellikle selam verip halini sor. 1-2 kısa cümleyi geçme."
    input_items=[{'role':'developer','content':dev}]
    for m in history[-12:]:
        text=str(m.get('text','')).strip()
        if not text or text=='…': continue
        input_items.append({'role':'user' if m.get('from')=='me' else 'assistant','content':text})
    payload={'model':MODEL,'reasoning':{'effort':'low'},'input':input_items,'max_output_tokens':180,'store':False}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers={'Content-Type':'application/json','Authorization':f'Bearer {API_KEY}'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=45) as resp: data=json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body=e.read().decode('utf-8','replace')
        try: detail=json.loads(body).get('error',{}).get('message',body)
        except Exception: detail=body
        raise RuntimeError(f'OpenAI API hatası ({e.code}): {detail}')
    text=extract_text(data)
    if not text: raise RuntimeError('Model metin yanıtı üretmedi')
    return text

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,fmt,*args): sys.stdout.write('[NİYET] '+(fmt%args)+'\n')
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=='/api/status': return self.send_json({'configured':bool(API_KEY),'model':MODEL,'mode':'openai' if API_KEY else 'not_configured'})
        if self.path=='/': self.path='/index.html'
        return super().do_GET()
    def do_POST(self):
        global API_KEY, MODEL
        try:
            length=int(self.headers.get('Content-Length','0'))
            data=json.loads(self.rfile.read(length).decode('utf-8'))
            if self.path=='/api/config':
                key=str(data.get('api_key','')).strip()
                model=str(data.get('model','')).strip() or MODEL
                if not key: return self.send_json({'error':'API anahtarı boş bırakılamaz.'},400)
                validate_api_key(key)
                API_KEY=key; MODEL=model
                return self.send_json({'ok':True,'configured':True,'model':MODEL})
            if self.path=='/api/chat':
                if not API_KEY: return self.send_json({'error':'OpenAI API bağlantısı yapılmadı. Önce API anahtarını bağlayın.','needs_config':True},401)
                pid=str(data.get('person_id','')); history=data.get('history') or []
                opening=bool(data.get('opening',False))
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                reply=ask_openai(pid,history,opening=opening)
                return self.send_json({'reply':reply,'mode':'openai','model':MODEL})
            return self.send_json({'error':'Not found'},404)
        except Exception as e:
            return self.send_json({'error':str(e)},503)

def main():
    global MODEL
    print('\nNİYET V6.2 — yalnızca OpenAI sohbetli prototip')
    url=f'http://{HOST}:{PORT}'
    server=ThreadingHTTPServer((HOST,PORT),Handler)
    print('Açılıyor:',url)
    print('OpenAI bağlantısı tarayıcı arayüzünden yapılacak.')
    print('Kapatmak için Ctrl+C.')
    threading.Timer(.8,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print('\nKapatıldı.')
    finally: server.server_close()

if __name__=='__main__': main()
