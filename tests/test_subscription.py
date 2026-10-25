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
