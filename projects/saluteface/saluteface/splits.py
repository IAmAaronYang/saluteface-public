"""Group-aware deterministic splitting to reduce sequence-family leakage."""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from .similarity import cluster_records

def group_split(records,*,threshold:float=.8,seed:str='saluteface-v3',ratios=(.8,.1,.1),k:int=3)->dict[str,str]:
    items=list(records)
    if len({r.identifier for r in items})!=len(items):raise ValueError('duplicate identifiers')
    if len(ratios)!=3 or any(x<0 for x in ratios) or abs(sum(ratios)-1)>1e-8:raise ValueError('ratios must sum to one')
    clusters=cluster_records(items,threshold=threshold,k=k)
    output={}
    for cluster in clusters:
        digest=sha256((seed+':'+':'.join(cluster)).encode()).digest()
        value=int.from_bytes(digest[:8],'big')/2**64
        split='train' if value<ratios[0] else 'validation' if value<ratios[0]+ratios[1] else 'test'
        for identifier in cluster:output[identifier]=split
    return output

def split_counts(mapping:dict[str,str])->dict[str,int]:
    return {s:sum(v==s for v in mapping.values()) for s in ('train','validation','test')}
