import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PackagingTests(unittest.TestCase):
 def test_marketplace_paths_and_manifests(self):
  market=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text())
  self.assertEqual(market,json.loads((ROOT/'.claude-plugin/marketplace.json').read_text()))
  for entry in market['plugins']:
   plugin=(ROOT/entry['source']['path']).resolve()
   self.assertTrue(plugin.is_relative_to(ROOT))
   portable=json.loads((plugin/'plugin.json').read_text())
   overlay=json.loads((plugin/'.codex-plugin/plugin.json').read_text())
   self.assertEqual(entry['name'],portable['name']);self.assertEqual(overlay['name'],portable['name'])
   self.assertTrue((plugin/overlay['skills']/'claude-bridge/SKILL.md').is_file())
 def test_standalone_and_plugin_skills_match(self):
  source=ROOT/'claude-bridge';dest=ROOT/'plugins/claude-bridge/skills/claude-bridge'
  for p in source.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:
    self.assertEqual(p.read_bytes(),(dest/p.relative_to(source)).read_bytes(),str(p))
if __name__=='__main__':unittest.main()
