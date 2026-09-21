"""Render pages for final visual QA, using the bundled artifact Python."""
from pathlib import Path
import sys,subprocess,json,re
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
kind=sys.argv[1]
pdf=ROOT/('基于大语言模型输出文本的选择偏好研究/draft_v3/build/manuscript.pdf' if kind=='latex' else 'output/qa_v3/word/word_render.pdf')
out=ROOT/'output/qa_v3'/kind
out.mkdir(parents=True,exist_ok=True)
r=PdfReader(pdf);text='\n'.join(p.extract_text() for p in r.pages)
(out/'extracted.txt').write_text(text,encoding='utf-8')
assert '[?]' not in text and '??' not in text
assert '1.6196' in text and '400' in text and 'Neyman' in text
if kind=='latex':
    log=(pdf.parent/'manuscript.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search('Overfull|undefined|Missing character|LaTeX Error',log)
subprocess.run(['pdftoppm','-scale-to','1500','-png',str(pdf),str(out/'page')],check=True)
(out/'checks.json').write_text(json.dumps(dict(pages=len(r.pages),text_checks=True,visual_review='pending'),indent=2),encoding='utf-8')
print('Rendered',len(r.pages),'pages',out)
