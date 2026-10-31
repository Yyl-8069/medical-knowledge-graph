import os


def get_neo4j_config():
    password = os.environ.get('NEO4J_PASSWORD')
    if not password:
        raise ValueError('请设置环境变量 NEO4J_PASSWORD')
    return {
        'uri': os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
        'auth': (os.environ.get('NEO4J_USER', 'neo4j'), password),
    }
