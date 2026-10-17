"""Compare the five source database fingerprints with the committed manifest baseline."""

from pathlib import Path
import hashlib
import json


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
expected_paths = {f'../{name}' for name in database_names}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
if set(manifest) != {'files'} or not isinstance(manifest['files'], list):
    raise SystemExit('Invalid input manifest: it must contain only a files list.')

manifest_paths = [item.get('path') for item in manifest['files'] if isinstance(item, dict)]
if len(manifest_paths) != len(manifest['files']) or set(manifest_paths) != expected_paths or len(manifest_paths) != len(expected_paths):
    raise SystemExit('Invalid input manifest: it must list each of the five DASC .db files exactly once and no other files.')

alerts = []
for item in manifest['files']:
    rel_path = item['path']
    path = (root / rel_path).resolve()
    if path.suffix.lower() != '.db' or not path.is_relative_to(project_root):
        raise SystemExit(f'Invalid database path in input manifest: {rel_path}')
    expected_sha256 = item.get('sha256')
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise SystemExit(f'Invalid SHA-256 baseline in input manifest: {rel_path}')
    if not path.is_file():
        alerts.append(f'missing source database: {rel_path}')
        continue

    actual_sha256 = sha256(path)
    if actual_sha256 != expected_sha256:
        alerts.append(
            f'source database changed: {rel_path} '
            f'(expected {expected_sha256}, found {actual_sha256})'
        )
    else:
        print(f'OK: {rel_path}')

if alerts:
    for alert in alerts:
        print(f'ALERT: {alert}')
    print(f'ALERT: {len(alerts)} source database issue(s); no other files were checked.')
else:
    print(f'PASS: all {len(expected_paths)} source database fingerprints match; no other files were checked.')
