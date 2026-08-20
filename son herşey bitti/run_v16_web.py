#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, sys, urllib.request, urllib.error, threading, math, re, difflib, concurrent.futures, copy, hashlib, time

ROOT=Path(__file__).resolve().parent
HOST=os.getenv('HOST','0.0.0.0')
PORT=int(os.getenv('PORT',os.getenv('NIYET_PORT','10000')))
MODEL=os.getenv('OPENAI_MODEL','gpt-5.6-luna')
API_KEY=os.getenv('OPENAI_API_KEY','').strip()
WEB_MODE=os.getenv('NIYET_WEB_MODE','1').strip()!='0'
RATE_LIMIT_PER_MIN=max(10,int(os.getenv('NIYET_RATE_LIMIT_PER_MIN','60')))
_RATE_LOCK=threading.Lock()
_RATE_BUCKETS={}

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
'yasemin':('Yasemin Uçar','dengeleyici ve sosyal psikoloji odaklı','Sosyal psikoloji ve dijital topluluklar.'),
'tolga':('Tolga Sert','sert konuşma tarzı test botu; keskin ve meydan okuyan ama hakaretsiz','NİYET dijital güvenlik katmanını sınamak için sentetik test profili.'),
'berk':('Berk Koral','sert konuşma tarzı test botu; ısrarcı ve baskın ama hakaretsiz','NİYET erken uyarı ve sınır ihlali algısını sınamak için sentetik test profili.')}

INTENTS=['Bilgilendirme','Eleştiri','İtiraz','Mizah','Tavsiye','Destek / Övgü','Soru']

CORE_PROPERTIES={
  'intent_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
  'has_insult':{'type':'boolean'},'has_personal_attack':{'type':'boolean'},'has_dismissive_language':{'type':'boolean'},'has_contempt':{'type':'boolean'},
  'is_unconstructive':{'type':'boolean'},'has_unexplained_contradiction':{'type':'boolean'},'escalates_tension':{'type':'boolean'},'is_ambiguous':{'type':'boolean'},'has_risky_irony':{'type':'boolean'},
  'is_calming':{'type':'boolean'},'is_polite':{'type':'boolean'},'apologizes':{'type':'boolean'},'acknowledges_other':{'type':'boolean'},'returns_to_topic':{'type':'boolean'},
  'has_reasoning':{'type':'boolean'},'offers_alternative':{'type':'boolean'},'asks_constructive_question':{'type':'boolean'},'is_clear':{'type':'boolean'},'is_respectful':{'type':'boolean'},'explains_change':{'type':'boolean'},
  'has_boundary_violation':{'type':'boolean'},'has_repeated_unwanted_contact':{'type':'boolean'},'has_threat_or_intimidation':{'type':'boolean'},'has_sexual_harassment_signal':{'type':'boolean'},
  'reason':{'type':'string'}
}
CORE_REQUIRED=list(CORE_PROPERTIES.keys())

def core_schema():
    return {'type':'object','properties':CORE_PROPERTIES,'required':CORE_REQUIRED,'additionalProperties':False}

STABILITY_VARIANT_SCHEMA={
  'type':'object',
  'properties':{
    'id':{'type':'string'},
    'text':{'type':'string'},
    'change':{'type':'string'}
  },
  'required':['id','text','change'],
  'additionalProperties':False
}

ANALYSIS_SCHEMA={
  'type':'object',
  'properties':{**CORE_PROPERTIES,'stability_variants':{'type':'array','items':STABILITY_VARIANT_SCHEMA}},
  'required':CORE_REQUIRED+['stability_variants'],
  'additionalProperties':False
}

INTERVENTION_CANDIDATE_SCHEMA={
  'type':'object',
  'properties':{
    'id':{'type':'string'},
    'text':{'type':'string'},
    'change':{'type':'string'}
  },
  'required':['id','text','change'],
  'additionalProperties':False
}
INTERVENTION_SCHEMA={
  'type':'object',
  'properties':{'candidates':{'type':'array','items':INTERVENTION_CANDIDATE_SCHEMA}},
  'required':['candidates'],
  'additionalProperties':False
}

BATCH_ITEM_SCHEMA={
  'type':'object',
  'properties':{
    'id':{'type':'string'},
    'intent_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
    'reason':{'type':'string'}
  },
  'required':['id','intent_distribution','reason'],
  'additionalProperties':False
}
BATCH_SCHEMA={
  'type':'object',
  'properties':{'items':{'type':'array','items':BATCH_ITEM_SCHEMA}},
  'required':['items'],
  'additionalProperties':False
}

CONTEXT_SHADOW_SCHEMA={
  'type':'object',
  'properties':{
    'standalone_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
    'contextual_distribution':{'type':'object','properties':{k:{'type':'integer'} for k in INTENTS},'required':INTENTS,'additionalProperties':False},
    'context_relevance':{'type':'integer','minimum':0,'maximum':100},
    'context_dependency':{'type':'boolean'},
    'standalone_reason':{'type':'string'},
    'contextual_reason':{'type':'string'}
  },
  'required':['standalone_distribution','contextual_distribution','context_relevance','context_dependency','standalone_reason','contextual_reason'],
  'additionalProperties':False
}

_CACHE_LOCK=threading.Lock()
_FAST_CACHE={}
_ENRICH_CACHE={}
_SHADOW_CACHE={}
_CACHE_LIMIT=160

def _cache_key(*parts):
    raw=json.dumps(parts,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def _cache_get(store,key):
    with _CACHE_LOCK:
        val=store.get(key)
        return copy.deepcopy(val) if val is not None else None

def _cache_put(store,key,value):
    with _CACHE_LOCK:
        if len(store)>=_CACHE_LIMIT:
            # insertion-ordered dict: remove oldest cached result
            store.pop(next(iter(store)),None)
        store[key]=copy.deepcopy(value)


CHAT_SCHEMA={
  'type':'object',
  'properties':{'reply':{'type':'string'},'user_analysis':core_schema(),'reply_analysis':core_schema()},
  'required':['reply','user_analysis','reply_analysis'],
  'additionalProperties':False
}

BOT_COMMENT_SCHEMA=CHAT_SCHEMA

DEFAULT_CALIBRATION={
  'version':'1.0',
  'status':'human_calibrated',
  'human_labels':3600,
  'target_human_labels':3600,
  'unique_messages':450,
  'uncertainty_high':65,
  'model_independent':True
}

def load_calibration():
    p=ROOT/'calibration_profile.json'
    if not p.exists(): return DEFAULT_CALIBRATION.copy()
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        out=DEFAULT_CALIBRATION.copy(); out.update(data)
        runtime=data.get('runtime') or {}
        for key in ('status','human_labels','target_human_labels','unique_messages','uncertainty_high','model_independent'):
            if key in runtime: out[key]=runtime[key]
        return out
    except Exception as e:
        print('[NİYET V16] calibration_profile.json okunamadı:',e)
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

def normalized_entropy_unit(dist):
    p=normalize_dist(dist)
    h=-sum(v*math.log(v) for v in p.values() if v>0)
    return h/math.log(len(INTENTS))

def normalized_entropy(dist):
    return round(100*normalized_entropy_unit(dist),1)

def perception_uncertainty(dist):
    """Reader-perception ambiguity score in [0,100].

    V13 used normalized entropy directly. Human-calibrated distributions are naturally soft,
    so entropy alone could label a message as highly uncertain even when the leading
    perception was clearly separated. V13.6 therefore combines top-two proximity with
    residual distribution spread. High values are reserved mainly for near-ties.
    """
    p=normalize_dist(dist)
    shares=sorted((100.0*v for v in p.values()), reverse=True)
    top1=shares[0] if shares else 0.0
    top2=shares[1] if len(shares)>1 else 0.0
    gap=max(0.0, top1-top2)
    # Near-tie component: gap 0 => 100, gap >= 35 => 0.
    tie=max(0.0,min(100.0,100.0*(1.0-gap/35.0)))
    # Soft distributions have non-zero entropy by design; only the upper tail contributes.
    ent=normalized_entropy(p)
    spread=max(0.0,min(100.0,(ent-50.0)/35.0*100.0))
    # Weak-leading-perception penalty, kept deliberately small.
    weak_top=max(0.0,min(100.0,(55.0-top1)/25.0*100.0))
    return round(0.65*tie+0.25*spread+0.10*weak_top,1)

def project_simplex(values):
    """Euclidean projection onto {x>=0, sum(x)=1}."""
    v=[float(x) for x in values]
    u=sorted(v,reverse=True)
    cssv=0.0; rho=-1
    for j,val in enumerate(u):
        cssv+=val
        t=(cssv-1.0)/(j+1)
        if val-t>0: rho=j
    if rho<0:
        return [1.0/len(v)]*len(v)
    theta=(sum(u[:rho+1])-1.0)/(rho+1)
    w=[max(x-theta,0.0) for x in v]
    total=sum(w) or 1.0
    return [x/total for x in w]

def _ridge_calibrate(dist):
    """Apply the deployed V1 human-perception calibration profile learned from 3,600 labels."""
    coeff=(CALIBRATION.get('coefficients') or {})
    intercepts=coeff.get('intercepts') or []
    matrix=coeff.get('matrix_output_by_feature') or []
    outputs=coeff.get('output_categories') or INTENTS
    if len(intercepts)!=7 or len(matrix)!=7 or any(len(row)!=15 for row in matrix):
        return None
    p=normalize_dist(dist)
    probs=[p[k] for k in INTENTS]
    # Training features: seven probabilities, seven natural logs, normalized entropy (0..1).
    eps=1e-6
    features=probs+[math.log(max(x,eps)) for x in probs]+[normalized_entropy_unit(p)]
    raw=[]
    for b,row in zip(intercepts,matrix):
        raw.append(float(b)+sum(float(c)*float(x) for c,x in zip(row,features)))
    projected=project_simplex(raw)
    mapped={k:0.0 for k in INTENTS}
    for k,v in zip(outputs,projected):
        if k in mapped: mapped[k]=v*100.0
    return mapped

def calibrate_distribution(dist):
    exact=_ridge_calibrate(dist)
    if exact is None:
        p=normalize_dist(dist); exact={k:p[k]*100.0 for k in INTENTS}
    # Keep one decimal and force an exact total of 100 for UI readability.
    rounded={k:round(float(exact.get(k,0.0)),1) for k in INTENTS}
    diff=round(100.0-sum(rounded.values()),1)
    if abs(diff)>=0.05:
        top=max(rounded,key=rounded.get); rounded[top]=round(rounded[top]+diff,1)
    return rounded

def shift_type(a,selected,dominant):
    if selected==dominant: return 'Belirgin algı sapması yok'
    if selected=='Mizah' and dominant=='Eleştiri' and (a.get('has_risky_irony') or a.get('has_contempt')):
        return 'Mizah → Eleştiri algısı · alay/küçümseme sinyali'
    if selected=='Tavsiye' and dominant=='Eleştiri' and (a.get('has_dismissive_language') or a.get('has_contempt')):
        return 'Tavsiye → Eleştiri algısı · üstten/kovucu ton sinyali'
    if selected=='Soru' and dominant in ('Eleştiri','İtiraz') and (a.get('has_personal_attack') or a.get('has_contempt')):
        return f'Soru → {dominant} algısı · ima/suçlama sinyali'
    return f'{selected} → {dominant} algısı'

def calibration_meta():
    ev=CALIBRATION.get('evaluation_oof') or {}
    human=(CALIBRATION.get('runtime') or {}).get('human_agreement_reference') or {}
    clean=(CALIBRATION.get('runtime') or {}).get('clean_research') or {}
    return {
      'status':CALIBRATION.get('status','human_calibrated'),
      'version':CALIBRATION.get('version','1.0'),
      'profile_name':CALIBRATION.get('profile_name','NİYET İnsan Algısı Kalibrasyon Katmanı'),
      'human_labels':int(CALIBRATION.get('human_labels',3600) or 3600),
      'target_human_labels':int(CALIBRATION.get('target_human_labels',3600) or 3600),
      'unique_messages':int(CALIBRATION.get('unique_messages',450) or 450),
      'readers_per_message':int((CALIBRATION.get('source') or {}).get('readers_per_message',8) or 8),
      'model_independent':True,
      'algorithm':(CALIBRATION.get('training') or {}).get('algorithm','Ridge multi-output regression + simplex projection'),
      'validation':(CALIBRATION.get('training') or {}).get('validation','5-fold stratified cross-validation'),
      'author_intent_used_as_training_feature':bool((CALIBRATION.get('training') or {}).get('author_intent_used_as_training_feature',False)),
      'raw_dominant_accuracy':round(100*float((ev.get('raw_luna') or {}).get('dominant_accuracy',0.647619)),1),
      'calibrated_dominant_accuracy':round(100*float((ev.get('calibrated_niyet') or {}).get('dominant_accuracy',0.764286)),1),
      'calibrated_top2_accuracy':round(100*float((ev.get('calibrated_niyet') or {}).get('top2_accuracy',0.92381)),1),
      'human_reference':round(100*float(human.get('leave_one_reader_vs_other7_dominant',0.71)),1),
      'strict_clean_shift_rate':round(100*float(clean.get('strict_clean_dominant_shift_rate',0.2706)),1),
      'strong_shift_threshold':round(100*float((CALIBRATION.get('decision_layer') or {}).get('strong_intent_shift_probability_threshold',0.355)),1)
    }

def decision_layer(a,selected_intent=''):
    raw=a.get('intent_distribution') or {}
    calibrated=calibrate_distribution(raw)
    a['raw_intent_distribution']={k:round(v*100,1) for k,v in normalize_dist(raw).items()}
    a['intent_distribution']=calibrated
    uncertainty=perception_uncertainty(calibrated)
    dominant=max(calibrated,key=calibrated.get)
    selected=selected_intent if selected_intent in INTENTS else ''
    selected_share=float(calibrated.get(selected,0)) if selected else 0.0
    dominant_share=float(calibrated.get(dominant,0))
    mismatch=max(0,100-selected_share) if selected else uncertainty
    high_uncertainty=uncertainty>=float(CALIBRATION.get('uncertainty_high',65))
    strong_thr=100*float((CALIBRATION.get('decision_layer') or {}).get('strong_intent_shift_probability_threshold',0.355))
    different=bool(selected and dominant!=selected)
    strong=bool(different and dominant_share>=strong_thr)
    drift=bool(different and not high_uncertainty)
    if high_uncertainty: status='Yüksek algı belirsizliği — kesin hüküm verilmedi'
    elif strong: status='Belirgin niyet kayması'
    elif drift: status='Hafif algı kayması'
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
      'strong_intent_drift':strong,
      'strong_threshold':round(strong_thr,1),
      'decision_status':status,
      'shift_type':shift_type(a,selected,dominant) if selected else 'Yazar niyeti belirtilmedi'
    }
    a['calibration_meta']=calibration_meta()
    return a

def js_distance(a,b):
    """Normalized Jensen-Shannon distance in [0,1]."""
    p=normalize_dist(a); q=normalize_dist(b)
    pv=[p[k] for k in INTENTS]; qv=[q[k] for k in INTENTS]
    m=[(x+y)/2 for x,y in zip(pv,qv)]
    def kl(x,y):
        return sum(xi*math.log(xi/yi) for xi,yi in zip(x,y) if xi>0 and yi>0)
    js=0.5*kl(pv,m)+0.5*kl(qv,m)
    return math.sqrt(max(0.0,min(1.0,js/math.log(2))))


def stability_summary(original_dist, variant_dists):
    distances=[js_distance(original_dist,d) for d in variant_dists if d]
    if not distances:
        return {'available':False,'score':None,'label':'Hesaplanamadı','mean_js_distance':None,'max_js_distance':None,'variant_count':0}
    mean=sum(distances)/len(distances)
    worst=max(distances)
    # Mean captures overall stability; worst-case term prevents one highly sensitive
    # micro-change from being hidden by three stable variants. JS distance is already
    # normalized to [0,1], so the resulting score also remains interpretable.
    robust=0.70*mean+0.30*worst
    score=round(100*(1-min(1.0,robust)))
    label='Kararlı' if score>=75 else 'Orta' if score>=50 else 'Kırılgan'
    return {
      'available':True,
      'score':score,
      'label':label,
      'mean_js_distance':round(mean,4),
      'max_js_distance':round(worst,4),
      'robust_js_distance':round(robust,4),
      'variant_count':len(distances),
      'method':'Kontrollü yüzey mikro-varyasyonları + kör ikinci algı çıkarımı + insan kalibrasyonu + %70 ortalama / %30 en yüksek normalize Jensen-Shannon uzaklığı'
    }


def only_surface_change(a,b):
    def clean(x):
        return re.sub(r'[\W_]+','',str(x or '').casefold(),flags=re.UNICODE)
    return clean(a)==clean(b)


def change_cost(original,candidate):
    a=str(original or '').strip(); b=str(candidate or '').strip()
    if not a or not b or a==b: return 0
    if only_surface_change(a,b): return 5
    aw=re.findall(r"\w+|[^\w\s]",a,flags=re.UNICODE)
    bw=re.findall(r"\w+|[^\w\s]",b,flags=re.UNICODE)
    word_delta=1-difflib.SequenceMatcher(None,aw,bw).ratio()
    char_delta=1-difflib.SequenceMatcher(None,a,b).ratio()
    cost=round(100*(0.75*word_delta+0.25*char_delta))
    return max(4,min(100,cost))


def intervention_prompt(text,selected_intent):
    return [
      {'role':'developer','content':"NİYET İfade Önerisi aday üreticisisin. Kullanıcının üslubunu, ana içeriğini ve soru/eleştiri gibi temel söylem biçimini mümkün olduğunca koru; metni baştan yazma. Amaç, kullanıcının beyan ettiği iletişim niyetinin okuyucu tarafından daha açık algılanmasına yardımcı olabilecek küçük değişiklikler üretmektir. Öneri, mevcut mesajdan daha belirsiz, daha alaycı, daha suçlayıcı veya daha kolay yanlış anlaşılır hale gelmemeli. Özellikle retorik soru + emoji gibi yapılarda, yalnızca emojiyi çoğaltmak veya belirsizliği artırmak çözüm sayılmaz. Olasılık, puan veya başarı tahmini üretme; bunlar daha sonra kör bir algı çıkarımıyla ayrıca ölçülecek. Tam 5 farklı aday üret. Adaylar birbirinin kopyası olmasın ve şu aileleri kapsasın: (1) yüzeysel en küçük değişiklik, (2) emoji sadeleştirmesi, (3) vurgu sözcüğü sadeleştirmesi, (4) noktalama sadeleştirmesi, (5) daha açık ama yine kısa soru/ifade biçimi, (6) küçük ton yumuşatma, (7) anlamı ve kullanıcı üslubunu koruyan başka bir minimal seçenek. Özellikle seçilen niyet zaten baskınsa öneriler niyeti zorla değiştirmeye değil yalnızca açıklığı/kararlılığı küçük ölçüde artırmaya çalışsın."},
      {'role':'user','content':f'Yazarın beyan ettiği niyet: {selected_intent}\nOrijinal metin: {text}'}
    ]


def deterministic_micro_variants(text):
    """Create reproducible, surface-level variants for stability/intervention auditing.

    These variants do not optimize toward author intent. They only remove or reduce
    common surface cues (repeated emoji/punctuation, emphasis words) so stability is
    not dependent solely on another generative rewrite.
    """
    src=str(text or '').strip()
    if not src:
        return []
    out=[]
    def add(candidate,change):
        c=re.sub(r'\s+',' ',str(candidate or '')).strip()
        if c and c!=src and all(x['text']!=c for x in out) and change_cost(src,c)<=38:
            out.append({'text':c,'change':change})
    # Remove common emoji ranges only; preserve normal punctuation.
    no_emoji=re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]+','',src)
    add(no_emoji,'Emoji sinyalini kaldırma')
    # Collapse repeated emoji to a single occurrence.
    one_emoji=re.sub(r'([\U0001F300-\U0001FAFF\u2600-\u27BF])\1+',r'\1',src)
    add(one_emoji,'Tekrarlanan emojiyi sadeleştirme')
    # Collapse emphatic punctuation.
    punct=re.sub(r'([!?])\1+',r'\1',src)
    add(punct,'Tekrarlanan noktalama işaretini sadeleştirme')
    # Remove one common emphasis marker without changing proposition/content.
    emphasis=re.sub(r'(?i)(^|\s)(gerçekten|cidden|resmen|açıkçası|kesinlikle|zaten)(?=\s|[?!,.]|$)',r'\1',src,count=1)
    add(emphasis,'Vurgu sözcüğünü azaltma')
    return out[:4]


def safe_candidate_gate(before, before_unc, before_dom, before_gap, selected_intent, cand_dist, cost):
    """V13.6 recommendation gate.

    A recommendation must improve selected-intent evidence and must not create a new
    dominant-perception problem or a large ambiguity increase. Three tiers are used so
    small but genuinely non-worsening minimal changes remain visible.
    """
    after=float(cand_dist.get(selected_intent,0)) if selected_intent in INTENTS else 0.0
    gain=round(after-before,1)
    after_unc=perception_uncertainty(cand_dist)
    unc_change=round(after_unc-before_unc,1)
    after_dom=max(cand_dist,key=cand_dist.get)
    after_other=max([float(v) for k,v in cand_dist.items() if k!=selected_intent] or [0.0])
    after_gap=after_other-after
    gap_improvement=round(before_gap-after_gap,1)
    if before_dom==selected_intent:
        dominance_ok=(after_dom==selected_intent)
    else:
        dominance_ok=after_dom in (before_dom,selected_intent)
    no_major_uncertainty_jump=after_unc < 80.0 and unc_change <= 8.0
    gap_ok=gap_improvement >= -0.5
    strict=(gain>=4.0 and cost<=48 and unc_change<=3.0 and dominance_ok and gap_improvement>=0.0)
    high_gain=(gain>=9.0 and cost<=68 and no_major_uncertainty_jump and dominance_ok and gap_ok)
    optional_minimal=(gain>=1.5 and cost<=30 and unc_change<=1.5 and dominance_ok and gap_ok)
    accepted=bool(strict or high_gain or optional_minimal)
    tier='strict' if strict else ('high_gain' if high_gain else ('optional_minimal' if optional_minimal else 'rejected'))
    return {
      'accepted':accepted,'tier':tier,'after':after,'gain':gain,'after_unc':after_unc,
      'unc_change':unc_change,'after_dom':after_dom,'after_gap':after_gap,'gap_improvement':gap_improvement
    }


def batch_perception_prompt(items,context=''):
    rows='\n'.join([f"[{x['id']}] {x['text']}" for x in items])
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+"\nAşağıda birden fazla mesaj verilecek. Her mesajı birbirinden bağımsız değerlendir. Yazarın seçtiği niyet sana verilmemektedir ve tahmin edilmemelidir. Her id için yalnızca tipik okuyucu algısını yedi niyet kategorisinde dağıt ve en fazla bir kısa gerekçe yaz."},
      {'role':'user','content':f'Bağlam: {context or "yok"}\nMesajlar:\n{rows}'}
    ]


def evaluate_variants(items,context=''):
    """V14: evaluate small candidate batches concurrently.

    Primary analysis is already returned to the UI. These secondary blind perception
    checks run in parallel where possible so Algı Kararlılığı / İfade Önerisi
    finish without serially stacking every API round trip.
    """
    if not items:
        return {}

    def eval_chunk(chunk, pos):
        local={}
        def consume(payload):
            for item in payload.get('items') or []:
                iid=str(item.get('id',''))
                if not iid: continue
                raw=item.get('intent_distribution') or {}
                local[iid]={
                  'raw_intent_distribution':{k:round(v*100,1) for k,v in normalize_dist(raw).items()},
                  'intent_distribution':calibrate_distribution(raw),
                  'reason':str(item.get('reason',''))
                }
        try:
            budget=max(900,360*len(chunk))
            d=call_responses(batch_perception_prompt(chunk,context),budget,BATCH_SCHEMA,f'niyet_v14_variant_{pos}')
            consume(d)
            return local
        except Exception as batch_error:
            print(f'[NİYET V16] varyant batch uyarısı ({pos}): {batch_error}')
        for item in chunk:
            try:
                d=call_responses(batch_perception_prompt([item],context),620,BATCH_SCHEMA,'niyet_v14_variant_single')
                consume(d)
            except Exception as single_error:
                print(f"[NİYET V16] varyant atlandı {item.get('id','?')}: {single_error}")
        return local

    chunk_size=3
    chunks=[items[pos:pos+chunk_size] for pos in range(0,len(items),chunk_size)]
    out={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(3,len(chunks))) as ex:
        futures=[ex.submit(eval_chunk,chunk,i+1) for i,chunk in enumerate(chunks)]
        for fut in concurrent.futures.as_completed(futures):
            try: out.update(fut.result())
            except Exception as e: print('[NİYET V16] paralel varyant uyarısı:',e)
    return out


def attach_v13_analysis(original,text,selected_intent,context=''):
    stability_variants=[]
    seen={str(text).strip()}
    # V13.6: first use reproducible surface variants, then supplement with model-generated
    # micro-variants. Stability candidates are filtered by edit cost so the score reflects
    # genuinely small wording changes rather than rewrites.
    raw_stability=[]
    raw_stability.extend(deterministic_micro_variants(text))
    raw_stability.extend((original.get('stability_variants') or [])[:6])
    for item in raw_stability:
        t=str(item.get('text','')).strip()
        if not t or t in seen: continue
        cost=change_cost(text,t)
        if cost<=0 or cost>38: continue
        seen.add(t)
        stability_variants.append({'id':f's{len(stability_variants)+1}','text':t,'change':str(item.get('change','Küçük ifade değişikliği')),'change_cost':cost})
        if len(stability_variants)>=3: break

    interventions=[]
    if selected_intent in INTENTS:
        try:
            generated=call_responses(intervention_prompt(text,selected_intent),1100,INTERVENTION_SCHEMA,'niyet_v13_minimum_intervention')
        except Exception as e:
            # The main calibrated perception result is more important than optional
            # candidate generation. Deterministic micro-candidates remain available.
            print(f'[NİYET V16] İfade Önerisi aday üretimi uyarısı: {e}')
            generated={'candidates':[]}
            original.setdefault('enrichment_warnings',[]).append('Model tabanlı ek öneri üretimi bu analizde tamamlanamadı; doğrulanabilen minimal adaylarla devam edildi.')
        # Add deterministic tiny candidates before generative candidates. All candidates
        # still have to pass a blind second perception inference + human calibration.
        raw_interventions=[]
        raw_interventions.extend(deterministic_micro_variants(text))
        raw_interventions.extend((generated.get('candidates') or [])[:5])
        seen_i={str(text).strip()}
        for item in raw_interventions:
            t=str(item.get('text','')).strip()
            if not t or t in seen_i: continue
            seen_i.add(t)
            cost=change_cost(text,t)
            if cost<=0 or cost>72: continue
            interventions.append({'id':f'i{len(interventions)+1}','text':t,'change':str(item.get('change','Minimal düzenleme')),'change_cost':cost})
            if len(interventions)>=6: break

    combined=stability_variants+interventions
    evaluated=evaluate_variants(combined,context)
    original_dist=original.get('intent_distribution') or {}
    stab_dists=[]
    stab_out=[]
    for item in stability_variants:
        ev=evaluated.get(item['id'])
        if not ev: continue
        stab_dists.append(ev['intent_distribution'])
        stab_out.append({**item,**ev,'distance':round(js_distance(original_dist,ev['intent_distribution']),4)})
    original['stability']=stability_summary(original_dist,stab_dists)
    original['stability']['variants']=stab_out

    dl=original.get('decision_layer') or {}
    before=float(dl.get('selected_share') or 0)
    before_unc=float(dl.get('perception_uncertainty') or perception_uncertainty(original_dist))
    before_dom=str(dl.get('dominant_intent') or max(original_dist,key=original_dist.get))
    before_other=max([float(v) for k,v in original_dist.items() if k!=selected_intent] or [0.0])
    before_gap=before_other-before
    scored=[]
    for item in interventions:
        ev=evaluated.get(item['id'])
        if not ev: continue
        cand_dist=ev['intent_distribution']
        cost=int(item.get('change_cost') or change_cost(text,item['text']))
        gate=safe_candidate_gate(before,before_unc,before_dom,before_gap,selected_intent,cand_dist,cost)
        gain=gate['gain']; after=gate['after']; after_unc=gate['after_unc']; unc_change=gate['unc_change']; after_dom=gate['after_dom']
        stability_score=float((original.get('stability') or {}).get('score') or 100)
        uncertainty_weight=0.45 if stability_score<50 else 0.30 if stability_score<75 else 0.18
        utility=gain + uncertainty_weight*max(0.0,before_unc-after_unc) + 0.18*max(0.0,gate['gap_improvement']) - 0.65*max(0.0,unc_change)
        efficiency=round(utility/max(cost,1),3)
        scored.append({
          **item,**ev,
          'before_match':round(before,1),'after_match':round(after,1),
          'before_risk':round(100-before,1),'after_risk':round(100-after,1),
          'before_uncertainty':round(before_unc,1),'after_uncertainty':round(after_unc,1),
          'uncertainty_change':unc_change,'dominant_after':after_dom,
          'perception_gain':gain,'change_cost':cost,'efficiency':efficiency,'safe_recommendation':gate['accepted'],
          'recommendation_tier':gate['tier'],'gap_improvement':gate['gap_improvement'],
          'evaluation_mode':'Kör ikinci algı çıkarımı + insan kalibrasyonu + V14 üç kademeli öneri kapısı'
        })
    accepted_scored=[x for x in scored if x['safe_recommendation']]
    # Keep diversity: smallest edit, best efficiency and highest gain. This prevents a
    # useful minimal option from disappearing just because the message is already stable.
    by_cost=sorted(accepted_scored,key=lambda x:(x['change_cost'],-x['perception_gain']))
    by_eff=sorted(accepted_scored,key=lambda x:(x['efficiency'],x['perception_gain']),reverse=True)
    by_gain=sorted(accepted_scored,key=lambda x:(x['perception_gain'],-x['change_cost']),reverse=True)
    ranked=[]
    for seq in (by_cost,by_eff,by_gain):
        if seq and all(x['id']!=seq[0]['id'] for x in ranked): ranked.append(seq[0])
    for x in by_eff:
        if all(y['id']!=x['id'] for y in ranked): ranked.append(x)
    original['interventions']=ranked[:3]
    original['intervention_audit']={
      'generated':len(interventions),'accepted':len(accepted_scored),
      'strict':sum(1 for x in accepted_scored if x.get('recommendation_tier')=='strict'),
      'high_gain':sum(1 for x in accepted_scored if x.get('recommendation_tier')=='high_gain'),
      'optional_minimal':sum(1 for x in accepted_scored if x.get('recommendation_tier')=='optional_minimal'),
      'rejected':len(scored)-len(accepted_scored)
    }
    original['v13_method']={
      'raw_perception_blind_to_author_intent':True,
      'stability_second_inference':True,
      'stability_reproducible_surface_variants':True,
      'intervention_second_inference':True,
      'selected_intent_used_only_downstream':True
    }
    original.pop('stability_variants',None)
    return original


def persona_instruction(pid):
    name,style,bio=PERSONAS[pid]
    if pid=='tolga':
        return f'''Sen {name} adlı NİYET VFINAL2 prototipindeki SENTETİK SERT KONUŞMA TARZI TEST BOTUSUN. Amaç, gerilim ve dijital güvenlik katmanını kontrollü biçimde sınamaktır.
Üslubun kısa, keskin, sabırsız ve meydan okuyan olabilir. "Bu argüman zayıf", "Net bir gerekçe sun", "Aynı noktayı tekrar ediyorsun", "Somut cevap ver" gibi sert ama fikir odaklı ifadeler kullan. Küfür, kişisel hakaret, aşağılayıcı lakap, nefret söylemi, korunan gruplara yönelik saldırı, cinsel taciz, şantaj, doxxing, fiziksel zarar tehdidi veya kendine zarar içeriği üretme. Kullanıcı açık sınır koyarsa en fazla bir tur kontrollü ısrar simüle et, sonra dur. Markdown kullanma.'''
    if pid=='berk':
        return f'''Sen {name} adlı NİYET VFINAL2 prototipindeki SENTETİK SERT KONUŞMA TARZI TEST BOTUSUN. Amaç, tekrarlı baskın iletişim ve sınır ihlali sinyallerini güvenli bir demoda görünür kılmaktır.
Kısa, ısrarcı, sert ve sorgulayıcı yazabilirsin. Kişiye saldırmak yerine düşünceyi zorla: "Bu cevap yeterli değil", "Konuyu kapatmadan önce netleştir", "Gerekçeni açıkça yaz" gibi ifadeler kullan. Küfür, kişisel hakaret, aşağılayıcı lakap, nefret söylemi, korunan gruplara yönelik saldırı, cinsel içerik/taciz, şantaj, doxxing, fiziksel zarar tehdidi veya kendine zarar içeriği üretme. Sınır ihlalini yalnızca düşük şiddetli ve kontrollü bir test örüntüsü olarak simüle et. Markdown kullanma.'''
    return f'''Sen {name} adlı NİYET prototipindeki sentetik sosyal medya kullanıcısısın. Üslubun: {style}. Profilin: {bio}
Türkçe, doğal ve kısa yaz; çoğu cevap 1-3 cümle. Bağlama sadık kal. Karakteri abartma. Hakaret üretme. NİYET sosyal sinyalleri yüksek belirsizlik gösteriyorsa karşı tarafın niyetini kesin varsayma; gerekirse kısa bir açıklama sorusu sor. Gerilim sinyali yüksekse karakterini koruyarak gerilimi büyütme. Markdown kullanma.'''

SAFETY_TEST_BOTS={'tolga','berk'}


def simple_local_analysis(text):
    t=str(text or '').lower()
    insult_terms=('aptal','salak','gerizekalı','beceriksiz')
    dismissive_terms=('boş yapma','uzatma','sus','defol','çek git','bunu da mı anlamadın','cevap versene','cevap vereceksin')
    contempt_terms=('komik duruyor','gereksiz','mantıklı değil','yine aynı','bu kadar basit')
    has_insult=any(x in t for x in insult_terms)
    has_dismissive=any(x in t for x in dismissive_terms)
    has_contempt=has_dismissive or any(x in t for x in contempt_terms)
    has_personal=has_insult or ('sen ' in t and (has_dismissive or has_contempt))
    escalates=has_dismissive or has_insult or 'yine yazarım' in t or 'sınır koyman' in t
    polite=any(x in t for x in ('teşekkür','sağ ol','lütfen','merhaba','selam'))
    calming=any(x in t for x in ('sakin','konuya dönelim','anlıyorum','özür'))
    clear=len(t.strip())>2
    dist={k:2 for k in INTENTS}
    if '?' in t:
        dist['Soru']=55
    elif has_dismissive or has_contempt:
        dist['Eleştiri']=55; dist['İtiraz']=25
    else:
        dist['Bilgilendirme']=45; dist['Soru']=20
    a={
      'intent_distribution':dist,
      'has_insult':has_insult,
      'has_personal_attack':has_personal,
      'has_dismissive_language':has_dismissive,
      'has_contempt':has_contempt,
      'is_unconstructive':has_dismissive or has_contempt,
      'has_unexplained_contradiction':False,
      'escalates_tension':escalates,
      'is_ambiguous':False,
      'has_risky_irony':False,
      'is_calming':calming,
      'is_polite':polite,
      'apologizes':'özür' in t,
      'acknowledges_other':'anlıyorum' in t or 'haklısın' in t,
      'returns_to_topic':'konuya dönelim' in t,
      'has_reasoning':'çünkü' in t,
      'offers_alternative':'yerine' in t,
      'asks_constructive_question':'?' in t and not has_dismissive,
      'is_clear':clear,
      'is_respectful':not (has_insult or has_dismissive or has_contempt),
      'explains_change':False,
      'has_boundary_violation':('yazma demen' in t or 'sınır koyman' in t or 'cevap vereceksin' in t),
      'has_repeated_unwanted_contact':('yine yazarım' in t or 'cevap versene' in t),
      'has_threat_or_intimidation':False,
      'has_sexual_harassment_signal':False,
      'reason':'Kontrollü V14 güvenlik testi için yerel davranış analizi.'
    }
    return decision_layer(a,'')


def test_bot_combined(pid,history,opening=False):
    history=history or []
    bot_turns=sum(1 for m in history if m.get('from')!='me' and str(m.get('text','')).strip() not in ('','…'))
    if pid=='tolga':
        sequence=[
          'Selam. Akışta yazdıklarını gördüm; iddian net ama gerekçen bana zayıf geliyor.',
          'Aynı noktayı tekrar ediyorsun. Somut bir gerekçe sunarsan tartışma ilerler.',
          'Konuyu dağıtma; söylediğin iddiaya doğrudan cevap ver.',
          'Hâlâ ikna olmadım. Net bir dayanak göstermeden bu görüş güçlü görünmüyor.'
        ]
    else:
        sequence=[
          'Buradaki iddianı gördüm; bu haliyle yeterince temellendirilmiş değil.',
          'Cevap vermek istemiyorsan bunu açık söyle; belirsiz bırakmak tartışmayı uzatıyor.',
          'Konuyu kapatmadan önce gerekçeni netleştirmeni istiyorum. Sınır koyarsan burada duracağım.',
          'Tamam, burada duruyorum. Bu test konuşması yeterince gerilim sinyali üretti.'
        ]
    reply=sequence[min(bot_turns,len(sequence)-1)]
    last_user=''
    for m in reversed(history):
        if m.get('from')=='me':
            last_user=str(m.get('text','')).strip(); break
    return {'reply':reply,'user_analysis':simple_local_analysis(last_user),'reply_analysis':simple_local_analysis(reply)}

ANALYSIS_RUBRIC='''NİYET iletişim analiz motorusun. Metni kişi hakkında ahlaki hüküm vermeden yalnızca iletişim davranışı açısından sınıflandır.
Yazarın seçtiği niyet, yazarın kendi beyanıdır ve kör algı tahmininde sana gösterilmez. intent_distribution yalnızca bağımsız bir sosyal medya okuyucusunun mesajı nasıl algılayabileceğini temsil etsin; yazarın gerçek niyetini tahmin etmeye çalışma.
Boole alanlarını yalnızca metinde veya verilen bağlamda açık kanıt varsa true yap. Sıradan kısa sohbeti yapıcı değil diye cezalandırma. Eleştiri tek başına saldırı değildir. Görüş değişikliği gerekçeliyse çelişki sayma. Nezaket, özür, karşı tarafı anlama, konuya dönüş, gerekçe, alternatif, yapıcı soru ve açıklık sinyallerini ayrı sınıflandır.
Dijital güvenlik alanlarında özellikle muhafazakâr ol: has_boundary_violation yalnızca karşı tarafın açık bir sınırının konuşma bağlamında ihlal edildiği durumlarda; has_repeated_unwanted_contact açıkça istenmeyen temasın tekrarında; has_threat_or_intimidation açık tehdit/korkutma sinyalinde; has_sexual_harassment_signal istenmeyen cinselleştirilmiş yaklaşımda true olsun. Tek bir belirsiz cümleden bu sonuçları çıkarma.
intent_distribution değerleri 0-100 arası göreli kanıttır; toplamın 100 olması şart değildir. reason en fazla 2 kısa Türkçe cümle olsun.'''

def analysis_prompt(text,context='',selected_intent=''):
    # Critical research rule: selected_intent is intentionally NOT shown to the raw perception pass.
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+"\nAyrıca algı kararlılığı testi için tam 4 kontrollü mikro-varyasyon üret. Bu varyasyonlar kullanıcı niyetini optimize etmeye çalışmamalı; yalnızca anlamı mümkün olduğunca koruyan küçük yüzey/dil değişiklikleri olmalı (ör. emoji kaldırma, vurgu sözcüğünü azaltma, noktalama sadeleştirme, küçük ton yumuşatma). Varyasyonlar için olasılık üretme; algıları daha sonra ayrı ve kör bir ikinci çıkarımda ölçülecek."},
      {'role':'user','content':f'Bağlam: {context or "yok"}\nAnaliz edilecek sosyal medya metni: {text}'}
    ]


def analyze(text,context='',selected_intent=''):
    # Backward-compatible full endpoint. V14 UI uses analyze_fast + enrich_analysis separately.
    primary=analyze_fast(text,context,selected_intent)
    return enrich_analysis(primary,text,selected_intent,context)


def fast_analysis_prompt(text,context=''):
    # Fast pass: only the essential blind perception + behavior features.
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+"\nBu hızlı geçişte yalnızca istenen temel analiz alanlarını üret. Varyasyon, yeniden yazım veya öneri üretme."},
      {'role':'user','content':f'Bağlam: {context or "yok"}\nAnaliz edilecek sosyal medya metni: {text}'}
    ]


def intent_signal_scope(text):
    """Yarışma sürümü: 7 niyet sınıfına zorlanmaması gereken gündelik sosyal ifadeleri ayır.

    Bu bir yeni niyet sınıfı veya kalibrasyon katsayısı değildir. Amaç, eğitim verisinde
    'Selamlaşma/Diğer' sınıfı bulunmadığı için kısa sosyal temas mesajlarının yapay biçimde
    mevcut 7 sınıftan birine zorlanmasını engellemektir.
    """
    raw=str(text or '').strip()
    folded=re.sub(r'\s+',' ',raw.casefold()).strip()
    # Noktalama/emoji son eklerini temizle; kelime içeriğini koru.
    cleaned=re.sub(r'[\s.!…,:;🙂😊👋🙏]+$','',folded).strip()

    greeting_patterns=(
        r'^selam(?:lar)?(?:\s+(?:herkese|arkadaşlar|millet|dostlar))?$',
        r'^merhaba(?:\s+(?:herkese|arkadaşlar|millet|dostlar))?$',
        r'^günaydın(?:\s+(?:herkese|arkadaşlar))?$',
        r'^iyi\s+(?:günler|akşamlar|geceler)(?:\s+(?:herkese|arkadaşlar))?$',
        r'^hey(?:\s+(?:herkese|arkadaşlar|millet))?$',
        r'^naber$',
        r'^ne\s+haber$',
        r'^nasılsın(?:ız)?$',
        r'^iyi\s+misin(?:iz)?$',
        r'^napıyorsun(?:uz)?$',
        r'^ne\s+yapıyorsun(?:uz)?$',
        r'^(?:selam(?:lar)?|merhaba|hey|günaydın|iyi\s+(?:günler|akşamlar|geceler))(?:\s+(?:herkese|arkadaşlar|millet|dostlar))?\s+(?:naber|ne\s+haber|nasılsın(?:ız)?|iyi\s+misin(?:iz)?|napıyorsun(?:uz)?|ne\s+yapıyorsun(?:uz)?)$'
    )
    greeting_only=any(re.fullmatch(p,cleaned,flags=re.IGNORECASE) for p in greeting_patterns)

    # Tamamen anlamsız/çok eksik girişler de puanlanmaz; ancak "Harika", "Yanlış",
    # "Katılmıyorum" gibi tek kelimelik ama niyet taşıyabilen ifadeler bu kapsama girmez.
    no_letters=not bool(re.search(r'[a-zçğıöşü]',folded,flags=re.IGNORECASE))
    empty_like=len(cleaned)<2 or no_letters

    if greeting_only:
        return {
            'scoreable':False,
            'reason':'daily_social_language',
            'category':'daily_language',
            'label':'Günlük dil tespit edildi',
            'explanation':'Bu ifade selamlaşma veya gündelik sosyal temas niteliğinde. NİYET bu tür kısa mesajları 7 ana paylaşım niyetinden birine zorlamak yerine günlük iletişim olarak işaretler.'
        }
    if empty_like:
        return {
            'scoreable':False,
            'reason':'insufficient_text',
            'label':'Niyet analizi için yetersiz içerik',
            'explanation':'Mesaj, güvenilir bir Niyet–Algı karşılaştırması yapmak için yeterli dilsel içerik taşımıyor.'
        }
    return {'scoreable':True,'reason':'in_scope','label':'Analiz edilebilir','explanation':''}


def analyze_fast(text,context='',selected_intent=''):
    scope=intent_signal_scope(text)
    key=_cache_key('fast',MODEL,text,context,selected_intent,CALIBRATION.get('version'),'scope-v15.1')
    cached=_cache_get(_FAST_CACHE,key)
    if cached is not None:
        cached['cache_hit']=True
        return cached

    # Çok kısa selamlaşmayı 7 sınıfa zorlamıyoruz. Böylece örn. "selam" +
    # "Bilgilendirme" seçiminde anlamsız %2 uyum / %98 risk üretilmez.
    if not scope.get('scoreable',True):
        selected=selected_intent if selected_intent in INTENTS else ''
        neutral={k:0.0 for k in INTENTS}
        a={
          'intent_distribution':neutral,
          'has_insult':False,'has_personal_attack':False,'has_dismissive_language':False,'has_contempt':False,
          'is_unconstructive':False,'has_unexplained_contradiction':False,'escalates_tension':False,'is_ambiguous':False,'has_risky_irony':False,
          'is_calming':False,'is_polite':True,'apologizes':False,'acknowledges_other':False,'returns_to_topic':False,
          'has_reasoning':False,'offers_alternative':False,'asks_constructive_question':False,'is_clear':True,'is_respectful':True,'explains_change':False,
          'has_boundary_violation':False,'has_repeated_unwanted_contact':False,'has_threat_or_intimidation':False,'has_sexual_harassment_signal':False,
          'reason':scope.get('explanation',''),
          'analysis_scope':scope,
          'decision_layer':{
            'selected_intent':selected,
            'dominant_intent':'',
            'dominant_share':None,
            'selected_share':None,
            'intent_match':None,
            'misunderstanding_risk':None,
            'perception_uncertainty':None,
            'high_uncertainty':False,
            'intent_drift':False,
            'strong_intent_drift':False,
            'strong_threshold':round(100*float((CALIBRATION.get('decision_layer') or {}).get('strong_intent_shift_probability_threshold',0.355)),1),
            'decision_status':scope.get('label','Günlük dil tespit edildi'),
            'shift_type':'Ölçülmedi'
          },
          'calibration_meta':calibration_meta(),
          'api_primary_analysis':False,
          'stability':{'available':False,'score':None,'label':'Gerekli değil','variant_count':0},
          'interventions':[],
          'enrichment_pending':False
        }
        _cache_put(_FAST_CACHE,key,a)
        return a

    a=call_responses(fast_analysis_prompt(text,context),900,core_schema(),'niyet_v15_fast_analysis')
    a=decision_layer(a,selected_intent)
    a['analysis_scope']=scope
    a.pop('raw_intent_distribution',None)
    a['api_primary_analysis']=True
    a['stability']={'available':False,'score':None,'label':'Hazırlanıyor','variant_count':0}
    a['interventions']=[]
    a['enrichment_pending']=True
    _cache_put(_FAST_CACHE,key,a)
    return a


def enrich_analysis(original,text,selected_intent,context=''):
    key=_cache_key('enrich',MODEL,text,context,selected_intent,CALIBRATION.get('version'))
    cached=_cache_get(_ENRICH_CACHE,key)
    if cached is not None:
        cached['cache_hit']=True
        return cached
    base=copy.deepcopy(original or {})
    if (base.get('analysis_scope') or {}).get('scoreable') is False:
        base['enrichment_pending']=False
        base['stability']={'available':False,'score':None,'label':'Gerekli değil','variant_count':0}
        base['interventions']=[]
        return base
    if not base.get('intent_distribution') or not base.get('decision_layer'):
        base=analyze_fast(text,context,selected_intent)
    base.pop('enrichment_pending',None)
    try:
        out=attach_v13_analysis(base,text,selected_intent,context)
    except Exception as e:
        print(f'[NİYET V16] zenginleştirme uyarısı: {e}')
        base['stability']={'available':False,'score':None,'label':'Bu analizde hesaplanamadı','variant_count':0}
        base['interventions']=[]
        base.setdefault('enrichment_warnings',[]).append('Algı Kararlılığı/İfade Önerisi ek hesaplarından biri tamamlanamadı; ana insan-kalibre algı sonucu korunmuştur.')
        out=base
    out.pop('raw_intent_distribution',None)
    out.pop('stability_variants',None)
    out['enrichment_pending']=False
    _cache_put(_ENRICH_CACHE,key,out)
    return out

def context_shadow_prompt(text,context=''):
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+"\nGÖREV: Aynı mesaj için iki ayrı tipik okuyucu algısı üret. standalone_distribution yalnızca mesajın kendisini görür. contextual_distribution ise verilen konuşma bağlamını da dikkate alır. Yazarın gerçek niyetini tahmin etme. İki dağılım da yedi NİYET kategorisini kapsasın. Ayrıca context_relevance ile mesajın mevcut konuşma/paylaşım konusuyla anlamsal ilişkisini 0-100 arasında değerlendir ve context_dependency ile mesajın anlamının bağlama gerçekten ihtiyaç duyup duymadığını belirt. ÖNEMLİ: Konu dışı, rastgele veya önceki konuşmayla zayıf ilişkili bir mesajı sırf bağlam verildi diye yeniden yorumlama. Konu uyuşmazlığı tek başına Bağlam Etkisi değildir. 'Aynen', 'o yüzden', 'katılıyorum', 'sen de öyle demiştin' gibi bağlama bağımlı yanıtlar ise bağlamdan güçlü biçimde etkilenebilir. Gerekçeler birer kısa cümle olsun."},
      {'role':'user','content':f'Konuşma bağlamı:\n{context or "- bağlam yok"}\n\nAynı değerlendirilecek mesaj:\n{text}'}
    ]

def context_shadow(text,context=''):
    text=str(text or '').strip(); context=str(context or '').strip()
    if not text:
        return {'available':False}
    key=_cache_key('shadow',MODEL,text,context,CALIBRATION.get('version'))
    cached=_cache_get(_SHADOW_CACHE,key)
    if cached is not None:
        cached['cache_hit']=True
        return cached
    last_error=None
    for attempt in range(3):
        try:
            d=call_responses(context_shadow_prompt(text,context),560,CONTEXT_SHADOW_SCHEMA,'niyet_v14_context_shadow')
            break
        except Exception as e:
            last_error=e
            msg=str(e)
            transient=('429' in msg or '408' in msg or '500' in msg or '502' in msg or '503' in msg or '504' in msg or 'timed out' in msg.lower())
            if not transient or attempt==2:
                raise
            time.sleep(1.0 if attempt==0 else 2.5)
    else:
        raise last_error or RuntimeError('Bağlam analizi tamamlanamadı.')
    standalone=calibrate_distribution(d.get('standalone_distribution') or {})
    contextual=calibrate_distribution(d.get('contextual_distribution') or {})
    distance=js_distance(standalone,contextual)
    sdom=max(standalone,key=standalone.get); cdom=max(contextual,key=contextual.get)
    relevance=max(0,min(100,int(d.get('context_relevance',50) or 0)))
    dependency=bool(d.get('context_dependency',False))
    # V14.2: Gölge Niyet, konu dışılığı bağlam kaynaklı anlam değişimi sanmamalı.
    # Bağlamla anlamsal ilişki zayıfsa dağılım farkı oluşsa bile kullanıcıya Orta/Yüksek uyarı verilmez.
    if relevance<35:
        level='Düşük'
    elif distance>=0.28 or (sdom!=cdom and distance>=0.18 and dependency):
        level='Yüksek'
    elif distance>=0.12 or (sdom!=cdom and dependency):
        level='Orta'
    else:
        level='Düşük'
    # Orta düzey konu ilişkisi, güçlü bağlam bağımlılığı yoksa en fazla Orta olabilir.
    if relevance<55 and not dependency and level=='Yüksek': level='Orta'
    unc=perception_uncertainty(contextual)
    ranked=sorted(contextual.items(),key=lambda kv:kv[1],reverse=True)
    warning=None
    if relevance>=35 and unc>=65 and len(ranked)>=2:
        warning=f'Bu ifade {ranked[0][0]} ile {ranked[1][0]} arasında farklı algılanabilir.'
    effect_text=None
    if level in ('Orta','Yüksek'):
        if sdom!=cdom and dependency:
            effect_text=f'Tek başına {sdom}, mevcut bağlamda daha çok {cdom} olarak algılanabilir.'
        else:
            effect_text='Mevcut konuşma bağlamı algı dağılımını belirgin biçimde değiştiriyor.'
    out={
      'available':True,'level':level,'distance':round(distance,4),
      'context_relevance':relevance,'context_dependency':dependency,
      'standalone_dominant':sdom,'contextual_dominant':cdom,
      'dominant_changed':sdom!=cdom,'contextual_uncertainty':unc,
      'uncertainty_warning':warning,'effect_text':effect_text,
      'standalone_reason':str(d.get('standalone_reason','')),'contextual_reason':str(d.get('contextual_reason',''))
    }
    _cache_put(_SHADOW_CACHE,key,out)
    return out

def local_chat_fallback(pid,last_user='',opening=False):
    name,style,_=PERSONAS[pid]
    if opening or not str(last_user).strip():
        return f"Selam, ben {name}. Bugün nasıl gidiyor?"
    t=str(last_user).lower()
    if '?' in str(last_user):
        return "Bence bunun tek bir cevabı yok. Hangi kısmını özellikle merak ediyorsun?"
    if any(x in t for x in ('teşekkür','sağ ol','eyvallah')):
        return "Rica ederim. İstersen buradan devam edebiliriz."
    if any(x in t for x in ('katılmıyorum','yanlış','mantıksız')):
        return "Farklı düşünüyor olabiliriz. Hangi noktaya katılmadığını biraz açar mısın?"
    return "Anladım. Biraz daha açarsan düşünceni daha iyi takip edebilirim."


def chat_combined(pid,history):
    # V13.6: sohbet cevabını ağır iki-analizli JSON şemasından ayır.
    # Model doğal cevabı üretir; Sohbet Sağlığı için gerekli yapılandırılmış
    # sinyaller yerel davranış katmanında çıkarılır. Böylece chat endpointi
    # analiz endpointinden bağımsız ve düşük gecikmeli kalır.
    hist=(history or [])[-12:]
    lines=[]
    for m in hist:
        txt=str(m.get('text','')).strip()
        if txt and txt!='…':
            lines.append(('Kullanıcı' if m.get('from')=='me' else PERSONAS[pid][0])+': '+txt)
    last_user=''
    for m in reversed(hist):
        if m.get('from')=='me':
            last_user=str(m.get('text','')).strip(); break
    opening=(not lines) or last_user.startswith('Konuşmayı sen başlat:')
    conversation='\n'.join(lines) or '- yeni sohbet'
    prompt=(
        'Konuşma geçmişi:\n'+conversation+
        '\n\nSon kullanıcı mesajı: '+(last_user or '-')+
        f'\n\nYalnızca {PERSONAS[pid][0]} karakterinin göndereceği doğal Türkçe mesajı yaz. '
        'JSON, başlık, açıklama veya analiz yazma. 1-3 kısa cümle yeterli.'
    )
    try:
        reply=call_responses([
          {'role':'developer','content':persona_instruction(pid)},
          {'role':'user','content':prompt}
        ],360,None,'niyet_chat_reply')
        reply=str(reply or '').strip()
        if not reply:
            raise RuntimeError('Sohbet modeli boş yanıt üretti.')
        if len(reply)>=2 and reply[0]==reply[-1] and reply[0] in ('"',"'"):
            reply=reply[1:-1].strip()
        mode='api_reply_local_signals'
    except Exception as e:
        print(f'[NİYET V16] sohbet yedek yanıtı ({pid}): {e}')
        reply=local_chat_fallback(pid,last_user,opening)
        mode='local_fallback'
    return {
      'reply':reply,
      'user_analysis':simple_local_analysis(last_user),
      'reply_analysis':simple_local_analysis(reply),
      'chat_mode':mode
    }

def bot_comment_combined(pid,post_text,user_comment='',comments=None):
    comments=comments or []
    context='\n'.join([f"- {c.get('text','')}" for c in comments[-5:]])
    prompt=f'''Ana paylaşım: {post_text}\nSon yorumlar:\n{context or '- yok'}\nKullanıcının son yorumu: {user_comment or '- yok; ilk yorum üret'}\n\nTek JSON çıktıda: (1) karaktere uygun kısa reply üret, (2) kullanıcı yorumu varsa user_analysis olarak analiz et; yoksa nötr bir analiz üret, (3) kendi reply mesajını reply_analysis olarak analiz et. Yüksek algı belirsizliğinde kullanıcının niyetini kesin varsayma; yüksek gerilimde yanıtı büyütme.'''
    d=call_responses([{'role':'developer','content':persona_instruction(pid)+'\n\n'+ANALYSIS_RUBRIC},{'role':'user','content':prompt}],850,BOT_COMMENT_SCHEMA,'niyet_comment_turn')
    d['user_analysis']=decision_layer(d['user_analysis'],'')
    d['reply_analysis']=decision_layer(d['reply_analysis'],'')
    return d

def api_error_detail(exc):
    """Return a user-readable OpenAI/API connectivity error without exposing the key."""
    if isinstance(exc, urllib.error.HTTPError):
        body=exc.read().decode('utf-8','replace')
        try:
            detail=json.loads(body).get('error',{}).get('message',body)
        except Exception:
            detail=body
        hints={
            401:'API anahtarı geçersiz veya yetkilendirme başarısız.',
            403:'API anahtarının bu işlem/model için izni olmayabilir veya hesap/bölge erişimi kısıtlı olabilir.',
            404:'Seçilen model bu API hesabında bulunamadı veya erişilemiyor.',
            429:'API kullanım limiti, kota veya faturalandırma sınırı nedeniyle istek reddedildi.',
        }
        hint=hints.get(exc.code,'OpenAI API isteği reddedildi.')
        return f'{hint} ({exc.code}) {detail}'
    if isinstance(exc, urllib.error.URLError):
        reason=getattr(exc,'reason',exc)
        return f'OpenAI sunucusuna ağ bağlantısı kurulamadı: {reason}'
    return str(exc)

def validate_connection(key, model):
    """Validate the exact endpoint/model NİYET uses.

    Older builds tested /v1/models. Restricted project keys can legitimately deny that
    endpoint even when /v1/responses is usable. V13.6 therefore performs a tiny
    Responses API request against the selected model instead.
    """
    payload={
        'model':model,
        'reasoning':{'effort':'none'},
        'input':[{'role':'user','content':'Yanıt olarak yalnızca OK yaz.'}],
        'max_output_tokens':16,
        'store':False,
    }
    req=urllib.request.Request(
        'https://api.openai.com/v1/responses',
        data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),
        headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            data=json.loads(r.read().decode('utf-8'))
            if r.status>=300:
                raise RuntimeError(f'OpenAI bağlantı testi başarısız: HTTP {r.status}')
            # A successful Responses API object is enough to validate auth/model access.
            if not isinstance(data,dict) or not data.get('id'):
                raise RuntimeError('OpenAI bağlantısı kuruldu ancak beklenen Responses API yanıtı alınamadı.')
            return True
    except Exception as e:
        raise RuntimeError(api_error_detail(e)) from None

def _client_ip(handler):
    forwarded=str(handler.headers.get('X-Forwarded-For','')).split(',')[0].strip()
    return forwarded or (handler.client_address[0] if handler.client_address else 'unknown')

def _rate_allowed(handler):
    now=time.time()
    ip=_client_ip(handler)
    with _RATE_LOCK:
        bucket=[t for t in _RATE_BUCKETS.get(ip,[]) if now-t<60]
        if len(bucket)>=RATE_LIMIT_PER_MIN:
            _RATE_BUCKETS[ip]=bucket
            return False
        bucket.append(now)
        _RATE_BUCKETS[ip]=bucket
        # Küçük bellek temizliği
        if len(_RATE_BUCKETS)>2000:
            cutoff=now-120
            for k in list(_RATE_BUCKETS)[:500]:
                if not any(t>=cutoff for t in _RATE_BUCKETS.get(k,[])):
                    _RATE_BUCKETS.pop(k,None)
        return True

class Handler(SimpleHTTPRequestHandler):
    server_version='NIYETWeb/VFINAL2'

    def end_headers(self):
        path=self.path.split('?',1)[0]
        if path.startswith('/videos/'):
            self.send_header('Cache-Control','public, max-age=86400')
        else:
            self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma','no-cache')
            self.send_header('Expires','0')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=()')
        super().end_headers()

    def __init__(self,*a,**kw):
        self._byte_range=None
        super().__init__(*a,directory=str(ROOT),**kw)

    @staticmethod
    def _parse_byte_range(value,size):
        """Tek bir HTTP Range isteğini (bytes=start-end) güvenli biçimde çöz."""
        if not value or not str(value).startswith('bytes=') or size<=0:
            return None
        spec=str(value)[6:].strip()
        # Çoklu range bu küçük prototip sunucusunda desteklenmiyor.
        if not spec or ',' in spec or '-' not in spec:
            return 'invalid'
        left,right=spec.split('-',1)
        try:
            if left=='':
                # bytes=-500 => son 500 byte
                suffix=int(right)
                if suffix<=0:
                    return 'invalid'
                suffix=min(suffix,size)
                return (size-suffix,size-1)
            start=int(left)
            if start<0 or start>=size:
                return 'invalid'
            if right=='':
                end=size-1
            else:
                end=int(right)
                if end<start:
                    return 'invalid'
                end=min(end,size-1)
            return (start,end)
        except (TypeError,ValueError):
            return 'invalid'

    def send_head(self):
        """MP4 dosyalarında HTTP byte-range desteği sağlar.

        Tarayıcı video oynatıcıları özellikle uzak sunucularda MP4 için 206 Partial
        Content / Accept-Ranges davranışına ihtiyaç duyabilir.
        """
        path_only=self.path.split('?',1)[0]
        if not path_only.startswith('/videos/'):
            self._byte_range=None
            return super().send_head()

        path=self.translate_path(path_only)
        videos_root=(ROOT/'videos').resolve()
        try:
            resolved=Path(path).resolve()
            if videos_root not in resolved.parents or not resolved.is_file():
                self.send_error(404)
                return None
        except Exception:
            self.send_error(404)
            return None

        try:
            f=open(resolved,'rb')
        except OSError:
            self.send_error(404)
            return None

        try:
            size=os.fstat(f.fileno()).st_size
            ctype=self.guess_type(str(resolved))
            parsed=self._parse_byte_range(self.headers.get('Range'),size)

            if parsed=='invalid':
                self._byte_range=None
                self.send_response(416)
                self.send_header('Content-Range',f'bytes */{size}')
                self.send_header('Accept-Ranges','bytes')
                self.send_header('Content-Length','0')
                self.end_headers()
                f.close()
                return None

            if parsed:
                start,end=parsed
                self._byte_range=(start,end)
                f.seek(start)
                self.send_response(206)
                self.send_header('Content-Type',ctype)
                self.send_header('Accept-Ranges','bytes')
                self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length',str(end-start+1))
                self.send_header('Last-Modified',self.date_time_string(os.fstat(f.fileno()).st_mtime))
                self.end_headers()
                return f

            self._byte_range=None
            self.send_response(200)
            self.send_header('Content-Type',ctype)
            self.send_header('Accept-Ranges','bytes')
            self.send_header('Content-Length',str(size))
            self.send_header('Last-Modified',self.date_time_string(os.fstat(f.fileno()).st_mtime))
            self.end_headers()
            return f
        except Exception:
            f.close()
            raise

    def copyfile(self,source,outputfile):
        if self._byte_range:
            start,end=self._byte_range
            remaining=end-start+1
            while remaining>0:
                chunk=source.read(min(64*1024,remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining-=len(chunk)
            return
        return super().copyfile(source,outputfile)

    def do_HEAD(self):
        path=self.path.split('?',1)[0]
        if path=='/' or path=='/index.html' or path.startswith('/videos/') or path in ('/robots.txt','/sitemap.xml'):
            f=self.send_head()
            if f:
                f.close()
            return
        if path in ('/healthz','/api/status'):
            # Basit HEAD yanıtı; API gövdesine gerek yok.
            self.send_response(200)
            self.send_header('Content-Length','0')
            self.end_headers()
            return
        return self.send_error(404)

    def log_message(self,fmt,*a):
        sys.stdout.write('[NİYET VFINAL2 WEB] '+fmt%a+'\n')

    def send_json(self,o,status=200):
        b=json.dumps(o,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path=self.path.split('?',1)[0]
        if path=='/healthz':
            return self.send_json({'ok':True,'version':'VFINAL2','ai_configured':bool(API_KEY)})
        if path=='/api/status':
            return self.send_json({
                'configured':bool(API_KEY),
                'model':MODEL if API_KEY else '',
                'version':'VFINAL2',
                'web_mode':True,
                'calibration':calibration_meta()
            })
        if path=='/robots.txt':
            body=(
                'User-agent: *\n'
                'Allow: /\n'
                'Disallow: /api/\n'
                'Sitemap: https://niyetaiapp.com/sitemap.xml\n'
            ).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/plain; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            if self.command!='HEAD': self.wfile.write(body)
            return
        if path=='/sitemap.xml':
            body='''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://niyetaiapp.com/</loc>
    <lastmod>2026-08-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/xml; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers()
            if self.command!='HEAD': self.wfile.write(body)
            return
        if path=='/':
            self.path='/index.html'
            return super().do_GET()
        # Public web sunucusunda backend kaynak/katsayı dosyalarını doğrudan servis etme.
        if path=='/index.html' or path.startswith('/videos/'):
            if '..' in path:
                return self.send_error(404)
            return super().do_GET()
        return self.send_error(404)

    def do_POST(self):
        global CALIBRATION
        try:
            if not _rate_allowed(self):
                return self.send_json({'error':'Çok fazla istek gönderildi. Lütfen kısa süre sonra tekrar dene.'},429)

            n=int(self.headers.get('Content-Length','0') or 0)
            if n<=0 or n>6*1024*1024:
                return self.send_json({'error':'Geçersiz istek boyutu.'},413)
            d=json.loads(self.rfile.read(n).decode('utf-8'))

            # Web sürümünde ziyaretçiler API anahtarını değiştiremez.
            if self.path=='/api/config':
                return self.send_json({
                    'error':'Web sürümünde API anahtarı sunucu ortam değişkeni olarak yönetilir.'
                },403)

            if self.path=='/api/reload_calibration':
                return self.send_json({'error':'Public web sürümünde bu işlem kapalıdır.'},403)

            allowed_api_paths={'/api/chat','/api/analyze_fast','/api/analyze_enrich','/api/context_shadow','/api/analyze','/api/bot_comment'}
            if self.path not in allowed_api_paths:
                return self.send_json({'error':'Not found'},404)

            # Güvenlik-test botları API anahtarı olmadan çalışabilir.
            if self.path=='/api/chat':
                pid=str(d.get('person_id',''))
                hist=d.get('history') or []
                opening=bool(d.get('opening',False))
                if pid in SAFETY_TEST_BOTS:
                    out=test_bot_combined(pid,hist,opening)
                    return self.send_json({
                        'reply':out['reply'],
                        'analysis':out['user_analysis'],
                        'reply_analysis':out['reply_analysis'],
                        'model':'NİYET güvenlik-test motoru',
                        'version':'VFINAL2',
                        'test_bot':True
                    })

            if not API_KEY:
                return self.send_json({
                    'error':'AI servisi sunucuda henüz yapılandırılmamış.',
                    'needs_config':True
                },503)

            if self.path=='/api/analyze_fast':
                text=str(d.get('text',''))
                if len(text)>4000: return self.send_json({'error':'Metin çok uzun.'},400)
                a=analyze_fast(text,str(d.get('context',''))[:8000],str(d.get('selected_intent','')))
                return self.send_json({'analysis':a,'model':MODEL,'version':'VFINAL2','stage':'primary'})

            if self.path=='/api/analyze_enrich':
                text=str(d.get('text',''))
                if len(text)>4000: return self.send_json({'error':'Metin çok uzun.'},400)
                a=enrich_analysis(d.get('analysis') or {},text,str(d.get('selected_intent','')),str(d.get('context',''))[:8000])
                return self.send_json({'analysis':a,'model':MODEL,'version':'VFINAL2','stage':'enrichment'})

            if self.path=='/api/context_shadow':
                text=str(d.get('text',''))
                if len(text)>4000: return self.send_json({'error':'Metin çok uzun.'},400)
                out=context_shadow(text,str(d.get('context',''))[:8000])
                return self.send_json({'shadow':out,'model':MODEL,'version':'VFINAL2'})

            if self.path=='/api/analyze':
                text=str(d.get('text',''))
                if len(text)>4000: return self.send_json({'error':'Metin çok uzun.'},400)
                a=analyze(text,str(d.get('context',''))[:8000],str(d.get('selected_intent','')))
                return self.send_json({'analysis':a,'model':MODEL,'version':'VFINAL2'})

            if self.path=='/api/chat':
                pid=str(d.get('person_id',''))
                hist=(d.get('history') or [])[-12:]
                opening=bool(d.get('opening',False))
                if pid not in PERSONAS:
                    return self.send_json({'error':'Bilinmeyen bot'},400)
                if opening and not hist:
                    hist=[{'from':'me','text':'Konuşmayı sen başlat: doğal, kısa bir selam ver ve halimi sor.'}]
                out=chat_combined(pid,hist)
                model_label=MODEL if out.get('chat_mode')!='local_fallback' else 'NİYET yerel sohbet yedeği'
                return self.send_json({
                    'reply':out['reply'],
                    'analysis':out['user_analysis'],
                    'reply_analysis':out['reply_analysis'],
                    'model':model_label,
                    'version':'VFINAL2',
                    'chat_mode':out.get('chat_mode')
                })

            if self.path=='/api/bot_comment':
                pid=str(d.get('person_id',''))
                if pid not in PERSONAS:
                    return self.send_json({'error':'Bilinmeyen bot'},400)
                post=str(d.get('post_text',''))[:5000]
                user_comment=str(d.get('user_comment',''))[:3000]
                comments=(d.get('comments') or [])[-8:]
                out=bot_comment_combined(pid,post,user_comment,comments)
                return self.send_json({
                    'reply':out['reply'],
                    'user_analysis':out['user_analysis'],
                    'reply_analysis':out['reply_analysis'],
                    'model':MODEL,
                    'version':'VFINAL2'
                })

            return self.send_json({'error':'Not found'},404)
        except json.JSONDecodeError:
            return self.send_json({'error':'Geçersiz JSON isteği.'},400)
        except Exception as e:
            print('[NİYET VFINAL2 WEB] hata:',repr(e))
            return self.send_json({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

def main():
    print('\nNİYET VFINAL2 WEB — yerel/yedek web sunucusu')
    print('Adres:',f'{HOST}:{PORT}')
    print('Model:',MODEL)
    print('OpenAI:', 'hazır' if API_KEY else 'OPENAI_API_KEY eksik')
    print('Rate limit:',RATE_LIMIT_PER_MIN,'istek/dk/IP')
    srv=ThreadingHTTPServer((HOST,PORT),Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()

if __name__=='__main__':
    main()
