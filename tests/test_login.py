import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'claude-bridge/scripts/bridge.py'
spec=importlib.util.spec_from_file_location('login_bridge',p);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class LoginTests(unittest.TestCase):
 def test_valid_login_never_restarts(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(b,'subscription_status',return_value={'installed':True,'configured':True}),patch.object(b.subprocess,'Popen') as start:
   self.assertTrue(b.ensure_login(Path(tmp))['configured']);start.assert_not_called();self.assertFalse((Path(tmp)/'_login').exists())
 def test_signed_out_launches_once_and_no_credentials_in_state(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(b,'subscription_status',return_value={'installed':True,'configured':False,'reason_code':'login_required'}),patch.object(b.subprocess,'Popen') as start:
   first=b.ensure_login(Path(tmp));second=b.ensure_login(Path(tmp));self.assertTrue(first['login_started']);self.assertFalse(second['login_started']);self.assertEqual(start.call_count,1)
   command=start.call_args[0][0];self.assertEqual(command[-1],'_login-worker');self.assertFalse(start.call_args.kwargs['shell'])
   state=json.loads((Path(tmp)/'_login/attempt.json').read_text());self.assertEqual(set(state),{'started_at','phase'})
 def test_overrides_or_wrong_account_do_not_launch(self):
  for code in ['install_required','auth_override','account_mismatch','status_unavailable']:
   with tempfile.TemporaryDirectory() as tmp,patch.object(b,'subscription_status',return_value={'configured':False,'reason_code':code}),patch.object(b.subprocess,'Popen') as start:
    self.assertFalse(b.ensure_login(Path(tmp))['ok']);start.assert_not_called()
 def test_worker_calls_official_subscription_login_and_filters_output(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(b,'subscription_status',side_effect=[{'configured':False,'reason_code':'login_required'},{'configured':True}]),patch.object(b.shutil,'which',return_value='/official/claude'),patch.object(b.subprocess,'run',return_value=subprocess.CompletedProcess([],0)) as run:
   result=b.login_worker(Path(tmp));self.assertTrue(result['configured']);self.assertEqual(run.call_args[0][0],['/official/claude','auth','login','--claudeai']);self.assertEqual(run.call_args.kwargs['stdout'],subprocess.DEVNULL);self.assertEqual(run.call_args.kwargs['timeout'],300)
 def test_launch_failure_allows_retry(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(b,'subscription_status',return_value={'configured':False,'reason_code':'login_required'}),patch.object(b.subprocess,'Popen',side_effect=OSError):
   with self.assertRaises(b.BridgeError):b.ensure_login(Path(tmp))
   self.assertFalse((Path(tmp)/'_login/launch.lock').exists());self.assertFalse((Path(tmp)/'_login/attempt.json').exists())
if __name__=='__main__':unittest.main()
