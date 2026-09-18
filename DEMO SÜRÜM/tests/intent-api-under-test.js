const v14FastCache=new Map(),v14EnrichCache=new Map();
function v14AnalysisKey(text,selected,context='',base=null){return JSON.stringify([String(text),selected,String(context),base?.intent_distribution||null,base?.decision_layer||null,base?.calibration_meta?.version||null])}
function cloneV14(o){return JSON.parse(JSON.stringify(o))}
async function fetchWithTimeoutVFinal(url,options={},timeoutMs=0){
  // VFINAL3 acil: istemci tarafı timeout kaldırıldı. Render Free cold-start sırasında
  // çalışan AI isteğinin 20/35 saniyede yanlışlıkla kesilmesini önler.
  return await fetch(url,options);
}
async function apiAnalyzeFastV14(text,context='',selectedIntent=''){
  // API durum rozeti eski/yanlış olsa bile gerçek endpoint her analizde denenir.
  // Böylece Render yeniden başlatma/cold-start sonrası tek başarısız status kontrolü sistemi kilitlemez.
  let key=v14AnalysisKey(text,selectedIntent,context),cached=v14FastCache.get(key);if(cached)return cloneV14(cached);
  try{
    let r=await fetchWithTimeoutVFinal('/api/analyze_fast',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,context,selected_intent:selectedIntent})});
    let d=await r.json();if(d.calibration)lastCalibrationMeta=d.calibration;if(!r.ok)throw new Error(d.error||'Hızlı analiz başarısız');let a=d.analysis;a._source='luna';apiConnected=true;setApiBadge(true,d.model||'');if(a?.calibration_meta)lastCalibrationMeta=a.calibration_meta;v14FastCache.set(key,cloneV14(a));return a;
  }catch(e){console.warn('V14 hızlı API analizi:',e);let a=localAnalyzeV9(text,selectedIntent);a._fallback_error=e.message;return a}
}
async function apiAnalyzeEnrichV14(text,context,selectedIntent,base){
  if(!apiConnected||base?._source!=='luna')return base;
  let key=v14AnalysisKey(text,selectedIntent,context,base),cached=v14EnrichCache.get(key);if(cached)return cloneV14(cached);
  let r=await fetch('/api/analyze_enrich',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,context,selected_intent:selectedIntent,analysis:base})});
  let d=await r.json();if(!r.ok)throw new Error(d.error||'Derin analiz başarısız');let a=d.analysis;a._source='luna';if(a?.calibration_meta)lastCalibrationMeta=a.calibration_meta;v14EnrichCache.set(key,cloneV14(a));return a;
}
