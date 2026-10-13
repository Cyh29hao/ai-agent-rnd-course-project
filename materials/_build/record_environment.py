"""Record reproducibility requirements and local evidence without reading secrets."""
from pathlib import Path
import json,hashlib,sys,platform,datetime,importlib.metadata
root=Path(__file__).resolve().parents[1]
assets=root/'_build'/'assets'
source={'anthropic_fig3.png':'https://alignment.anthropic.com/2026/automated-alignment-researchers/fig3.png','anthropic_aar_checkpoint.png':'https://alignment.anthropic.com/2026/automated-alignment-researchers/fig9.png','runme_completed.png':'https://cdn.openai.com/devhub/blog/automating-repetitive-work-at-openai-with-codex/runme-completed-evaluation-notebook-edge-to-edge.webp','runme_goal.png':'https://cdn.openai.com/devhub/blog/automating-repetitive-work-at-openai-with-codex/runme-evaluation-goal-original.webp'}
manifest=[{'file':name,'original_url':url,'sha256':hashlib.sha256((assets/name).read_bytes()).hexdigest(),'location':'within this package','note':'Source image retained; PPT uses labelled native cropping where needed.'} for name,url in source.items()]
(assets/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
versions={name:importlib.metadata.version(name) for name in ['python-pptx','python-docx','PyMuPDF','Pillow','pywin32']}
env={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version.split()[0],'os':platform.system(),'installed_library_versions':versions,'render_requirement':'Windows with usable Microsoft PowerPoint and Word COM automation','font':'Microsoft YaHei / 等线','quota_checkpoint_requirement':'Only signed-in production monitor uses ~/.codex/scripts/check_codex_quota.py; students need not have that monitor to read materials or run practice validators.','dependency_boundary':'No old rejected deck directory needed; figure assets bundled. No new packages installed by this step.'}
(root/'_build'/'environment.json').write_text(json.dumps(env,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(env,ensure_ascii=True))
