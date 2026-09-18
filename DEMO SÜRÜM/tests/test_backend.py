import unittest,sys,copy,random,json,tempfile
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import run_v16_web as m
import app_v16_2 as appmod
appmod.app.logger.disabled=True

def analysis(**kwargs):
 a={k:False for k,v in m.CORE_PROPERTIES.items() if v.get('type')=='boolean'}
 a.update(intent_distribution={k:(70 if k=='Soru' else 5) for k in m.INTENTS},reason='Controlled fixture',is_clear=True,is_respectful=True)
 a.update(kwargs);return a
class Checks(unittest.TestCase):
 def setUp(self):
  m._FAST_CACHE.clear();m._ENRICH_CACHE.clear();m._RAW_CACHE.clear();m._BEHAVIOR_CACHE.clear()
 def test_calibration_math(self):
  rng=random.Random(42)
  for i in range(1000):
   d={k:rng.random()*100 for k in m.INTENTS};a=m.decision_layer({'intent_distribution':d},m.INTENTS[i%7]);v=a['intent_distribution'];self.assertAlmostEqual(sum(v.values()),100);self.assertGreaterEqual(min(v.values()),0);dl=a['decision_layer'];self.assertAlmostEqual(dl['intent_match']+dl['misunderstanding_risk'],100)
 def test_blind_inference(self):
  with patch.object(m,'call_responses',side_effect=lambda *a:analysis()) as call:
   x=m.analyze_fast('Bu uygulama ne zaman açılıyor?','same','Soru');y=m.analyze_fast('Bu uygulama ne zaman açılıyor?','same','Eleştiri')
   self.assertEqual(call.call_count,1);self.assertEqual(x['intent_distribution'],y['intent_distribution'])
 def test_scope(self):
  with patch.object(m,'call_responses',side_effect=AssertionError('must not call')):
   self.assertIsNone(m.analyze_fast('Selam','','Soru')['decision_layer']['intent_match'])
 def test_invalid_distribution(self):
  for d in [{},{k:0 for k in m.INTENTS},{k:float('nan') for k in m.INTENTS}]:
   with self.assertRaises(ValueError):m.calibrate_distribution(d)
 def test_bad_coefficients(self):
  cases=[m.DEFAULT_CALIBRATION.copy()]
  for field,val in [('intercepts',[float('nan')]*7),('output_categories',['Soru']*7),('matrix_output_by_feature',[[1]*14]*7)]:
   p=copy.deepcopy(m.CALIBRATION);p['coefficients'][field]=val;cases.append(p)
  for p in cases:
   with patch.object(m,'CALIBRATION',p):
    self.assertFalse(m.calibration_available());self.assertEqual(m.calibration_meta()['status'],'unavailable')
    with self.assertRaises(RuntimeError):m.calibrate_distribution(analysis()['intent_distribution'])
 def test_missing_and_broken_profile(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d,patch.object(m,'ROOT',Path(d)):
   self.assertFalse(m.calibration_available(m.load_calibration()))
   (Path(d)/'calibration_profile.json').write_text('{broken',encoding='utf-8')
   self.assertFalse(m.calibration_available(m.load_calibration()))
 def test_enrich_base_cache(self):
  a=m.decision_layer(analysis(),'Soru');b=copy.deepcopy(a);b['decision_layer']['selected_share']=10
  with patch.object(m,'attach_v13_analysis',side_effect=lambda original,*args:original) as call:
   m.enrich_analysis(a,'text','Soru','ctx');m.enrich_analysis(b,'text','Soru','ctx');m.enrich_analysis(b,'text','Soru','ctx');self.assertEqual(call.call_count,2)
 def test_verified_suggestions(self):
  a=m.decision_layer(analysis(),'Soru')
  with patch.object(m,'call_responses',return_value={'candidates':[{'text':'Bu doğru mu?','change':'fixture'}]}),patch.object(m,'evaluate_variants',return_value={}):
   out=m.attach_v13_analysis(a,'Bu gerçekten doğru mu?','Soru','ctx');self.assertEqual(out['interventions'],[])
 def test_http_analysis(self):
  with patch.object(m,'API_KEY','dummy'),patch.object(m,'call_responses',side_effect=lambda *args:analysis()):
   c=appmod.app.test_client()
   for txt in ['Mal ve hizmet satın aldım.','Ben aptal değilim.','Bana salak dedi; bunu kabul etmiyorum.']:
    r=c.post('/api/analyze_fast',json={'text':txt,'selected_intent':'Bilgilendirme','context':'new post'});self.assertEqual(r.status_code,200);self.assertTrue(r.json['analysis']['api_primary_analysis'])
 def test_http_no_calibration(self):
  with patch.object(m,'CALIBRATION',m.DEFAULT_CALIBRATION.copy()),patch.object(m,'call_responses',side_effect=AssertionError('must not call')):
   r=appmod.app.test_client().post('/api/analyze_fast',json={'text':'a'});self.assertEqual(r.status_code,503);self.assertEqual(r.json['calibration']['status'],'unavailable')
 def test_http_interactions(self):
  fixture={'reply':'Sakin konuşalım.','user_analysis':analysis(has_personal_attack=True,is_respectful=False),'reply_analysis':analysis(is_calming=True)}
  with patch.object(m,'API_KEY','dummy'),patch.object(m,'call_responses',side_effect=lambda *args:copy.deepcopy(fixture)):
   c=appmod.app.test_client()
   for path,payload,key in [('/api/chat',{'person_id':'sila','history':[{'from':'me','text':'sen sorunlusun tamamen'}]},'analysis'),('/api/bot_comment',{'person_id':'sila','user_comment':'sen sorunlusun tamamen'},'user_analysis')]:
    r=c.post(path,json=payload);self.assertEqual(r.status_code,200);self.assertTrue(r.json[key]['has_personal_attack']);self.assertFalse(r.json['reply_analysis']['has_personal_attack'])
 def test_http_failure_and_invalid(self):
  with patch.object(m,'API_KEY','dummy'),patch.object(m,'call_responses',side_effect=RuntimeError('simulated failure')):
   c=appmod.app.test_client()
   self.assertEqual(c.post('/api/chat',json={'person_id':'sila'}).status_code,503)
   self.assertEqual(c.post('/api/bot_comment',json={'person_id':'sila'}).status_code,503)
   self.assertEqual(c.post('/api/chat',json={'person_id':'unknown'}).status_code,400)
 def test_static_page(self):
  self.assertEqual(appmod.app.test_client().get('/').status_code,200)
if __name__=='__main__':unittest.main(verbosity=1)
