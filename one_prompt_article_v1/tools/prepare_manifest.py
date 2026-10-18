from pathlib import Path
import hashlib,json
root=Path(__file__).absolute().parents[1]
files=[]
for path in sorted(root.rglob('*')):
    rel=path.relative_to(root)
    if not path.is_file() or any(p in {'inputs','outputs','__pycache__','.git'} for p in rel.parts) or path.name in {'input_manifest.json','Electrochimica_Acta_research_article_refernce.docx'}:
        continue
    role='scientific input' if path.suffix in {'.db','.csv','.ipynb','.png','.svg','.pdf','.zip'} else 'instructions or metadata'
    files.append({'path':rel.as_posix(),'role':role,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size})
manifest={'network':'No scientific data downloads; relevant web research permitted','generation_executed':False,'excluded':['Electrochimica_Acta_research_article_refernce.docx','inputs/','outputs/'],'files':files}
(root/'article/input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Registered',len(files),'files; reference and generated outputs excluded.')
