import os,tempfile,unittest
import core
from adapters import telegram_update,email_message
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();core.DB=self.temp.name+'/db.sqlite'
 def tearDown(self):self.temp.cleanup()
 def test_three_sources_and_replay(self):
  a=core.ingest('form','a','user@example.org','Нужен сайт')
  self.assertEqual(a,core.ingest('form','a','user@example.org','Нужен сайт'))
  telegram_update({'update_id':1,'message':{'chat':{'id':42,'type':'private'},'text':'Нужен сайт'}})
  email_message(b'From: client@example.org\nSubject: Request\n\nHello','mail:1')
  for _ in range(3):self.assertTrue(core.process_one())
  with core.connect() as c:
   rows=c.execute('SELECT * FROM leads').fetchall()
   self.assertEqual(len(rows),3);self.assertTrue(all(r['status']=='review' for r in rows))
 def test_conflicting_id(self):
  core.ingest('form','a','x','one')
  with self.assertRaises(ValueError):core.ingest('form','a','x','two')
 def test_failure_and_manual(self):
  core.ingest('form','a','x','one')
  def fail(row):raise TimeoutError()
  for _ in range(3):
   core.process_one(fail)
   with core.connect() as c:c.execute('UPDATE leads SET due=0')
  with core.connect() as c:self.assertEqual(c.execute('SELECT status FROM leads').fetchone()[0],'manual')
 def test_recover_interrupted_work(self):
  core.ingest('form','a','x','one')
  with core.connect() as c:c.execute("UPDATE leads SET status='processing',updated=0")
  self.assertTrue(core.process_one())
 def test_cursor_persisted(self):
  core.cursor('telegram',123);self.assertEqual(core.cursor('telegram'),'123')
if __name__=='__main__':unittest.main()
