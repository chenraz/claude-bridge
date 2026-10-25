import argparse, importlib.util, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bridge',ROOT/'claude-bridge/scripts/bridge.py'); b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.p=Path(self.temp.name);self.project=self.p/'app';self.project.mkdir();self.env=self.p/'.env';self.env.write_text('ANTHROPIC_API_KEY=test-secret\n');self.task=self.p/'task.txt';self.task.write_text('Make an app');self.args=argparse.Namespace(backend='api',env_file=self.env,state_dir=self.p/'sessions',project=self.project,session='main',prompt_file=self.task,context_file=[],max_tokens=4096)
 def tearDown(self):self.temp.cleanup()
 def test_history_and_project_isolation(self):
  seen=[]
  def api(c,m,t):
   seen.append(m);return {'content':[{'type':'text','text':'Create index.html'}],'stop_reason':'end_turn','usage':{'input_tokens':10,'output_tokens':5}}
  with patch.object(b,'api_call',side_effect=api):
   self.assertTrue(b.ask(self.args)['ok']);b.ask(self.args)
   self.assertEqual(len(seen[1]),3)
   other=self.p/'other';other.mkdir();self.args.project=other;b.ask(self.args);self.assertEqual(len(seen[2]),1)
  self.assertEqual(list(self.project.iterdir()),[])
 def test_failure_not_saved_and_lock_released(self):
  with patch.object(b,'api_call',side_effect=b.BridgeError('offline')):
   with self.assertRaises(b.BridgeError): b.ask(self.args)
  self.assertFalse(list(self.args.state_dir.rglob('*.json')));self.assertFalse(list(self.args.state_dir.rglob('*.lock')))
 def test_secret_and_outside_context_blocked(self):
  secret=self.project/'.env';secret.write_text('secret')
  outside=self.p/'outside.txt';outside.write_text('secret')
  link=self.project/'escape.txt';link.symlink_to(outside)
  for file in (secret,outside,link):
   with self.assertRaises(b.BridgeError): b.make_prompt('task',[str(file)],self.project,self.env)
 def test_only_explicit_context(self):
  f=self.project/'code.js';f.write_text('const a = 1;')
  (self.project/'not-selected.txt').write_text('do not send')
  text=b.make_prompt('task',[str(f)],self.project,self.env)
  self.assertIn('const a = 1',text);self.assertNotIn('do not send',text)
 def test_status_never_prints_token(self):
  r=subprocess.run([sys.executable,str(ROOT/'claude-bridge/scripts/bridge.py'),'--backend','api','--env-file',str(self.env),'status'],capture_output=True,text=True)
  self.assertEqual(r.returncode,0);self.assertTrue(json.loads(r.stdout)['configured']);self.assertNotIn('test-secret',r.stdout+r.stderr)
 def test_init_config_creates_private_file_and_preserves_key(self):
  new=self.p/'config'/'.env';self.assertTrue(b.init_config(new)['created'])
  self.assertIn('PASTE_YOUR_KEY_HERE',new.read_text())
  if os.name!='nt':self.assertEqual(new.stat().st_mode & 0o777,0o600)
  new.write_text('PRIVATE_EXISTING_KEY');self.assertFalse(b.init_config(new)['created'])
  self.assertEqual(new.read_text(),'PRIVATE_EXISTING_KEY')
 def test_one_request_no_tools(self):
  class Response:
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self):return b'{"content":[{"type":"text","text":"ok"}]}'
  with patch.object(b.urllib.request,'urlopen',return_value=Response()) as fetch:
   b.api_call({'ANTHROPIC_API_KEY':'fake'},[{'role':'user','content':'hi'}],4096)
   self.assertEqual(fetch.call_count,1);req=fetch.call_args[0][0];body=json.loads(req.data);self.assertNotIn('tools',body);self.assertNotIn('fake',req.full_url)
if __name__ == '__main__': unittest.main()
