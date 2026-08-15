#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, sys, urllib.request, urllib.error, webbrowser, threading
ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'; PORT=int(os.getenv('NIYET_PORT','8000'))
MODEL=os.getenv('OPENAI_MODEL','gpt-5.6-luna')
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
INTENTS=['Bilgilendirme','Eleştiri','İtiraz','Mizah','Tavsiye','Destek','Soru']
ANALYSIS_SCHEMA={
 'type':'object','properties':{
  'intent_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
  'has_insult':{'type':'boolean'},'has_personal_attack':{'type':'boolean'},'has_dismissive_language':{'type':'boolean'},
  'has_contempt':{'type':'boolean'},'is_unconstructive':{'type':'boolean'},'has_unexplained_contradiction':{'type':'boolean'},
  'escalates_tension':{'type':'boolean'},'is_ambiguous':{'type':'boolean'},'has_risky_irony':{'type':'boolean'},'is_calming':{'type':'boolean'},
  'reason':{'type':'string'}},
 'required':['intent_distribution','has_insult','has_personal_attack','has_dismissive_language','has_contempt','is_unconstructive','has_unexplained_contradiction','escalates_tension','is_ambiguous','has_risky_irony','is_calming','reason'],
 'additionalProperties':False}

def extract_text(data):
    out=[]
    for item in data.get('output',[]):
        if item.get('type')=='message':
            for c in item.get('content',[]):
                if c.get('type')=='output_text' and c.get('text'): out.append(c['text'])
    return '\n'.join(out).strip()

def call_responses(input_items,max_output=350,schema=None):
    if not API_KEY: raise RuntimeError('OpenAI API bağlantısı yapılmadı.')
    payload={'model':MODEL,'reasoning':{'effort':'low'},'input':input_items,'max_output_tokens':max_output,'store':False}
    if schema:
        payload['text']={'format':{'type':'json_schema','name':'niyet_analysis','strict':True,'schema':schema}}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':f'Bearer {API_KEY}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=60) as r: data=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode('utf-8','replace')
        try: detail=json.loads(body).get('error',{}).get('message',body)
        except Exception: detail=body
        raise RuntimeError(f'OpenAI API hatası ({e.code}): {detail}')
    text=extract_text(data)
    if not text: raise RuntimeError('Model yanıt üretmedi.')
    return json.loads(text) if schema else text

def persona_instruction(pid):
    name,style,bio=PERSONAS[pid]
    return f'''Sen {name} adlı NİYET prototipindeki sentetik sosyal medya kullanıcısısın. Üslubun: {style}. Profilin: {bio}
Türkçe, doğal ve kısa yaz; çoğu cevap 1-3 cümle. Bağlama sadık kal. Karakteri abartma. Hakaret üretme; sert kullanıcıya sakin sınır koyabilirsin. Markdown kullanma.'''

def analysis_prompt(text,context='',selected_intent=''):
    return [{'role':'developer','content':'''NİYET iletişim analiz motorusun. Metni kişi hakkında ahlaki hüküm vermeden yalnızca iletişim davranışı açısından sınıflandır.
Boole alanlarını yalnızca metinde veya verilen bağlamda açık kanıt varsa true yap. Sıradan kısa sohbeti "yapıcı değil" diye cezalandırma. Eleştiri tek başına saldırı değildir. Görüş değişikliği gerekçeliyse çelişki sayma.
intent_distribution alanındaki yedi değeri 0-100 arasında göreli kanıt olarak ver; toplamın tam 100 olması şart değil. reason en fazla 2 kısa Türkçe cümle olsun.'''} ,
      {'role':'user','content':f'Seçilen niyet: {selected_intent or "belirtilmedi"}\nBağlam: {context or "yok"}\nAnaliz edilecek metin: {text}'}]

def analyze(text,context='',selected_intent=''):
    return call_responses(analysis_prompt(text,context,selected_intent),350,ANALYSIS_SCHEMA)

def chat(pid,history):
    items=[{'role':'developer','content':persona_instruction(pid)}]
    for m in history[-12:]:
        txt=str(m.get('text','')).strip()
        if txt and txt!='…': items.append({'role':'user' if m.get('from')=='me' else 'assistant','content':txt})
    return call_responses(items,180)

def bot_reply(pid,post_text,user_comment='',comments=None):
    comments=comments or []
    context='\n'.join([f"- {c.get('text','')}" for c in comments[-5:]])
    prompt=f'''Ana paylaşım: {post_text}\nSon yorumlar:\n{context or '- yok'}\n'''
    if user_comment: prompt+=f'Kullanıcının sana/konuya son yorumu: {user_comment}\nBu yoruma bağlamlı bir yanıt ver.'
    else: prompt+='Bu paylaşıma karakterine uygun, doğal ve konuya bağlı bir ilk yorum yaz.'
    return call_responses([{'role':'developer','content':persona_instruction(pid)},{'role':'user','content':prompt}],180)

def validate_key(key):
    req=urllib.request.Request('https://api.openai.com/v1/models',headers={'Authorization':f'Bearer {key}'})
    with urllib.request.urlopen(req,timeout=20) as r: return r.status<300

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,fmt,*a): sys.stdout.write('[NİYET V7] '+fmt%a+'\n')
    def send_json(self,o,status=200):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/status': return self.send_json({'configured':bool(API_KEY),'model':MODEL})
        if self.path=='/': self.path='/index.html'
        return super().do_GET()
    def do_POST(self):
        global API_KEY,MODEL
        try:
            n=int(self.headers.get('Content-Length','0')); d=json.loads(self.rfile.read(n).decode())
            if self.path=='/api/config':
                key=str(d.get('api_key','')).strip(); model=str(d.get('model','')).strip() or 'gpt-5.6-luna'
                if not key: return self.send_json({'error':'API anahtarı boş.'},400)
                validate_key(key); API_KEY=key; MODEL=model
                return self.send_json({'ok':True,'model':MODEL})
            if not API_KEY: return self.send_json({'error':'OpenAI API bağlantısı gerekli.','needs_config':True},401)
            if self.path=='/api/analyze':
                a=analyze(str(d.get('text','')),str(d.get('context','')),str(d.get('selected_intent','')))
                return self.send_json({'analysis':a,'model':MODEL})
            if self.path=='/api/chat':
                pid=str(d.get('person_id','')); hist=d.get('history') or []
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                user_text=''
                for m in reversed(hist):
                    if m.get('from')=='me': user_text=str(m.get('text','')); break
                a=analyze(user_text,'Özel sohbet mesajı') if user_text else None
                reply=chat(pid,hist)
                return self.send_json({'reply':reply,'analysis':a,'model':MODEL})
            if self.path=='/api/bot_comment':
                pid=str(d.get('person_id','')); post=str(d.get('post_text','')); user_comment=str(d.get('user_comment','')); comments=d.get('comments') or []
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                user_analysis=analyze(user_comment,f'Ana paylaşım: {post}') if user_comment else None
                reply=bot_reply(pid,post,user_comment,comments)
                reply_analysis=analyze(reply,f'Ana paylaşım: {post}')
                return self.send_json({'reply':reply,'user_analysis':user_analysis,'reply_analysis':reply_analysis,'model':MODEL})
            return self.send_json({'error':'Not found'},404)
        except Exception as e: return self.send_json({'error':str(e)},503)

def main():
    print('\nNİYET V7 — GPT-5.6 Luna + API davranış analizi + 25 mikro video')
    url=f'http://{HOST}:{PORT}'; srv=ThreadingHTTPServer((HOST,PORT),Handler)
    print('Açılıyor:',url); print('Varsayılan model:',MODEL); print('Kapatmak için Ctrl+C')
    threading.Timer(.7,lambda:webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()
if __name__=='__main__': main()
