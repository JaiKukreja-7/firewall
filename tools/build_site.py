"""Build hosting assets with the Python standard library; no installation."""
from pathlib import Path
import shutil
import json
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reporting_demo import create_fixture, validate

site = ROOT / 'site'
site.mkdir(exist_ok=True)
for source in (ROOT / 'web').glob('*.html'):
    shutil.copy2(source, site / source.name)
for name in ['submission.html', 'NS-P02_Verification_Report.pdf', 'NS-P02_Verification_Report.docx',
             'NS-P02_Presentation.pptx', 'validation-evidence.json', 'presentation-script.md',
             'teacher-guide.html', 'NS-P02_Teacher_Guide.pdf', 'NS-P02_Teacher_Guide.docx',
             'NS-P02_Teacher_Guide.md']:
    source = ROOT / 'deliverables' / name
    if source.exists():
        shutil.copy2(source, site / name)
with TemporaryDirectory() as folder:
    database = Path(folder) / 'telemetry.sqlite'
    create_fixture(database)
    evidence = validate(database)
    assert len(evidence['results']) == 13 and all(item['passed'] for item in evidence['results'])
(site / 'reporting-evidence.json').write_text(json.dumps(evidence, indent=2))
(site / 'reporting_demo.py').write_text((ROOT / 'reporting_demo.py').read_text())
(site / '.nojekyll').touch()
print('Built static dashboard, report, presentation and verified reporting evidence.')
