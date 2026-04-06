import pandas as pd
from pathlib import Path

base = Path(r'd:\Files\25_10_22_青苗计划')
paths = [
    base / 'Data' / 'lmarena-aiarena-human-preference-140k' / 'Data',
    base / 'Data' / 'integrated_data',
    base / 'Data' / 'optimized_data',
    base / 'Data' / 'format_data',
    base / 'Data' / 'length_data',
]
output_lines = []
output_lines.append('DATA PARQUET AUDIT REPORT')
output_lines.append('='*80)
for p in paths:
    output_lines.append(f'\nDIRECTORY: {p}')
    if not p.exists():
        output_lines.append('  NOT FOUND')
        continue
    files = sorted([f for f in p.glob('*.parquet') if f.is_file()])
    if not files:
        output_lines.append('  NO PARQUET FILES FOUND')
        continue
    for f in files:
        try:
            df = pd.read_parquet(f)
            output_lines.append(f'\nFILE: {f.name}')
            output_lines.append(f'  PATH: {f}')
            output_lines.append(f'  ROWS: {len(df):,}')
            output_lines.append(f'  COLUMNS ({len(df.columns)}):')
            cols = ', '.join(map(str, df.columns.tolist()))
            if len(cols) > 1000:
                output_lines.append('    ' + ', '.join(map(str, df.columns.tolist()[:40])) + ', ...')
            else:
                output_lines.append('    ' + cols)
        except Exception as e:
            output_lines.append(f'  ERROR: {e}')

report_path = base / 'Reports' / 'R14_data_audit_report.txt'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))
print('\n'.join(output_lines))
print('\nReport saved to:', report_path)
