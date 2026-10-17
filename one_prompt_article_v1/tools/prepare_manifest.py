from pathlib import Path
import hashlib
import json
import sys


root = Path(__file__).resolve().parents[1]
project_root = root.parent.resolve()
manifest_path = root / 'article' / 'input_manifest.json'
database_names = (
    'DASC_Bare_Catalysts_RPBE_D4.db',
    'DASC_OH_Adsorption_RPBE_D4.db',
    'DASC_O_Adsorption_RPBE_D4.db',
    'DASC_OOHx_Adsorption_RPBE_D4.db',
    'DASC_OOHz_Adsorption_RPBE_D4.db',
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


current_files = {}
for name in database_names:
    path = project_root / name
    if not path.is_file():
        raise FileNotFoundError(f'Required source database is missing: {path}')
    current_files[f'../{name}'] = {
        'path': f'../{name}',
        'role': 'source of truth',
        'sha256': sha256(path),
        'bytes': path.stat().st_size,
    }


accept_current = sys.argv[1:] == ['--accept-current']
if sys.argv[1:] not in ([], ['--accept-current']):
    raise SystemExit('Usage: python tools/prepare_manifest.py [--accept-current]')

if manifest_path.is_file() and not accept_current:
    existing = json.loads(manifest_path.read_text(encoding='utf-8'))
    existing_files = {
        item.get('path'): item
        for item in existing.get('files', [])
        if isinstance(item, dict) and str(item.get('path', '')).lower().endswith('.db')
    }
    expected_paths = set(current_files)
    if set(existing_files) != expected_paths:
        raise SystemExit(
            'Existing manifest does not contain exactly the five source database baselines. '
            'Review it and use --accept-current only to intentionally establish new baselines.'
        )

    changed = [
        rel_path
        for rel_path, current in current_files.items()
        if existing_files[rel_path].get('sha256') != current['sha256']
    ]
    if changed:
        for rel_path in changed:
            print(f'ALERT: source database differs from the recorded baseline: {rel_path}')
        print('Manifest left unchanged. Review the database before accepting a new baseline.')
        raise SystemExit(0)

manifest = {'files': list(current_files.values())}
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
if accept_current:
    print('Accepted current SHA-256 baselines for the five source databases.')
else:
    print('Prepared the database-only manifest; existing database baselines are unchanged.')
