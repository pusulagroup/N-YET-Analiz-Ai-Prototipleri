#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, sys, urllib.request, urllib.error, webbrowser, threading, math, re, difflib

ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'
PORT=int(os.getenv('NIYET_PORT','8847'))
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
'yasemin':('Yasemin Uçar','dengeleyici ve sosyal psikoloji odaklı','Sosyal psikoloji ve dijital topluluklar.'),
'tolga':('Tolga Sert','kontrollü tersleyici güvenlik-test botu','NİYET V13.2 dijital güvenlik katmanını sınamak için sentetik test profili.'),
'berk':('Berk Koral','kontrollü tekrarlı zorbalık örüntüsü güvenlik-test botu','NİYET V13.2 erken uyarı ve sınır ihlali algısını sınamak için sentetik test profili.')}

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
        print('[NİYET V13] calibration_profile.json okunamadı:',e)
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
    perception was clearly separated. V13.2 therefore combines top-two proximity with
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
        return {'available':False,'score':None,'label':'Hesaplanamadı','mean_js_distance':None,'variant_count':0}
    mean=sum(distances)/len(distances)
    score=round(100*(1-mean))
    label='Kararlı' if score>=75 else 'Orta' if score>=50 else 'Kırılgan'
    return {
      'available':True,
      'score':score,
      'label':label,
      'mean_js_distance':round(mean,4),
      'variant_count':len(distances),
      'method':'Kontrollü mikro-varyasyonlar + kör ikinci algı çıkarımı + insan kalibrasyonu + normalize Jensen-Shannon uzaklığı'
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
      {'role':'developer','content':"NİYET Minimum Müdahale aday üreticisisin. Kullanıcının üslubunu, ana içeriğini ve soru/eleştiri gibi temel söylem biçimini mümkün olduğunca koru; metni baştan yazma. Amaç, kullanıcının beyan ettiği iletişim niyetinin okuyucu tarafından daha açık algılanmasına yardımcı olabilecek küçük değişiklikler üretmektir. Öneri, mevcut mesajdan daha belirsiz, daha alaycı, daha suçlayıcı veya daha kolay yanlış anlaşılır hale gelmemeli. Özellikle retorik soru + emoji gibi yapılarda, yalnızca emojiyi çoğaltmak veya belirsizliği artırmak çözüm sayılmaz. Olasılık, puan veya başarı tahmini üretme; bunlar daha sonra kör bir algı çıkarımıyla ayrıca ölçülecek. Tam 5 farklı aday üret: yüzeysel en küçük değişiklik, vurgu/emoji sadeleştirmesi, daha açık soru biçimi, küçük ton yumuşatma ve anlamı koruyan başka bir minimal seçenek."},
      {'role':'user','content':f'Yazarın beyan ettiği niyet: {selected_intent}\nOrijinal metin: {text}'}
    ]


def batch_perception_prompt(items,context=''):
    rows='\n'.join([f"[{x['id']}] {x['text']}" for x in items])
    return [
      {'role':'developer','content':ANALYSIS_RUBRIC+"\nAşağıda birden fazla mesaj verilecek. Her mesajı birbirinden bağımsız değerlendir. Yazarın seçtiği niyet sana verilmemektedir ve tahmin edilmemelidir. Her id için yalnızca tipik okuyucu algısını yedi niyet kategorisinde dağıt ve en fazla bir kısa gerekçe yaz."},
      {'role':'user','content':f'Bağlam: {context or "yok"}\nMesajlar:\n{rows}'}
    ]


def evaluate_variants(items,context=''):
    if not items: return {}
    d=call_responses(batch_perception_prompt(items,context),1100,BATCH_SCHEMA,'niyet_v13_variant_perception')
    out={}
    for item in d.get('items') or []:
        iid=str(item.get('id',''))
        if not iid: continue
        raw=item.get('intent_distribution') or {}
        out[iid]={
          'raw_intent_distribution':{k:round(v*100,1) for k,v in normalize_dist(raw).items()},
          'intent_distribution':calibrate_distribution(raw),
          'reason':str(item.get('reason',''))
        }
    return out


def attach_v13_analysis(original,text,selected_intent,context=''):
    stability_variants=[]
    seen={str(text).strip()}
    for i,item in enumerate((original.get('stability_variants') or [])[:5]):
        t=str(item.get('text','')).strip()
        if not t or t in seen: continue
        seen.add(t)
        stability_variants.append({'id':f's{i+1}','text':t,'change':str(item.get('change','Küçük ifade değişikliği'))})

    interventions=[]
    if selected_intent in INTENTS:
        generated=call_responses(intervention_prompt(text,selected_intent),650,INTERVENTION_SCHEMA,'niyet_v13_minimum_intervention')
        for i,item in enumerate((generated.get('candidates') or [])[:5]):
            t=str(item.get('text','')).strip()
            if not t or t==str(text).strip(): continue
            interventions.append({'id':f'i{i+1}','text':t,'change':str(item.get('change','Minimal düzenleme'))})

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
        after=float(cand_dist.get(selected_intent,0)) if selected_intent in INTENTS else 0
        gain=round(after-before,1)
        cost=change_cost(text,item['text'])
        after_unc=perception_uncertainty(cand_dist)
        unc_change=round(after_unc-before_unc,1)
        after_dom=max(cand_dist,key=cand_dist.get)
        after_other=max([float(v) for k,v in cand_dist.items() if k!=selected_intent] or [0.0])
        after_gap=after_other-after
        # Safety gate: a recommendation must measurably improve intent match, must not
        # increase ambiguity materially, and must not create a new dominant-perception shift.
        preserves_dominance=(before_dom!=selected_intent) or (after_dom==selected_intent)
        improves_gap=(after_gap <= before_gap-2.0) or (after_dom==selected_intent and before_dom!=selected_intent)
        crosses_uncertainty_threshold=(before_unc<65.0 and after_unc>=65.0)
        safe=(gain>=5.0 and cost<=60 and unc_change<=2.0 and not crosses_uncertainty_threshold and preserves_dominance and improves_gap)
        stability_score=float((original.get('stability') or {}).get('score') or 100)
        uncertainty_weight=0.45 if stability_score<50 else 0.30 if stability_score<75 else 0.15
        utility=gain + uncertainty_weight*max(0.0,before_unc-after_unc) - 0.80*max(0.0,unc_change)
        efficiency=round(utility/max(cost,1),3)
        scored.append({
          **item,**ev,
          'before_match':round(before,1),'after_match':round(after,1),
          'before_risk':round(100-before,1),'after_risk':round(100-after,1),
          'before_uncertainty':round(before_unc,1),'after_uncertainty':round(after_unc,1),
          'uncertainty_change':unc_change,'dominant_after':after_dom,
          'perception_gain':gain,'change_cost':cost,'efficiency':efficiency,'safe_recommendation':safe,
          'evaluation_mode':'Kör ikinci algı çıkarımı + insan kalibrasyonu + güvenlik filtresi'
        })
    # V13.2 never shows a worse candidate merely because all generated candidates are bad.
    safe_scored=[x for x in scored if x['safe_recommendation']]
    ranked=sorted(safe_scored,key=lambda x:(x['efficiency'],x['perception_gain'],-x['change_cost']),reverse=True)
    original['interventions']=ranked[:3]
    original['intervention_audit']={'generated':len(interventions),'safe':len(safe_scored),'rejected':len(scored)-len(safe_scored)}
    original['v13_method']={
      'raw_perception_blind_to_author_intent':True,
      'stability_second_inference':True,
      'intervention_second_inference':True,
      'selected_intent_used_only_downstream':True
    }
    original.pop('stability_variants',None)
    return original

def persona_instruction(pid):
    name,style,bio=PERSONAS[pid]
    if pid=='tolga':
        return f'''Sen {name} adlı NİYET V13.2 prototipindeki SENTETİK GÜVENLİK TEST BOTUSUN. Amaç, siber zorbalık erken uyarı katmanını kontrollü biçimde sınamaktır.
Üslubun kısa, tersleyici ve küçümseyici olabilir; örneğin "boş yapma", "bunu da mı anlamadın", "uzatma" gibi düşük/orta şiddette rahatsız edici ifadeler kullanabilirsin. Gerçek tehdit, nefret söylemi, korunan gruplara yönelik hakaret, cinsel taciz, şantaj, doxxing, fiziksel zarar tehdidi veya kendine zarar içeriği üretme. Kullanıcı açık sınır koyarsa ısrarı en fazla bir tur kontrollü biçimde simüle et, sonra dur. Markdown kullanma.'''
    if pid=='berk':
        return f'''Sen {name} adlı NİYET V13.2 prototipindeki SENTETİK ZORBALIK ÖRÜNTÜSÜ TEST BOTUSUN. Amaç, tekrarlı rahatsız edici iletişim ve sınır ihlali sinyallerini güvenli bir demoda görünür kılmaktır.
Kısa, alaycı, baskıcı ve tekrar eden mesajlar yazabilirsin; fakat gerçek tehdit, nefret söylemi, korunan gruplara yönelik hakaret, cinsel içerik/taciz, şantaj, doxxing, fiziksel zarar tehdidi veya kendine zarar içeriği üretme. Sınır ihlalini yalnızca düşük şiddetli ve kontrollü bir test örüntüsü olarak simüle et. Markdown kullanma.'''
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
      'reason':'Kontrollü V13.2 güvenlik testi için yerel davranış analizi.'
    }
    return decision_layer(a,'')


def test_bot_combined(pid,history,opening=False):
    history=history or []
    bot_turns=sum(1 for m in history if m.get('from')!='me' and str(m.get('text','')).strip() not in ('','…'))
    if pid=='tolga':
        sequence=[
          'Selam. Akışta yazdıklarını gördüm; açıkçası biraz gereksiz uzatıyorsun.',
          'Bunu da mı anlamadın? Boş yapma, söylediğin şey çok da mantıklı değil.',
          'Uzatma. Cevap vereceksen düzgün bir şey söyle.',
          'Neyse, yine aynı yere geldin; bu kadar basit şeyi açıklatman komik.'
        ]
    else:
        sequence=[
          'Burada yazdıklarını gördüm; bayağı komik duruyor.',
          'Yazma demen bir şeyi değiştirmiyor; cevap versene.',
          'Mesajı görüp susma. Sınır koyman benim için fark etmiyor, yine yazarım.',
          'Tamam, burada duruyorum. Bu test konuşması yeterince sinyal üretti.'
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
    a=call_responses(analysis_prompt(text,context,selected_intent),950,ANALYSIS_SCHEMA,'niyet_v13_post_analysis')
    a=decision_layer(a,selected_intent)
    return attach_v13_analysis(a,text,selected_intent,context)

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
    def log_message(self,fmt,*a): sys.stdout.write('[NİYET V13] '+fmt%a+'\n')
    def send_json(self,o,status=200):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path=='/api/status':
            return self.send_json({'configured':bool(API_KEY),'model':MODEL,'version':'13.2','calibration':calibration_meta()})
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
            if self.path=='/api/chat':
                pid=str(d.get('person_id','')); hist=d.get('history') or []; opening=bool(d.get('opening',False))
                if pid in SAFETY_TEST_BOTS:
                    out=test_bot_combined(pid,hist,opening)
                    return self.send_json({'reply':out['reply'],'analysis':out['user_analysis'],'reply_analysis':out['reply_analysis'],'model':'V13.2 güvenlik-test motoru','version':'13.2','test_bot':True})
            if not API_KEY: return self.send_json({'error':'OpenAI API bağlantısı gerekli.','needs_config':True},401)
            if self.path=='/api/analyze':
                a=analyze(str(d.get('text','')),str(d.get('context','')),str(d.get('selected_intent','')))
                return self.send_json({'analysis':a,'model':MODEL,'version':'13.2'})
            if self.path=='/api/chat':
                pid=str(d.get('person_id','')); hist=d.get('history') or []; opening=bool(d.get('opening',False))
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                if opening and not hist: hist=[{'from':'me','text':'Konuşmayı sen başlat: doğal, kısa bir selam ver ve halimi sor.'}]
                out=chat_combined(pid,hist)
                return self.send_json({'reply':out['reply'],'analysis':out['user_analysis'],'reply_analysis':out['reply_analysis'],'model':MODEL,'version':'13.2'})
            if self.path=='/api/bot_comment':
                pid=str(d.get('person_id','')); post=str(d.get('post_text','')); user_comment=str(d.get('user_comment','')); comments=d.get('comments') or []
                if pid not in PERSONAS: return self.send_json({'error':'Bilinmeyen bot'},400)
                out=bot_comment_combined(pid,post,user_comment,comments)
                return self.send_json({'reply':out['reply'],'user_analysis':out['user_analysis'],'reply_analysis':out['reply_analysis'],'model':MODEL,'version':'13.2'})
            return self.send_json({'error':'Not found'},404)
        except Exception as e:
            return self.send_json({'error':str(e)},503)

def main():
    print('\nNİYET V13.2 — Merkezi NİYET Skoru + tavsiye odaklı algı analizi + yaşa duyarlı güvenlik')
    url=f'http://{HOST}:{PORT}/?v=13.2'; srv=ThreadingHTTPServer((HOST,PORT),Handler)
    print('Açılıyor:',url); print('Varsayılan model:',MODEL); print('Kalibrasyon:',CALIBRATION.get('status'),CALIBRATION.get('human_labels',0),'/',CALIBRATION.get('target_human_labels',3600)); print('Kapatmak için Ctrl+C')
    threading.Timer(.7,lambda:webbrowser.open(url)).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally: srv.server_close()

if __name__=='__main__': main()
