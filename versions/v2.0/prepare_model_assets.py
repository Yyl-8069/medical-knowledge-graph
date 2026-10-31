"""从已有本地工程恢复模型文件；不下载、不覆盖不同内容的文件。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def restore(source, project_root, assets):
    source = source.resolve()
    project_root = project_root.resolve()
    jobs = []
    for entry in assets:
        src = (source / entry['source_file']).resolve()
        dst = (project_root / entry['target_file']).resolve()
        if source.resolve() not in src.parents or project_root.resolve() not in dst.parents:
            raise ValueError('Asset path outside the intended directory')
        if sha256(src) != entry['sha256']:
            raise ValueError('Source hash mismatch: ' + entry['source_file'])
        if dst.exists():
            if sha256(dst) != entry['sha256']:
                raise FileExistsError(str(dst))
        else:
            jobs.append((src, dst, entry['sha256']))
    for src, dst, expected in jobs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        if sha256(dst) != expected:
            raise ValueError('Copied hash mismatch: ' + str(dst))
        print('Restored:', dst.relative_to(project_root))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True, help='原工程 v2.0 目录')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'docs/model_assets.json').read_text(encoding='utf-8'))
    restore(args.source, ROOT, manifest['assets'])
