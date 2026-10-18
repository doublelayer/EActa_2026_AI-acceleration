from pathlib import Path
import hashlib,json
from zipfile import ZipFile
root=Path(__file__).absolute().parents[1]
manifest=json.loads((root/'article/input_manifest.json').read_text())
for item in manifest['files']:
    path=root/item['path']
    assert path.is_file(),item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],item['path']
    assert not item['path'].startswith('inputs/'),item['path']
    assert item['path']!='Electrochimica_Acta_research_article_refernce.docx',item['path']
    if path.suffix=='.ipynb':
        data=json.loads(path.read_text());assert len(data['cells'])>1,path.name
    if path.suffix=='.zip':
        with ZipFile(path) as archive:assert archive.testzip() is None,path.name
reference='Electrochimica_Acta_research_article_refernce.docx'
assert (root/reference).is_file(),reference
allowed={'PROMPT.txt','AGENTS.md',reference}
assert len(list(root.glob('*.ipynb')))==4
for path in root.iterdir():
    assert path.is_dir() or path.suffix=='.ipynb' or path.name in allowed,path.name
print('PASS:',len(manifest['files']),'registered files; input integrity checked; article generation not yet executed.')
