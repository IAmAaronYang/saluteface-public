"""End-to-end reproducible local pipeline for FASTA input, dataset construction and audit."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import hashlib,json
from .fasta import read_fasta
from .dataset import DatasetEntry,serialize_jsonl
from .quality import audit_dict
from .splits import group_split,split_counts
from .hub_export import export_dataset
from .structure import descriptors
from .io_utils import atomic_json_write

@dataclass(frozen=True)
class PipelineConfig:
    seed:str='saluteface-v3'
    similarity_threshold:float=.80
    kmer_size:int=3
    source:str='local-fasta'

def run_pipeline(input_path:Path,output_dir:Path,config:PipelineConfig=PipelineConfig())->dict:
    records=list(read_fasta(Path(input_path).read_text(encoding='utf8').splitlines()))
    if not records:raise ValueError('no records')
    if not (0<=config.similarity_threshold<=1):raise ValueError('invalid threshold')
    splits=group_split(records,threshold=config.similarity_threshold,k=config.kmer_size,seed=config.seed)
    entries=[DatasetEntry(r.identifier,r.sequence,splits[r.identifier],'original',config.source) for r in records]
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    content=serialize_jsonl(entries)
    (output_dir/'dataset.jsonl').write_text(content,encoding='utf8')
    with (output_dir/'descriptors.jsonl').open('w',encoding='utf8') as f:
        for r in records:f.write(json.dumps({'identifier':r.identifier,**asdict(descriptors(r.sequence))},sort_keys=True)+'\n')
    audit=audit_dict(entries)
    atomic_json_write(output_dir/'audit.json',audit)
    hub=export_dataset(entries,output_dir/'huggingface')
    report={'pipeline':'saluteface-v3','config':asdict(config),'input_sha256':hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),'records':len(records),'splits':split_counts(splits),'audit':audit,'hub':hub}
    atomic_json_write(output_dir/'pipeline_report.json',report)
    return report
