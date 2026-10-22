import os,tempfile,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import core
from app import app
class ApiTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();core.DB=self.temp.name+'/db'
  self.env=patch.dict(os.environ,{'ADMIN_TOKEN':'a'*40,'INGEST_TOKEN':'i'*40,'AI_MODE':'demo'});self.env.start()
  self.client=TestClient(app);self.admin={'Authorization':'Bearer '+'a'*40};self.ingest={'Authorization':'Bearer '+'i'*40}
 def tearDown(self):self.env.stop();self.temp.cleanup()
 def test_token_separation(self):
  payload={'external_id':'1','contact':'test@example.org','text':'Пример заявки'}
  self.assertEqual(self.client.get('/api/leads').status_code,401)
  self.assertEqual(self.client.get('/api/leads',headers=self.ingest).status_code,401)
  self.assertEqual(self.client.post('/api/form',json=payload,headers=self.admin).status_code,401)
  r=self.client.post('/api/form',json=payload,headers=self.ingest);self.assertEqual(r.status_code,200)
  ident=r.json()['id'];self.assertEqual(self.client.post('/api/form',json=payload,headers=self.ingest).json()['id'],ident)
  self.assertEqual(self.client.post('/api/leads/'+ident+'/approve',headers=self.admin).status_code,409)
  core.process_one()
  self.assertFalse(self.client.post('/api/leads/'+ident+'/approve',headers=self.admin).json()['sent'])
  self.assertEqual(len(self.client.get('/api/leads/'+ident+'/events',headers=self.admin).json()),3)
 def test_hidden_docs_and_limits(self):
  self.assertEqual(self.client.get('/docs').status_code,404)
  self.assertEqual(self.client.post('/api/form',json={'external_id':'x','contact':'x','text':'a'*20001},headers=self.ingest).status_code,422)
