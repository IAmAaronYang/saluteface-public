"""Create portable Hugging Face-compatible dataset folders locally, no network needed."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
import csv,json,hashlib
from .dataset import DatasetEntry

def export_dataset(entries:list[DatasetEntry],destination:Path,*,title:str='Saluteface sequence pilot')->dict:
    if not entries:raise ValueError('entries required')
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    by_split=defaultdict(list)
    for entry in entries:by_split[entry.split].append(entry)
    files={};counts={}
    for split,rows in sorted(by_split.items()):
        path=destination/f'{split}.csv'
        with path.open('w',newline='',encoding='utf8') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(DatasetEntry.__dataclass_fields__))
            writer.writeheader()
            for row in rows:writer.writerow(asdict(row))
        content=path.read_bytes();files[path.name]=hashlib.sha256(content).hexdigest();counts[split]=len(rows)
    card=f"""---
language:
- en
license: mit
task_categories:
- text-classification
---

# {title}

Locally generated educational protein-sequence research data.

**Not DeepMind SynthID Bio. Not experimentally validated.**

Data splits are in CSV format. Synthetic sequence modifications may change function.
"""
    (destination/'README.md').write_text(card,encoding='utf8')
    report={'title':title,'counts':counts,'sha256':files,'total':len(entries),'format':'csv'}
    (destination/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    return report
