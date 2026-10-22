from pathlib import Path
import re, unittest
root=Path(__file__).resolve().parents[1]
class Release(unittest.TestCase):
 def test_public_assets(self):
  html=(root/'public/index.html').read_text()
  for asset in ('style.css','demo.js','product.pptx'):self.assertTrue((root/'public'/asset).is_file())
  self.assertNotIn('<script>',html)
  js=(root/'public/demo.js').read_text()
  for bad in ('fetch(', 'localStorage', 'innerHTML', 'ADMIN_TOKEN', 'LLM_API_KEY'):self.assertNotIn(bad,js)
 def test_deployment_boundaries(self):
  compose=(root/'compose.yaml').read_text()
  self.assertIn('127.0.0.1:8010:8000',compose)
  self.assertNotIn('proxy_pass',(root/'deploy/nginx-location.conf').read_text())
 def test_no_runtime_data(self):
  self.assertFalse((root/'.env').exists())
  for p in (root/'public').rglob('*'):self.assertNotIn(p.suffix,('.db','.sqlite','.env'))
if __name__=='__main__':unittest.main()
