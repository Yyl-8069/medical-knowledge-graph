"""固定问句冒烟评估：真实分类器与解析器，不连接数据库。"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'red_spider'))
from question_classifier import QuestionClassifier
from question_parser import QuestionPaser


def main():
    cases = json.loads((ROOT / 'tests/evaluation_cases.json').read_text(encoding='utf-8'))
    assert cases and len({case['id'] for case in cases}) == len(cases), 'Empty or duplicate cases'
    classifier, parser = QuestionClassifier(), QuestionPaser()
    results = []
    for case in cases:
        assert set(case['expected_types']) <= set(parser.RELATIONS), 'Unknown expected intent'
        classification = classifier.classify(case['question'])
        queries = parser.parser_main(classification)
        actual = sorted({query['question_type'] for query in queries})
        passed = actual == sorted(set(case['expected_types']))
        results.append(dict(case, actual_types=actual, passed=passed))
        print('{} {} | {} | {}'.format('PASS' if passed else 'FAIL', case['id'], case['question'], actual))
    passed = sum(result['passed'] for result in results)
    report = {'metric': 'query_intent_set_exact_match', 'scope': '12 manually selected smoke cases; no database or answer correctness evaluation',
              'passed': passed, 'total': len(results), 'ratio': passed / len(results), 'results': results}
    output = ROOT / 'docs/evaluation_results.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Exact match: {}/{} ({:.1%})'.format(passed, len(results), report['ratio']))
    print('Neo4j integration and answer correctness: NOT RUN')


if __name__ == '__main__':
    main()
