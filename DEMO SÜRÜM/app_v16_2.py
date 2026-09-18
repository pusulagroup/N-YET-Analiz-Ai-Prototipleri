from pathlib import Path
import os
import time
import threading

from flask import Flask, request, jsonify, send_file, abort, make_response
from werkzeug.utils import safe_join

import run_v16_web as core

ROOT=Path(__file__).resolve().parent
VIDEOS=(ROOT/'videos').resolve()

app=Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH']=6*1024*1024

RATE_LIMIT_PER_MIN=max(10,int(os.getenv('NIYET_RATE_LIMIT_PER_MIN','60')))
_RATE_LOCK=threading.Lock()
_RATE_BUCKETS={}

def _client_ip():
    forwarded=str(request.headers.get('X-Forwarded-For','')).split(',')[0].strip()
    return forwarded or request.remote_addr or 'unknown'

def _rate_allowed():
    now=time.time()
    ip=_client_ip()
    with _RATE_LOCK:
        bucket=[t for t in _RATE_BUCKETS.get(ip,[]) if now-t<60]
        if len(bucket)>=RATE_LIMIT_PER_MIN:
            _RATE_BUCKETS[ip]=bucket
            return False
        bucket.append(now)
        _RATE_BUCKETS[ip]=bucket
        if len(_RATE_BUCKETS)>2000:
            cutoff=now-120
            for k in list(_RATE_BUCKETS)[:500]:
                if not any(t>=cutoff for t in _RATE_BUCKETS.get(k,[])):
                    _RATE_BUCKETS.pop(k,None)
        return True

def j(payload,status=200):
    return jsonify(payload),status

@app.after_request
def security_headers(resp):
    resp.headers['X-Content-Type-Options']='nosniff'
    resp.headers['X-Frame-Options']='DENY'
    resp.headers['Referrer-Policy']='no-referrer'
    resp.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    return resp

@app.get('/')
def index():
    return send_file(ROOT/'index.html',mimetype='text/html',conditional=True,max_age=0)

@app.get('/robots.txt')
def robots_txt():
    body=(
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /api/\n'
        'Sitemap: https://niyetaiapp.com/sitemap.xml\n'
    )
    resp=make_response(body,200)
    resp.headers['Content-Type']='text/plain; charset=utf-8'
    resp.headers['Cache-Control']='public, max-age=3600'
    return resp

@app.get('/sitemap.xml')
def sitemap_xml():
    body='''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://niyetaiapp.com/</loc>
    <lastmod>2026-08-20</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
'''
    resp=make_response(body,200)
    resp.headers['Content-Type']='application/xml; charset=utf-8'
    resp.headers['Cache-Control']='public, max-age=3600'
    return resp

@app.get('/healthz')
def healthz():
    return j({'ok':True,'version':core.RELEASE_VERSION,'ai_configured':bool(core.API_KEY)})

@app.get('/api/status')
def api_status():
    return j({
        'configured':bool(core.API_KEY),
        'model':core.MODEL if core.API_KEY else '',
        'version':core.RELEASE_VERSION,
        'web_mode':True,
        'calibration':core.calibration_meta()
    })

@app.route('/videos/<path:filename>',methods=['GET','HEAD'])
def video(filename):
    # Yalnızca mp4 ve videos/ klasörünün içi.
    if not filename.lower().endswith('.mp4'):
        abort(404)
    candidate=safe_join(str(VIDEOS),filename)
    if not candidate:
        abort(404)
    p=Path(candidate).resolve()
    if VIDEOS not in p.parents or not p.is_file():
        abort(404)

    # Flask/Werkzeug conditional=True ile HTTP Range / 206 yanıtını yönetir.
    resp=send_file(
        p,
        mimetype='video/mp4',
        conditional=True,
        as_attachment=False,
        max_age=86400,
        etag=True
    )
    resp.headers['Accept-Ranges']='bytes'
    resp.headers['Content-Disposition']='inline'
    return resp

@app.before_request
def limit_api():
    if request.path.startswith('/api/') and request.method=='POST':
        if not _rate_allowed():
            return j({'error':'Çok fazla istek gönderildi. Lütfen kısa süre sonra tekrar dene.'},429)

@app.post('/api/config')
def api_config():
    return j({'error':'Web sürümünde API anahtarı sunucu ortam değişkeni olarak yönetilir.'},403)

@app.post('/api/reload_calibration')
def reload_calibration():
    return j({'error':'Public web sürümünde bu işlem kapalıdır.'},403)

def _payload():
    data=request.get_json(silent=True)
    if not isinstance(data,dict):abort(400)
    if core.payload_error_v12(data):abort(400)
    return data

@app.post('/api/analyze_behavior')
def analyze_behavior_route():
    if not core.API_KEY:return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload();text=d.get('text','');context=d.get('context','')
    if not isinstance(text,str) or not isinstance(context,str) or not text.strip() or len(text)>4000 or len(context)>8000:
        return j({'error':'Geçersiz metin veya bağlam.'},400)
    try:return j({'analysis':core.analyze_behavior(text,context),'model':core.MODEL,'version':core.RELEASE_VERSION,'stage':'behavior'})
    except Exception:
        app.logger.exception('analyze_behavior')
        return j({'error':'Davranış analizi tamamlanamadı.','retryable':True},503)

@app.errorhandler(400)
def bad_request(_):return j({'error':'Geçersiz istek.'},400)

@app.post('/api/analyze_fast')
def analyze_fast_route():
    if not core.calibration_available():
        return j({'error':'İnsan algısı kalibrasyon profili eksik veya geçersiz.','calibration':core.calibration_meta()},503)
    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload()
    text=str(d.get('text',''))
    if len(text)>4000:
        return j({'error':'Metin çok uzun.'},400)
    try:
        a=core.analyze_fast(text,str(d.get('context',''))[:8000],str(d.get('selected_intent','')))
        return j({'analysis':a,'model':core.MODEL,'version':core.RELEASE_VERSION,'stage':'primary'})
    except Exception as e:
        app.logger.exception("analyze_fast")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.post('/api/analyze_enrich')
def analyze_enrich_route():
    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload()
    text=str(d.get('text',''))
    if len(text)>4000:
        return j({'error':'Metin çok uzun.'},400)
    try:
        a=core.enrich_analysis(d.get('analysis') or {},text,str(d.get('selected_intent','')),str(d.get('context',''))[:8000])
        return j({'analysis':a,'model':core.MODEL,'version':core.RELEASE_VERSION,'stage':'enrichment'})
    except Exception:
        app.logger.exception("analyze_enrich")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.post('/api/context_shadow')
def context_shadow_route():
    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload()
    text=str(d.get('text',''))
    if len(text)>4000:
        return j({'error':'Metin çok uzun.'},400)
    try:
        out=core.context_shadow(text,str(d.get('context',''))[:8000])
        return j({'shadow':out,'model':core.MODEL,'version':core.RELEASE_VERSION})
    except Exception:
        app.logger.exception("context_shadow")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.post('/api/analyze')
def analyze_route():
    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload()
    text=str(d.get('text',''))
    if len(text)>4000:
        return j({'error':'Metin çok uzun.'},400)
    try:
        a=core.analyze(text,str(d.get('context',''))[:8000],str(d.get('selected_intent','')))
        return j({'analysis':a,'model':core.MODEL,'version':core.RELEASE_VERSION})
    except Exception:
        app.logger.exception("analyze")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.post('/api/chat')
def chat_route():
    d=_payload()
    pid=str(d.get('person_id',''))
    hist=(d.get('history') or [])[-12:]
    opening=bool(d.get('opening',False))

    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)

    if pid not in core.PERSONAS:
        return j({'error':'Bilinmeyen bot'},400)
    if opening and not hist:
        hist=[{'from':'me','text':'Konuşmayı sen başlat: doğal, kısa bir selam ver ve halimi sor.'}]
    try:
        out=core.reply_only_combined(pid,history=hist) if d.get('reply_only') is True else core.chat_combined(pid,hist)
        model_label=core.MODEL if out.get('chat_mode')!='local_fallback' else 'NİYET yerel sohbet yedeği'
        return j({
            'reply':out['reply'],
            'analysis':out['user_analysis'],
            'reply_analysis':out['reply_analysis'],
            'model':model_label,
            'version':core.RELEASE_VERSION,
            'chat_mode':out.get('chat_mode')
        })
    except Exception:
        app.logger.exception("chat")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.post('/api/bot_comment')
def bot_comment_route():
    if not core.API_KEY:
        return j({'error':'AI servisi sunucuda henüz yapılandırılmamış.','needs_config':True},503)
    d=_payload()
    pid=str(d.get('person_id',''))
    if pid not in core.PERSONAS:
        return j({'error':'Bilinmeyen bot'},400)
    try:
        out=core.reply_only_combined(pid,post_text=str(d.get('post_text',''))[:5000],user_comment=str(d.get('user_comment',''))[:3000],comments=(d.get('comments') or [])[-8:]) if d.get('reply_only') is True else core.bot_comment_combined(pid,str(d.get('post_text',''))[:5000],str(d.get('user_comment',''))[:3000],(d.get('comments') or [])[-8:])
        return j({
            'reply':out['reply'],
            'user_analysis':out['user_analysis'],
            'reply_analysis':out['reply_analysis'],
            'model':core.MODEL,
            'version':core.RELEASE_VERSION
        })
    except Exception:
        app.logger.exception("bot_comment")
        return j({'error':'AI servisine şu anda ulaşılamıyor. Lütfen tekrar deneyin.','retryable':True},503)

@app.errorhandler(404)
def not_found(_):
    return j({'error':'Not found'},404)

@app.errorhandler(413)
def too_large(_):
    return j({'error':'Geçersiz istek boyutu.'},413)
