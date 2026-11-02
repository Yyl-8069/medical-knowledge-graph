import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch, MagicMock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qingnang'))
from grounded_answer import answer_question, request_answer

class GroundedAnswerTests(unittest.TestCase):
    def test_empty_retrieval_does_not_call_model(self):
        with patch('grounded_answer.run_query',return_value={'records':[]}), patch('grounded_answer.request_answer') as api:
            result=answer_question('感冒吃什么','foods','感冒')
        self.assertIn('未检索到',result['answer'])
        api.assert_not_called()

    def test_answer_includes_evidence_and_api_gets_only_retrieved_rows(self):
        retrieval={'records':[{'disease':'感冒','drug':'药甲'}],'cypher':'MATCH ...','parameters':{'name':'感冒'}}
        with patch('grounded_answer.run_query',return_value=retrieval), patch('grounded_answer.request_answer',return_value='药品记录包含药甲。') as api:
            result=answer_question('感冒药品有哪些','drugs','感冒')
        self.assertEqual(result['retrieval'],retrieval)
        self.assertEqual(api.call_args.args[1],retrieval)
        self.assertIn('药甲',result['answer'])

    def test_api_serializes_evidence_and_uses_configured_endpoint(self):
        response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps({'choices':[{'message':{'content':'记录回答'}}]}).encode()
        config={'LLM_BASE_URL':'https://example.com/v1','LLM_MODEL':'test-model','LLM_API_KEY':'unit-test-key'}
        with patch.dict(os.environ,config,clear=True), patch('grounded_answer.urlopen',return_value=response) as send:
            self.assertEqual(request_answer('问题',{'records':[{'drug':'药甲'}]}),'记录回答')
        req=send.call_args.args[0]
        self.assertEqual(req.full_url,'https://example.com/v1/chat/completions')
        payload=json.loads(req.data)
        self.assertIn('药甲',payload['messages'][1]['content'])
        self.assertNotIn('unit-test-key',payload['messages'][1]['content'])
        self.assertEqual(send.call_args.kwargs['timeout'],60)

    def test_missing_config_does_not_send_request(self):
        with patch.dict(os.environ,{},clear=True),patch('grounded_answer.urlopen') as send:
            with self.assertRaises(ValueError):request_answer('问题',{'records':[{}]})
        send.assert_not_called()
