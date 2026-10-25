import importlib.util,json,os,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'claude-bridge/scripts/bridge.py'
spec=importlib.util.spec_from_file_location('subscription_bridge',p);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class SubscriptionTests(unittest.TestCase):
 def test_status_filters_sensitive_metadata(self):
  response=subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True,'authMethod':'claude.ai','subscriptionType':'max','email':'private@example.com','accessToken':'DO_NOT_PRINT'}),'')
  with patch.dict(os.environ,{},clear=True),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=response):
   status=b.subscription_status();self.assertTrue(status['configured']);self.assertNotIn('private',json.dumps(status));self.assertNotIn('DO_NOT_PRINT',json.dumps(status))
 def test_provider_override_blocks_subscription(self):
  with patch.dict(os.environ,{'ANTHROPIC_API_KEY':'FAKE_SECRET'},clear=True),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run') as process:
   status=b.subscription_status();self.assertFalse(status['configured']);process.assert_not_called();self.assertNotIn('FAKE_SECRET',json.dumps(status))
 def test_console_login_not_accepted_as_subscription(self):
  response=subprocess.CompletedProcess([],0,json.dumps({'loggedIn':True,'authMethod':'api_key'}),'')
  with patch.dict(os.environ,{},clear=True),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=response):
   self.assertFalse(b.subscription_status()['configured'])
 def test_official_cli_uses_stdin_and_no_tools_or_bare(self):
  response=subprocess.CompletedProcess([],0,json.dumps({'result':'done','is_error':False,'usage':{}}),'')
  with patch.object(b,'subscription_status',return_value={'configured':True}),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=response) as run:
   result=b.subscription_call([{'role':'user','content':'PRIVATE_TASK'}]);self.assertEqual(result['content'][0]['text'],'done')
   command=run.call_args[0][0];self.assertIn('--safe-mode',command);self.assertNotIn('--bare',command);self.assertNotIn('--dangerously-skip-permissions',command);self.assertEqual(command[command.index('--tools')+1],'');self.assertNotIn('PRIVATE_TASK',command);self.assertIn('PRIVATE_TASK',run.call_args.kwargs['input']);self.assertFalse(run.call_args.kwargs['shell'])
 def test_quota_error_does_not_fall_back(self):
  response=subprocess.CompletedProcess([],1,json.dumps({'is_error':True,'result':'limit reached'}),'')
  with patch.object(b,'subscription_status',return_value={'configured':True}),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=response),patch.object(b,'api_call') as api:
   with self.assertRaises(b.BridgeError):b.subscription_call([])
   api.assert_not_called()
if __name__=='__main__':unittest.main()

class NativeSessionTests(unittest.TestCase):
 def test_first_call_saves_named_session_and_resume_sends_only_new_turn(self):
  session_id='11111111-1111-4111-8111-111111111111'
  response=subprocess.CompletedProcess([],0,json.dumps({'result':'done','is_error':False}),'')
  messages=[{'role':'user','content':'older task'},{'role':'assistant','content':'older result'},{'role':'user','content':'new task'}]
  with patch.object(b,'subscription_status',return_value={'configured':True}),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=response) as run,patch.dict(os.environ,{},clear=True):
   first=b.subscription_call(messages,project=Path.cwd(),session_name='main')
   command=run.call_args[0][0];self.assertIn('--session-id',command);self.assertIn('--name',command);self.assertNotIn('--no-session-persistence',command);self.assertIn('older task',run.call_args.kwargs['input'])
   self.assertTrue(first['native_session_id'])
   b.subscription_call(messages,project=Path.cwd(),native_session_id=session_id)
   command=run.call_args[0][0];self.assertIn('--resume',command);self.assertNotIn('--session-id',command);self.assertEqual(run.call_args.kwargs['input'],'new task')
 def test_session_info_reveals_metadata_only(self):
  import argparse,tempfile
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);args=argparse.Namespace(project=root,session='main',state_dir=root/'state')
   project,path=b.session_path(args);b.atomic_json(path,{'native_session_id':'11111111-1111-4111-8111-111111111111','messages':[{'role':'user','content':'PRIVATE_CONVERSATION'}]})
   info=b.session_info(args);self.assertIn('--resume',info['resume_command']);self.assertNotIn('PRIVATE_CONVERSATION',json.dumps(info))
 def test_disabled_history_is_not_silently_accepted(self):
  with patch.object(b,'subscription_status',return_value={'configured':True}),patch.dict(os.environ,{'CLAUDE_CODE_SKIP_PROMPT_HISTORY':'1'}):
   with self.assertRaises(b.BridgeError):b.subscription_call([])
