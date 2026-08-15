#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, sys, urllib.request, urllib.error, webbrowser, threading, math

ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'
PORT=int(os.getenv('NIYET_PORT','8819'))
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

INTENTS=['Bilgilendirme','Eleştiri','İtiraz','Mizah','Tavsiye','Destek / Övgü','Soru']

CORE_PROPERTIES={
  'intent_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
  'has_insult':{'type':'boolean'},'has_personal_attack':{'type':'boolean'},'has_dismissive_language':{'type':'boolean'},'has_contempt':{'type':'boolean'},
  'is_unconstructive':{'type':'boolean'},'has_unexplained_contradiction':{'type':'boolean'},'escalates_tension':{'type':'boolean'},'is_ambiguous':{'type':'boolean'},'has_risky_irony':{'type':'boolean'},
  'is_calming':{'type':'boolean'},'is_polite':{'type':'boolean'},'apologizes':{'type':'boolean'},'acknowledges_other':{'type':'boolean'},'returns_to_topic':{'type':'boolean'},
  'has_reasoning':{'type':'boolean'},'offers_alternative':{'type':'boolean'},'asks_constructive_question':{'type':'boolean'},'is_clear':{'type':'boolean'},'is_respectful':{'type':'boolean'},'explains_change':{'type':'boolean'},
  'reason':{'type':'string'}
}
CORE_REQUIRED=list(CORE_PROPERTIES.keys())

def core_schema():
    return {'type':'object','properties':CORE_PROPERTIES,'required':CORE_REQUIRED,'additionalProperties':False}

COUNTERFACTUAL_SCHEMA={
  'type':'object',
  'properties':{
    'text':{'type':'string'},
    'goal':{'type':'string'},
    'intent_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
    'reason':{'type':'string'}
  },
  'required':['text','goal','intent_distribution','reason'],
  'additionalProperties':False
}

ANALYSIS_SCHEMA={
  'type':'object',
  'properties':{**CORE_PROPERTIES,'counterfactuals':{'type':'array','items':COUNTERFACTUAL_SCHEMA}},
  'required':CORE_REQUIRED+['counterfactuals'],
  'additionalProperties':False
}

CHAT_SCHEMA={
  'type':'object',
  'properties':{'reply':{'type':'string'},'user_analysis':core_schema(),'reply_analysis':core_schema()},
  'required':['reply','user_analysis','reply_analysis'],
  'additionalProperties':False
}

BOT_COMMENT_SCHEMA=CHAT_SCHEMA

DEFAULT_CALIBRATION={
  'version':'survey-pending-v1',
  'status':'survey_pending',
  'human_labels':0,
  'target_human_labels':3600,
  'unique_messages':450,
  'temperature':1.0,
  'class_bias':{k:1.0 for k in INTENTS},
  'uncertainty_high':62,
  'drift_margin':12,
  'drift_min_dominant':45
}

def load_calibration():
    p=ROOT/'calibration_profile.json'
    if not p.exists(): return DEFAULT_CALIBRATION.copy()
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        out=DEFAULT_CALIBRATION.copy(); out.update(data)
        b=DEFAULT_CALIBRATION['class_bias'].copy(); b.update(data.get('class_bias') or {}); out['class_bias']=b
        return out
    except Exception as e:
        print('[NİYET V9] calibration_profile.json okunamadı:',e)
        return DEFAULT_CALIBRATION.copy()

CALIBRATION=load_calibration()

def extract_text(data):
    out=[]
    for item in data.get('output',[]):
        if item.get('type')=='message':
            for c in item.get('content',[]):
                if c.get('type')=='output_text' and c.get('text'): out.append(c['text'])
    return '\n'.join(out).strip()

def call_responses(input_items,max_output=900,schema=None,schema_name='niyet_analysis'):
    if not API_KEY: raise RuntimeError('OpenAI API bağlantısı yapılmadı.')
    payload={'model':MODEL,'reasoning':{'effort':'low'},'input':input_items,'max_output_tokens':max_output,'store':False}
    if schema:
        payload['text']={'format':{'type':'json_schema','name':schema_name,'strict':True,'schema':schema}}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':f'Bearer {API_KEY}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=75) as r: data=json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body=e.read().decode('utf-8','replace')
        try: detail=json.loads(body).get('error',{}).get('message',body)
        except Exception: detail=body
        raise RuntimeError(f'OpenAI API hatası ({e.code}): {detail}')
    text=extract_text(data)
    if not text: raise RuntimeError('Model yanıt üretmedi.')
    return json.loads(text) if schema else text

def normalize_dist(dist):
    vals={k:max(0.0,float((dist or {}).get(k,0) or 0)) for k in INTENTS}
    total=sum(vals.values()) or 1.0
    return {k:vals[k]/total for k in INTENTS}

def calibrate_distribution(dist):
    p=normalize_dist(dist)
    temp=max(.25,float(CALIBRATION.get('temperature',1.0) or 1.0))
    bias=CALIBRATION.get('class_bias') or {}
    adjusted={}
    for k,v in p.items():
        adjusted[k]=(max(v,1e-9)**(1.0/temp))*max(.01,float(bias.get(k,1.0) or 1.0))
    total=sum(adjusted.values()) or 1.0
    exact={k:adjusted[k]/total*100 for k in INTENTS}
    rounded={k:int(round(exact[k])) for k in INTENTS}
    diff=100-sum(rounded.values())
    if diff:
        top=max(exact,key=exact.get); rounded[top]+=diff
    return rounded

def normalized_entropy(dist):
    p=normalize_dist(dist)
    h=-sum(v*math.log(v) for v in p.values() if v>0)
    return round(100*h/math.log(len(INTENTS)),1)

def shift_type(a,selected,dominant):
    if selected==dominant: return 'Belirgin algı sapması yok'
    if selected=='Mizah' and (a.get('has_risky_irony') or a.get('has_contempt')): return 'Mizah → Alay / küçümseme algısı'
    if selected=='Eleştiri' and a.get('has_personal_attack'): return 'Eleştiri → Kişisel saldırı algısı'
    if selected=='Tavsiye' and (a.get('has_dismissive_language') or a.get('has_contempt')): return 'Tavsiye → Üstten / kovucu konuşma algısı'
    if selected=='Soru' and (a.get('has_personal_attack') or a.get('has_contempt')): return 'Soru → İma / suçlama algısı'
    if selected=='Bilgilendirme' and dominant in ('Eleştiri','İtiraz'): return f'Bilgilendirme → {dominant} algısı'
    if selected=='Destek / Övgü' and dominant=='Mizah': return 'Destek / Övgü → İronik algı'
    return f'{selected} → {dominant} algısı'

def decision_layer(a,selected_intent=''):
    calibrated=calibrate_distribution(a.get('intent_distribution') or {})
    a['raw_intent_distribution']=a.get('intent_distribution') or {}
    a['intent_distribution']=calibrated
    uncertainty=normalized_entropy(calibrated)
    dominant=max(calibrated,key=calibrated.get)
    selected=selected_intent if selected_intent in INTENTS else ''
    selected_share=float(calibrated.get(selected,0)) if selected else 0.0
    dominant_share=float(calibrated.get(dominant,0))
    mismatch=max(0,100-selected_share) if selected else uncertainty
    high_uncertainty=uncertainty>=float(CALIBRATION.get('uncertainty_high',62))
    drift=False
    if selected:
        drift=(not high_uncertainty and dominant!=selected and dominant_share>=float(CALIBRATION.get('drift_min_dominant',45)) and dominant_share-selected_share>=float(CALIBRATION.get('drift_margin',12)))
    if high_uncertainty: status='Yüksek algı belirsizliği — kesin hüküm verilmedi'
    elif drift: status='Belirgin niyet kayması'
    else: status='Belirgin niyet kayması yok'
    a['decision_layer']={
      'selected_intent':selected,
      'dominant_intent':dominant,
      'dominant_share':round(dominant_share,1),
      'selected_share':round(selected_share,1),
      'intent_match':round(selected_share,1) if selected else None,
      'misunderstanding_risk':round(mismatch,1),
      'perception_uncertainty':uncertainty,
      'high_uncertainty':high_uncertainty,
      'intent_drift':drift,
      'decision_status':status,
      'shift_type':shift_type(a,selected,dominant) if selected else 'Yazar niyeti belirtilmedi'
    }
    a['calibration_meta']={
      'status':CALIBRATION.get('status','survey_pending'),
      'version':CALIBRATION.get('version',''),
      'human_labels':int(CALIBRATION.get('human_labels',0) or 0),
      'target_human_labels':int(CALIBRATION.get('target_human_labels',3600) or 3600),
      'unique_messages':int(CALIBRATION.get('unique_messages',450) or 450),
      'model_independent':True
    }
    return a

def calibrate_counterfactuals(a,selected_intent=''):
    out=[]
    for item in (a.get('counterfactuals') or [])[:3]:
        dist=calibrate_distribution(item.get('intent_distribution') or {})
        uncertainty=normalized_entropy(dist)
        selected_share=float(dist.get(selected_intent,0)) if selected_intent in INTENTS else 0
        out.append({**item,'intent_distribution':dist,'perception_uncertainty':uncertainty,'selected_share':selected_share,'misunderstanding_risk':max(0,100-selected_share)})
    a['counterfactuals']=out
    return a

def persona_instruction(pid):
    name,style,bio=PERSONAS[pid]
    return f'''Sen {name} adlı NİYET prototipindeki sentetik sosyal medya kullanıcısısın. Üslubun: {style}. Profilin: {bio}
Türkçe, doğal ve kısa yaz; çoğu cevap 1-3 cümle. Bağlama sadık kal. Karakteri abartma. Hakaret üretme. NİYET sosyal sinyalleri yüksek belirsizlik gösteriyorsa karşı tarafın niyetini kesin varsayma; gerekirse kısa bir açıklama sorusu sor. Gerilim sinyali yüksekse karakterini koruyarak gerilimi büyütme. Markdown kullanma.'''

ANALYSIS_RUBRIC='''NİYET iletişim analiz motorusun. Metni kişi hakkında ahlaki hüküm vermeden yalnızca iletişim davranışı açısından sınıflandır.
Yazarın seçtiği niyet, yazarın kendi beyanıdır; okuyucu algısını buna zorla uydurma. intent_distribution okuyucuların mesajı nasıl algılayebileceğini temsil etsin.
Boole alanlarını yalnızca metinde veya verilen bağlamda açık kanıt varsa true yap. Sıradan kısa sohbeti yapıcı değil diye cezalandırma. Eleştiri tek başına saldırı değildir. Görüş değişikliği gerekçeliyse çelişki sayma. Nezaket, özür, karşı tarafı anlama, konuya dönüş, gerekçe, alternatif, yapıcı soru ve açıklık sinyallerini ayrı sınıflandır.
intent_distribution değerleri 0-100 arası göreli kanıttır; toplamın 100 olması şart değildir. reason en fazla 2 kısa Türkçe cümle olsun.'''

def analysis_prompt(text,context='',selected_intent=''):
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+'''\nAyrıca tam 3 karşı-olgusal minimal alternatif üret. Alternatifler metni baştan yazmamalı; yalnızca algıyı değiştiren küçük ifade değişiklikleri yapmalı. Her alternatif için beklenen okuyucu niyet dağılımını da üret.'''} ,
      {'role':'user','content':f'Yazarın seçtiği niyet: {selected_intent or "belirtilmedi"}\nBağlam: {context or "yok"}\nAnaliz edilecek metin: {text}'}
    ]

def analyze(text,context='',selected_intent=''):
    a=call_responses(analysis_prompt(text,context,selected_intent),950,ANALYSIS_SCHEMA,'niyet_post_analysis')
    a=decision_layer(a,selected_intent)
    return calibrate_counterfactuals(a,selected_intent)

def chat_combined(pid,history):
    hist=history[-12:]
    lines=[]
    for m in hist:
        txt=str(m.get('text','')).strip()
        if txt and txt!='…': lines.append(('Kullanıcı' if m.get('from')=='me' else PERSONAS[pid][0])+': '+txt)
    last_user=''
    for m in reversed(hist):
        if m.get('from')=='me': last_user=str(m.get('text','')).strip(); break
    prompt=f'''Konuşma:\n{chr(10).join(lines) or '- boş'}\n\nSon kullanıcı mesajı: {last_user or '-'}\n\nTek JSON çıktıda: (1) karaktere uygun reply yaz, (2) son kullanıcı mesajını iletişim açısından user_analysis olarak analiz et, (3) kendi üreteceğin reply mesajını reply_analysis olarak analiz et. Analizlerde yedi niyet dağılımı okuyucu algısını temsil etsin.'''
    d=call_responses([{'role':'developer','content':persona_instruction(pid)+'\n\n'+ANALYSIS_RUBRIC},{'role':'user','content':prompt}],800,CHAT_SCHEMA,'niyet_chat_turn')
    d['user_analysis']=decision_layer(d['user_analysis'],'')
    d['reply_analysis']=decision_layer(d['reply_analysis'],'')
    return d

def bot_comment_combined(pid,post_text,user_comment='',comments=None):
    comments=comments or []
    context='\n'.join([f"- {c.get('text','')}" for c in comments[-5:]])
    prompt=f'''Ana paylaşım: {post_text}\nSon yorumlar:\n{context or '- yok'}\nKullanıcının son yorumu: {user_comment or '- yok; ilk yorum üret'}\n\nTek JSON çıktıda: (1) karaktere uygun kısa reply üret, (2) kullanıcı yorumu varsa user_analysis olarak analiz et; yoksa nötr bir analiz üret, (3) kendi reply mesajını reply_analysis olarak analiz et. Yüksek algı belirsizliğinde kullanıcının niyetini kesin varsayma; yüksek gerilimde yanıtı büyütme.'''
    d=call_responses([{'role':'developer','content':persona_instruction(pid)+'\n\n'+ANALYSIS_RUBRIC},{'role':'user','content':prompt}],850,BOT_COMMENT_SCHEMA,'niyet_comment_turn')
    d['user_analysis']=decision_layer(d['user_analysis'],'')
    d['reply_analysis']=decision_layer(d['reply_analysis'],'')
    return d

def validate_key(key):
    req=urllib.request.Request('https://api.openai.com/v1/models',headers={'Authorization':f'Bearer {key}'})
    with urllib.request.urlopen(req,timeout=20) as r: return r.status<300

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma','no-cache'); self.send_header('Expires','0'); super().end_headers()
    def __init__(self,*a,**kw): super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,fmt,*a): sys.stdout.write('[NİYET V9] '+fmt%a+'\n')
    def send_json(self,o,status=200):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/status':
            return self.send_json({'configured':bool(API_KEY),'model':MODEL,'version':'9.0','calibration':{'status':CALIBRATION.get('status'),'version':CALIBRATION.get('version'),'human_labels':CALIBRATION.get('human_labels',0),'target_human_labels':CALIBRATION.get('target_human_labels',3600),'model_independent':True}})
        if self.path=='/': self.path='/index.html'
        return super().do_GET()
    def do_POST(self):
        global API_KEY,MODEL,CALIBRATION
        try:
            n=int(self.headers.get('Content-Length','0')); d=json.loads(self.rfile.read(n).decode())
            if self.path=='/api/config':
                key=str(d.get('api_key','')).strip(); model=str(d.get('model','')).strip() or 'gpt-5.6-luna'
                if not key: return self.send_json({'error':'API anahtarı boş.'},400)
                validate_key(key); API_KEY=key; MODEL=model
                return self.send_json({'ok':True,'model':MODEL})
            if self.path=='/api/reload_calibration':
                CALIBRATION=load_calibration(); return self.send_json({'ok':True,'calibration':CALIBRATION})
            if not API_KEY: return self.send_json({'error':'OpenAI API bağlantısı gerekli.','needs_config':True},401)
            if self.path=='/api/analyze':
                a=analyze(str(d.get('text','')),str(d.get('context','')),str(d.get('selected_intent','')))
                return self.send_json({'analysis':a,'model':MODEL,'version':'9.0'})
            if self.path=='/api/chat':
                pid=str(d.get('person_id','')); hist=d.get('history') or []; opening=bool(d.get('opening',False))
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                if opening and not hist: hist=[{'from':'me','text':'Konuşmayı sen başlat: doğal, kısa bir selam ver ve halimi sor.'}]
                out=chat_combined(pid,hist)
                return self.send_json({'reply':out['reply'],'analysis':out['user_analysis'],'reply_analysis':out['reply_analysis'],'model':MODEL,'version':'9.0'})
            if self.path=='/api/bot_comment':
                pid=str(d.get('person_id','')); post=str(d.get('post_text','')); user_comment=str(d.get('user_comment','')); comments=d.get('comments') or []
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                out=bot_comment_combined(pid,post,user_comment,comments)
                return self.send_json({'reply':out['reply'],'user_analysis':out['user_analysis'],'reply_analysis':out['reply_analysis'],'model':MODEL,'version':'9.0'})
            return self.send_json({'error':'Not found'},404)
        except Exception as e:
            return self.send_json({'error':str(e)},503)

def main():
    print('\nNİYET V9 — GPT-5.6 Luna + insan kalibrasyon katmanı + sosyal dinamikler')
    url=f'http://{HOST}:{PORT}/?v=9.0'; srv=ThreadingHTTPServer((HOST,PORT),Handler)
    print('Açılıyor:',url); print('Varsayılan model:',MODEL); print('Kalibrasyon:',CALIBRATION.get('status'),CALIBRATION.get('human_labels',0),'/',CALIBRATION.get('target_human_labels',3600)); print('Kapatmak için Ctrl+C')
    threading.Timer(.7,lambda:webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()

if __name__=='__main__': main()
