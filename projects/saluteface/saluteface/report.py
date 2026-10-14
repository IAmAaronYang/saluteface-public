"""Render reproducible, standalone Markdown reports from experimental JSON results."""
from __future__ import annotations
from pathlib import Path
from .io_utils import atomic_json_write
import json

def experiment_markdown(report:dict)->str:
    lines=['# Saluteface experimental report','','**Scope:** synthetic protocol evaluation; no biochemical or SynthID Bio claims.','',f"Samples: {len(report['trials'])} trials",'', '| Treatment | Edits | N | Detection rate | 95% Wilson CI |','|---|---:|---:|---:|---:|']
    for row in report['summary']:
        lo,hi=row['wilson_95']
        lines.append(f"| {row['treatment']} | {row['edits']} | {row['n']} | {row['detection_rate']:.3f} | {lo:.3f}–{hi:.3f} |")
    lines+=['','## ROC AUC by edit budget','']
    for key,value in report['roc_auc_by_edits'].items():lines.append(f'- {key} edits: {value:.4f}')
    lines+=['','## Caveats','','The toy watermark modifies sequence residues and has no demonstrated biological-function preservation, origin attribution, or clinical utility.','']
    return '\n'.join(lines)

def export_report(report:dict,path:Path)->None:
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(experiment_markdown(report),encoding='utf8')
