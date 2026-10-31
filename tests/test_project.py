import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / 'red_spider'
sys.path.insert(0, str(CODE))

from build_medicalgraph import MedicalGraph
from question_classifier import QuestionClassifier
from question_parser import QuestionPaser
from answer_search import AnswerSearcher
from config import get_neo4j_config


class ProjectTests(unittest.TestCase):
    def test_data_and_dictionaries_unchanged(self):
        manifest = json.loads((ROOT / 'docs/source_manifest.json').read_text(encoding='utf-8'))
        for entry in manifest['files']:
            if entry['file'].startswith(('data/', 'dict/')):
                self.assertEqual(hashlib.sha256((CODE / entry['file']).read_bytes()).hexdigest(), entry['source_sha256'])
        rows = [json.loads(line) for line in (CODE / 'data/medical.json').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(len(rows), 8808)
        self.assertEqual(len({row['name'] for row in rows}), 8807)

    def test_classification_and_parameterized_queries(self):
        classifier = QuestionClassifier()
        parser = QuestionPaser()
        for question, expected in [('感冒有什么症状', 'disease_symptom'), ('感冒吃什么', 'disease_food'), ('感冒用什么药', 'disease_drug')]:
            queries = parser.parser_main(classifier.classify(question))
            self.assertIn(expected, [q['question_type'] for q in queries])
        name = "a' OR 1=1"
        query = parser.sql_transfer('disease_symptom', [name])[0]
        self.assertNotIn(name, query['query'])
        self.assertEqual(query['parameters'], {'name': name})
        self.assertEqual(parser.parser_main(classifier.classify('hello')), [])

    def test_search_handles_multiple_types_and_empty_queries(self):
        searcher = AnswerSearcher.__new__(AnswerSearcher)
        searcher.num_limit = 10
        searcher.driver = MagicMock()
        session = searcher.driver.session.return_value.__enter__.return_value
        session.run.return_value.data.side_effect = [
            [{'m.name': '感冒', 'n.name': '咳嗽'}],
            [{'m.name': '感冒', 'n.name': '粥'}],
        ]
        queries = QuestionPaser().parser_main({'args': {'感冒': ['disease']}, 'question_types': ['disease_symptom', 'disease_food']})
        self.assertEqual(len(searcher.search_main(queries)), 2)
        self.assertEqual(session.run.call_count, 2)
        self.assertEqual(searcher.search_main([]), [])

    def test_graph_import_parameters_and_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'medical.json'
            data.write_text(json.dumps({'name': "疾病'", 'symptom': ['咳嗽', '咳嗽'], 'recommand_eat': ['粥'], 'recommand_drug': ['药']}, ensure_ascii=False), encoding='utf-8')
            graph = MedicalGraph(data)
            with patch('build_medicalgraph.GraphDatabase.driver') as factory, patch.dict(os.environ, {'NEO4J_PASSWORD': 'test-only'}):
                graph.create_graphnodes_and_graphrels()
                session = factory.return_value.__enter__.return_value.session.return_value.__enter__.return_value
                calls = session.run.call_args_list
                edge_calls = [call for call in calls if 'edges' in call.kwargs]
                self.assertEqual(len(edge_calls), 3)
                self.assertTrue(all('MERGE' in call.args[0] for call in edge_calls))
                self.assertEqual(edge_calls[-1].kwargs['edges'], [["疾病'", '咳嗽']])
                self.assertTrue(all("疾病'" not in call.args[0] for call in calls))

    def test_missing_password(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'NEO4J_PASSWORD'):
                get_neo4j_config()


if __name__ == '__main__':
    unittest.main()
