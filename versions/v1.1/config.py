import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEDICAL_DATA_PATH = Path(os.environ.get('MEDICAL_DATA_PATH', str(PROJECT_ROOT / 'red_spider/data/medical.json')))
NEO4J_CONFIG = {
    'uri': os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
    'auth': (os.environ.get('NEO4J_USER', 'neo4j'), os.environ.get('NEO4J_PASSWORD', '')),
}
