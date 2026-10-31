import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def run_version(version, script):
    code = "import sys;sys.path.insert(0," + repr(str(ROOT / 'versions' / version)) + ");" + script
    result = subprocess.run([sys.executable, '-c', code], cwd=str(ROOT),
                            env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    if result.returncode:
        raise AssertionError(result.stdout)
    return result.stdout

class VersionTests(unittest.TestCase):
    def test_v11_extended_queries_and_parameters(self):
        run_version('v1.1', """
from question_classifier import QuestionClassifier
from question_parser import QuestionParser
c,p=QuestionClassifier(),QuestionParser()
for question,expected in [('感冒不能吃什么','disease_not_food'),('感冒的原因是什么','disease_cause'),('感冒属于什么科','disease_belong'),('咳嗽','symptom_disease')]:
    queries=p.parser_main(c.classify(question))
    assert expected in [q['question_type'] for q in queries], (question,queries)
q=p.sql_transfer('disease_drug',["a' OR 1=1"])
assert len(q)==2
assert all("a' OR 1=1" not in item['query'] and item['parameters']['name']=="a' OR 1=1" for item in q)
assert p.parser_main({})==[]
""")

    def test_v20_intent_routing_without_model_inference(self):
        run_version('v2.0', """
from unittest.mock import MagicMock,patch
for name in ['torch','numpy','onnxruntime']:
    sys.modules[name]=MagicMock()
from question_classifier_19 import QuestionClassifier
from question_parser import QuestionParser
with patch.object(QuestionClassifier,'init_bert'):
    c=QuestionClassifier()
for index,expected in [(0,'disease_drug'),(2,'disease_not_food'),(8,'disease_check'),(18,'disease_belong')]:
    with patch.object(c,'question_class',return_value=index) as infer:
        result=c.classify('感冒')
        queries=QuestionParser().parser_main(result)
        assert expected in [q['question_type'] for q in queries],(index,queries)
        assert infer.call_count==1
""")

    def test_version_data_and_training_labels(self):
        manifest=json.loads((ROOT/'docs/version_source_manifest.json').read_text(encoding='utf-8'))
        for item in manifest['files']:
            if '/dict/' in item['project_file'] or '/project_data' in item['project_file'] or item['project_file'].endswith('vocab.txt'):
                self.assertEqual(hashlib.sha256((ROOT/item['project_file']).read_bytes()).hexdigest(),item['source_sha256'])
        for dataset,classes,counts in [('project_data',4,[32000,4000,4000]),('project_data_19',19,[15200,1900,1900])]:
            folder=ROOT/'versions/v2.0/bert'/dataset
            self.assertEqual(len((folder/'class.txt').read_text(encoding='utf-8').splitlines()),classes)
            for split,expected in zip(['train','dev','test'],counts):
                rows=[line for line in (folder/(split+'.txt')).read_text(encoding='utf-8').splitlines() if line.strip()]
                self.assertEqual(len(rows),expected)
                for row in rows:
                    question,label=row.rsplit('\t',1)
                    self.assertTrue(question)
                    self.assertTrue(0<=int(label)<classes)

    def test_asset_restore_prevents_overwrite_and_escape(self):
        path=ROOT/'versions/v2.0/prepare_model_assets.py'
        spec=importlib.util.spec_from_file_location('asset_restore',str(path))
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            source=base/'source';project=base/'project'
            source.mkdir();project.mkdir()
            (source/'model.pt').write_bytes(b'small test fixture')
            items=[{'source_file':'model.pt','target_file':'models/model.pt','sha256':module.sha256(source/'model.pt')}]
            module.restore(source,project,items)
            self.assertEqual((project/'models/model.pt').read_bytes(),b'small test fixture')
            (project/'models/model.pt').write_bytes(b'user change')
            with self.assertRaises(FileExistsError): module.restore(source,project,items)
            items[0]['target_file']='../outside.pt'
            with self.assertRaises(ValueError): module.restore(source,project,items)

    def test_v11_importer_schema_and_parameter_values(self):
        run_version('v1.1', """
import os
os.environ['NEO4J_PASSWORD']='test-only'
from unittest.mock import patch
from build_medicalgraph import MedicalGrapg
name="sample'entity"
values=[{name} for _ in range(7)]+[[{'name':name,'cured_prob':'未知'}]]+[[[name,name]] for _ in range(11)]
with patch.object(MedicalGrapg,'read_nodes',return_value=values), patch('build_medicalgraph.GraphDatabase.driver') as factory:
    MedicalGrapg().create_graphnodes_and_graphrels()
    session=factory.return_value.__enter__.return_value.session.return_value.__enter__.return_value
    calls=session.run.call_args_list
    edges=[call for call in calls if 'edges' in call.kwargs]
    assert len(edges)==11
    assert any('a:Producer' in call.args[0] and 'b:Drug' in call.args[0] for call in edges)
    assert any('a:Department' in call.args[0] and 'b:Department' in call.args[0] for call in edges)
    assert all(name not in call.args[0] for call in calls)
    assert all('MERGE' in call.args[0] for call in edges)
""")
