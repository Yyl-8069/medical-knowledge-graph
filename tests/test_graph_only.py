import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'qingnang'))
from query_graph import make_query, run_query
from build_medicalgraph import MedicalGraph, main

class GraphOnlyTests(unittest.TestCase):
    def test_drug_query_is_parameterized_and_covers_both_relations(self):
        name = "a' OR 1=1"
        query, parameters = make_query('drugs', name, 20)
        self.assertIn(':command_drug|recommand_drug', query)
        self.assertNotIn(name, query)
        self.assertEqual(parameters, {'name': name, 'limit': 20})

    def test_reject_unknown_operation_and_invalid_limit(self):
        for operation, limit in [('delete', 20), ('drugs', 0), ('drugs', 1001)]:
            with self.assertRaises(ValueError):
                make_query(operation, '感冒', limit)
        with self.assertRaises(ValueError):
            make_query('drugs', '', 20)

    def test_query_returns_raw_database_rows(self):
        driver = MagicMock()
        rows = [{'disease': '感冒', 'drug': '药品甲'}]
        driver.session.return_value.__enter__.return_value.run.return_value.data.return_value = rows
        with patch('query_graph.GraphDatabase.driver', return_value=driver), patch('query_graph.get_neo4j_config', return_value={}):
            result = run_query('drugs', '感冒', 20)
        self.assertEqual(result['records'], rows)
        self.assertEqual(result['parameters']['name'], '感冒')
        driver.close.assert_called_once()

    def test_import_defaults_to_preview_without_connecting(self):
        with patch('build_medicalgraph.GraphDatabase.driver') as connect, contextlib.redirect_stdout(io.StringIO()):
            main([])
        connect.assert_not_called()

    def test_existing_duplicate_nodes_stop_before_writes(self):
        graph = MedicalGraph()
        driver = MagicMock()
        driver.__enter__.return_value = driver
        driver.session.return_value.__enter__.return_value.run.return_value.data.return_value = [{'name':'重复'}]
        with patch('build_medicalgraph.GraphDatabase.driver', return_value=driver), patch('build_medicalgraph.get_neo4j_config', return_value={}):
            with self.assertRaisesRegex(ValueError, '重复'):
                graph.create_graphnodes_and_graphrels()
        calls = driver.session.return_value.__enter__.return_value.run.call_args_list
        self.assertTrue(all('CREATE' not in call.args[0] and 'MERGE' not in call.args[0] for call in calls))

    def test_original_data_hash_and_expanded_schema(self):
        manifest = json.loads((ROOT/'docs/source_manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((ROOT/'qingnang/data/medical.json').read_bytes()).hexdigest(), manifest['files'][0]['source_sha256'])
        with contextlib.redirect_stdout(io.StringIO()):
            values = MedicalGraph().read_nodes()
        self.assertEqual([len(group) for group in values[:7]], [3828,4870,3353,54,17201,5998,8807])
        self.assertEqual(len(MedicalGraph.RELATIONS), 11)

    def test_expanded_import_includes_missing_relations(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory) / 'medical.json'
            data.write_text(json.dumps({'name':'疾病甲','symptom':['症状甲'],
                'not_eat':['食物甲'],'do_eat':['食物乙'],'recommand_eat':['食物丙'],
                'common_drug':['药品甲'],'recommand_drug':['药品甲'],
                'drug_detail':['厂家甲(药品甲)'],'check':['检查甲'],
                'cure_department':['大科室','小科室'],'acompany':['疾病甲'],
                'desc':'简介甲'},ensure_ascii=False),encoding='utf-8')
            driver = MagicMock()
            driver.__enter__.return_value = driver
            session = driver.session.return_value.__enter__.return_value
            session.run.return_value.data.return_value = []
            with patch('build_medicalgraph.GraphDatabase.driver',return_value=driver), patch('build_medicalgraph.get_neo4j_config',return_value={}), contextlib.redirect_stdout(io.StringIO()):
                MedicalGraph(data).create_graphnodes_and_graphrels()
            calls = session.run.call_args_list
            edges = [c for c in calls if 'edges' in c.kwargs]
            self.assertEqual(len(edges),11)
            self.assertTrue(any('a:Producer' in c.args[0] and c.kwargs['edges']==[['厂家甲','药品甲']] for c in edges))
            self.assertTrue(any('a:Department' in c.args[0] and c.kwargs['edges']==[['小科室','大科室']] for c in edges))
            self.assertEqual({c.kwargs['title'] for c in edges if 'b:Food' in c.args[0]}, {'recommand_eat','no_eat','do_eat'})
            self.assertEqual(next(i for i,c in enumerate(calls) if 'CREATE' in c.args[0]),7)


class CompletionTests(unittest.TestCase):
    def test_completion_preserves_duplicate_nodes_and_uses_canonical_endpoints(self):
        graph=MedicalGraph()
        values=tuple([{'疾病甲'}]*7)+([{'name':'疾病甲'}],)+tuple([[['疾病甲','疾病甲']]]*11)
        driver=MagicMock();driver.__enter__.return_value=driver
        session=driver.session.return_value.__enter__.return_value
        session.run.return_value.data.return_value=[{'name':'重复','total':2}]
        with patch.object(graph,'read_nodes',return_value=values),patch('build_medicalgraph.GraphDatabase.driver',return_value=driver),patch('build_medicalgraph.get_neo4j_config',return_value={}),contextlib.redirect_stdout(io.StringIO()):
            graph.create_graphnodes_and_graphrels(complete_existing=True)
        queries=[c.args[0] for c in session.run.call_args_list]
        self.assertTrue(all('DELETE' not in q and 'CREATE CONSTRAINT' not in q for q in queries))
        edges=[c.args[0] for c in session.run.call_args_list if 'edges' in c.kwargs]
        self.assertEqual(len(edges),11)
        self.assertTrue(all('elementId(a)' in q and 'elementId(b)' in q for q in edges))


class CoverageTests(unittest.TestCase):
    def test_verification_detects_missing_candidate(self):
        from verify_graph import verify_graph
        graph=MedicalGraph()
        values=tuple([{'实体甲'}]*7)+([{'name':'实体甲'}],)+tuple([[['实体甲','实体甲']]]*11)
        driver=MagicMock();driver.__enter__.return_value=driver
        session=driver.session.return_value.__enter__.return_value
        session.run.return_value.single.side_effect=[{'missing':1}]+[{'missing':0}]*17
        with patch.object(graph,'read_nodes',return_value=values),patch('verify_graph.GraphDatabase.driver',return_value=driver),patch('verify_graph.get_neo4j_config',return_value={}):
            report=verify_graph(graph)
        self.assertFalse(report['complete'])
        self.assertEqual(report['nodes'][0]['missing'],1)
        self.assertEqual(len(report['relations']),11)
        self.assertTrue(all('MERGE' not in c.args[0] and 'DELETE' not in c.args[0] for c in session.run.call_args_list))


if __name__ == '__main__':
    unittest.main()
