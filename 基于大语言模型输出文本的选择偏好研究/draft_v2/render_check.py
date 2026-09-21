"""Render every page and produce contact sheets for manual visual review."""
from pathlib import Path
import json
import re
import shutil
import subprocess
from PIL import Image, ImageOps, ImageDraw
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
pdf = HERE / 'build/manuscript.pdf'
qa = HERE / 'build/qa'
qa.mkdir(parents=True, exist_ok=True)
reader = PdfReader(pdf)
text = '\n'.join(p.extract_text() for p in reader.pages)
assert len(reader.pages) >= 6
assert '62.37' in text and '1.6196' in text and '69.06' in text
log = (HERE / 'build/manuscript.log').read_text(encoding='utf-8',errors='replace')
assert not re.search(r'Overfull|undefined|Missing character|LaTeX Error', log)
(qa / 'extracted.txt').write_text(text, encoding='utf-8')
subprocess.run(['pdftoppm','-scale-to','1400','-png',str(pdf),str(qa / 'page')],check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
images = sorted(qa.glob('page-*.png'))
assert len(images) == len(reader.pages)
for first in range(0,len(images),3):
    canvas = Image.new('RGB',(1800,900),'#dadada')
    draw = ImageDraw.Draw(canvas)
    for j,path in enumerate(images[first:first+3]):
        im = Image.open(path).convert('RGB')
        im.thumbnail((580,845))
        canvas.paste(im,(j*600+(600-im.width)//2,35))
        draw.text((j*600+20,12),f'Page {first+j+1}',fill='black')
    canvas.save(qa / f'contact-{first//3+1}.jpg',quality=94)
dest = ROOT / 'output/pdf/数学的实践与认识_大修稿_v2.pdf'
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(pdf,dest)
source = (HERE / 'manuscript.tex').read_text(encoding='utf-8')
report = {'pages':len(reader.pages),'sections':len(re.findall(r'\\section\{',source)),
          'tables':source.count('\\begin{table}'),'figures':source.count('\\begin{figure}'),
          'chinese_characters_tex':len(re.findall(r'[\u4e00-\u9fff]',source)),
          'overfull_or_missing_references':False,'pdf':str(dest),
          'visual_review':'Contact sheets generated; inspect manually.'}
(qa / 'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
