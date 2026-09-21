"""防止历史入口被误用；不改变历史计算函数或输出。"""
import os
import sys


def require_legacy_opt_in(script: str) -> None:
    message = (f'{script} 是历史分析入口，不属于当前有效分析链。\n'
               '请使用 Codes/reproduce.py；当前结果见 CURRENT_RESULTS.json。\n'
               '仅为历史复核，可设置 MUC_ALLOW_LEGACY=1 后运行；'
               '这可能覆盖旧目录的输出，且不能将其与新版结论混用。')
    if os.environ.get('MUC_ALLOW_LEGACY') != '1':
        raise SystemExit(message)
    print('WARNING: ' + message, file=sys.stderr)
