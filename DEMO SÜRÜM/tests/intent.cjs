const fs=require('fs'),vm=require('vm'),assert=require('assert');const read=n=>fs.readFileSync(require('path').join(__dirname,n+'-under-test.js'),'utf8');
(async()=>{
let fetches=[],c={apiConnected:true,lastCalibrationMeta:null,setApiBadge:()=>{},console:{warn:()=>{}},localAnalyzeV9:()=>({_source:'local'}),fetch:async(url,opt)=>{fetches.push([url,JSON.parse(opt.body)]);return {ok:true,json:async()=>({analysis:{intent_distribution:{Soru:70},decision_layer:{selected_share:70},calibration_meta:{version:'1',available:true},enrichment_pending:true}})}}};
vm.createContext(c);vm.runInContext(read('intent-api'),c);
let a=await c.apiAnalyzeFastV14('Aynen','context A','Soru');await c.apiAnalyzeFastV14('Aynen','context A','Soru');assert.equal(fetches.length,1);
await c.apiAnalyzeFastV14('Aynen','context B','Soru');assert.equal(fetches.length,2);
await c.apiAnalyzeEnrichV14('Aynen','context A','Soru',a);await c.apiAnalyzeEnrichV14('Aynen','context A','Soru',a);assert.equal(fetches.length,3);
await c.apiAnalyzeEnrichV14('Aynen','context A','Soru',{...a,decision_layer:{selected_share:20}});assert.equal(fetches.length,4);
c.fetch=async()=>({ok:false,json:async()=>({error:'Calibration unavailable',calibration:{available:false,status:'unavailable'}})});let fallback=await c.apiAnalyzeFastV14('different','context','Soru');assert.equal(fallback._source,'local');assert.equal(c.lastCalibrationMeta.available,false);
let el={newPostText:{value:'Mal ve hizmet satın aldım.'},intent:{value:'Bilgilendirme'},analysisModal:{classList:{contains:()=>false}},aStabilityNote:{}},calls=0,renders=0,load=[],release;
let q={document:{getElementById:id=>el[id]},v14AnalysisRequest:0,apiConnected:true,pendingPostAnalysis:null,setAnalyzeLoading:x=>load.push(x),toast:()=>{},renderPostAnalysis:()=>renders++,showAnalysisServiceFallbackVFinal:()=>{},console:{warn:()=>{}},apiAnalyzeFastV14:async()=>{calls++;return {_source:'luna',enrichment_pending:true}},apiAnalyzeEnrichV14:async()=>{throw Error('test fail')}};
vm.createContext(q);vm.runInContext(read('analyze-post'),q);await q.analyzePost();await new Promise(r=>setImmediate(r));assert.equal(calls,1);assert.equal(q.pendingPostAnalysis.enrichment_pending,false);assert.equal(q.pendingPostAnalysis.stability.available,false);
q.apiAnalyzeFastV14=()=>new Promise(r=>release=r);let before=renders,p=q.analyzePost();el.intent.value='Soru';release({_source:'luna'});await p;assert.equal(renders,before);assert.equal(load.at(-1),false);
console.log('7 intent UI checks passed: context cache, base cache, calibration failure, semantic path, enrichment failure and stale selection.');
})().catch(e=>{console.error(e);process.exit(1)});
