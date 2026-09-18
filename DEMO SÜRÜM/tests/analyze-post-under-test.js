async function analyzePost(){
  let txt=document.getElementById('newPostText').value.trim();if(!txt){toast('Önce bir paylaşım yaz.');return}
  let selected=document.getElementById('intent').value,context='Yeni sosyal medya paylaşımı',req=++v14AnalysisRequest;
  setAnalyzeLoading(true);toast(apiConnected?'Hızlı insan-kalibre NİYET analizi hazırlanıyor…':'API bağlı değil · yalnızca yerel ön analiz çalışıyor…');
  try{
    let primary=await apiAnalyzeFastV14(txt,context,selected);if(req!==v14AnalysisRequest)return;if(document.getElementById('intent').value!==selected||document.getElementById('newPostText').value.trim()!==txt){setAnalyzeLoading(false);return;}
    primary.enrichment_pending=(primary._source==='luna'&&primary?.analysis_scope?.scoreable!==false&&primary.enrichment_pending!==false);pendingPostAnalysis=primary;renderPostAnalysis(primary,selected);if(primary._fallback_error)showAnalysisServiceFallbackVFinal();setAnalyzeLoading(false);
    if(primary._source!=='luna'){toast(primary._fallback_error?'AI servisine şu anda ulaşılamıyor · yerel ön analiz gösterildi.':'Yerel ön analiz hazır. Nihai insan-kalibre sonuç için Luna bağlantısı gerekli.');return}
    // Kullanıcı ana sonucu gördükten sonra derin analiz arka planda devam eder.
    apiAnalyzeEnrichV14(txt,context,selected,primary).then(enriched=>{
      if(req!==v14AnalysisRequest)return;
      if(document.getElementById('newPostText').value.trim()!==txt||document.getElementById('intent').value!==selected)return;
      enriched.enrichment_pending=false;pendingPostAnalysis=enriched;
      if(!document.getElementById('analysisModal').classList.contains('hidden'))renderPostAnalysis(enriched,selected);
    }).catch(e=>{console.warn('V14 derin analiz:',e);if(req===v14AnalysisRequest&&document.getElementById('newPostText').value.trim()===txt&&document.getElementById('intent').value===selected){primary.enrichment_pending=false;primary.stability={available:false,score:null,label:'Hesaplanamadı',variant_count:0};pendingPostAnalysis=primary;if(!document.getElementById('analysisModal').classList.contains('hidden')){renderPostAnalysis(primary,selected);let el=document.getElementById('aStabilityNote');if(el){el.className='stability-note';el.innerHTML='<b>AI servisine şu anda ulaşılamıyor.</b> Ana analiz korunuyor; Algı Kararlılığı / İfade Önerisi bu turda tamamlanamadı. Lütfen tekrar deneyin.'}}}});
  }catch(e){toast('Analiz başarısız: '+e.message);setAnalyzeLoading(false)}
}
