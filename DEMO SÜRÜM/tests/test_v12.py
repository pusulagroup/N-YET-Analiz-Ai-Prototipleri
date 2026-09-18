import importlib.util, unittest, time, copy, concurrent.futures, threading, json, ast, urllib.request
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('baseline',Path(__file__).with_name('test_backend.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);m=b.m
class NewTests(unittest.TestCase):
 def setUp(self):
  for store in [m._FAST_CACHE,m._RAW_CACHE,m._BEHAVIOR_CACHE,m._ENRICH_CACHE,m._SHADOW_CACHE,m._CACHE_TIMES,m._INFLIGHT]:store.clear()
 def test_parallel_identical_requests_coalesce(self):
  barrier=threading.Barrier(8)
  def compute():time.sleep(.08);return {'value':[1]}
  def worker(_):barrier.wait();return m.cached_compute_v12(m._RAW_CACHE,'key',compute)
  with patch.object(m,'_cache_put',wraps=m._cache_put) as put,concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
   results=list(ex.map(worker,range(8)))
  self.assertEqual(put.call_count,1);results[0]['value'][0]=9;self.assertEqual(results[1]['value'],[1]);self.assertFalse(m._INFLIGHT)
 def test_failure_cleans_inflight(self):
  with self.assertRaises(RuntimeError):m.cached_compute_v12(m._RAW_CACHE,'k',lambda:(_ for _ in ()).throw(RuntimeError()))
  self.assertFalse(m._INFLIGHT);self.assertEqual(m.cached_compute_v12(m._RAW_CACHE,'k',lambda:3),3)
 def test_expiry(self):
  m._cache_put(m._RAW_CACHE,'k',{'a':1});self.assertIsNotNone(m._cache_get(m._RAW_CACHE,'k'))
  with patch.object(m.time,'monotonic',return_value=time.monotonic()+301):self.assertIsNone(m._cache_get(m._RAW_CACHE,'k'))
 def test_profile_change_invalidates_key(self):
  before=m.calibration_fingerprint_v12();profile=copy.deepcopy(m.CALIBRATION);profile['coefficients']['intercepts'][0]+=.01
  with patch.object(m,'CALIBRATION',profile):self.assertNotEqual(before,m.calibration_fingerprint_v12())
 def test_behavior_reuses_full_analysis(self):
  with patch.object(m,'call_responses',return_value=b.analysis()) as call:
   m.analyze_fast('Toplantı ne zaman başlayacak?','ctx','Soru');a=m.analyze_behavior('Toplantı ne zaman başlayacak?','ctx')
   self.assertEqual(call.call_count,1);self.assertNotIn('intent_distribution',a);self.assertIn('is_respectful',a)
 def test_behavior_schema_and_cache(self):
  fixture={k:v for k,v in b.analysis().items() if k in m.BEHAVIOR_PROPERTIES}
  with patch.object(m,'call_responses',return_value=fixture) as call:
   self.assertEqual(m.analyze_behavior('Mal aldım.'),fixture);m.analyze_behavior('Mal aldım.');self.assertEqual(call.call_count,1)
   self.assertNotIn('intent_distribution',call.call_args.args[2]['properties'])
 def test_behavior_http_and_bad_payload(self):
  c=b.appmod.app.test_client()
  with patch.object(m,'API_KEY','test'),patch.object(m,'analyze_behavior',return_value={'is_calming':True}):
   r=c.post('/api/analyze_behavior',json={'text':'Sakin konuşalım.'});self.assertEqual(r.status_code,200);self.assertEqual(r.json['version'],'V12-2026-09-18')
   for data in [[],None,{'text':''},{'text':[]},{'text':'x','context':'x'*8001},{'text':'x'*4001}]:self.assertEqual(c.post('/api/analyze_behavior',json=data).status_code,400)
 def test_all_assets_and_restricted_paths(self):
  c=b.appmod.app.test_client();paths=list(b.ROOT.joinpath('videos').glob('*.mp4'));self.assertEqual(len(paths),25)
  for p in paths:
   r=c.get('/videos/'+p.name,headers={'Range':'bytes=0-31'});self.assertEqual(r.status_code,206);self.assertEqual(len(r.data),32);r.close()
  for path in ['/.env','/run_v16_web.py','/videos/../run_v16_web.py','/videos/no.mp4']:
   self.assertEqual(c.get(path).status_code,404)
  self.assertEqual(c.post('/api/config',json={}).status_code,403)
 def test_syntax(self):
  for p in b.ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
 def test_standalone_server_behavior(self):
  srv=m.ThreadingHTTPServer(('127.0.0.1',0),m.Handler);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
  try:
   with patch.object(m,'API_KEY','test'),patch.object(m,'analyze_behavior',return_value={'is_calming':True}):
    req=urllib.request.Request('http://127.0.0.1:'+str(srv.server_port)+'/api/analyze_behavior',data=json.dumps({'text':'Sakin konuşalım.'}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as response:result=json.load(response)
    self.assertTrue(result['analysis']['is_calming']);self.assertEqual(result['version'],m.RELEASE_VERSION)
  finally:srv.shutdown();srv.server_close();thread.join()
 def test_invalid_types_are_400(self):
  with patch.object(m,'API_KEY','test'):
   c=b.appmod.app.test_client()
   for endpoint,data in [('/api/chat',{'history':{}}),('/api/bot_comment',{'comments':['wrong']}),('/api/analyze_fast',{'text':[]}),('/api/analyze_enrich',{'analysis':[]})]:
    self.assertEqual(c.post(endpoint,json=data).status_code,400)
if __name__=='__main__':unittest.main(verbosity=2)
