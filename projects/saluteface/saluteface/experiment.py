"""Protocol-based comparative watermark experiments using multiple keys and edit budgets."""
from __future__ import annotations
from dataclasses import dataclass,asdict
from collections import defaultdict
from hashlib import sha256
from .watermark import WatermarkCodec
from .mutations import substitute
from .significance import wilson_interval,roc_auc
from .sequence import validate_sequence

@dataclass(frozen=True)
class Trial:
    sequence_sha256:str
    treatment:str
    edits:int
    score:float
    detected:bool
    expected:int

def run_experiment(sequences:list[str],*,key:bytes,edits=(0,1,2,3),seed:int=42,stride:int=7,threshold:float=.9)->dict:
    if not sequences:raise ValueError('sequences required')
    if any(n<0 for n in edits):raise ValueError('edits must be nonnegative')
    codec=WatermarkCodec(key,stride=stride,threshold=threshold)
    trials=[]
    for i,raw in enumerate(sequences):
        seq=validate_sequence(raw);encoded=codec.embed(seq)
        for n in edits:
            for treatment,base,expected in (('original',seq,0),('embedded',encoded,1)):
                mutated=substitute(base,min(n,len(base)),seed=seed,identifier=f'{i}:{treatment}:{n}').result if n else base
                verified=codec.verify(mutated)
                trials.append(Trial(sha256(seq.encode()).hexdigest(),treatment,n,verified.agreement,verified.detected,expected))
    groups=defaultdict(list)
    for x in trials:groups[(x.treatment,x.edits)].append(x)
    summary=[]
    for (name,n),values in sorted(groups.items()):
        positive=sum(v.detected for v in values)
        lo,hi=wilson_interval(positive,len(values))
        summary.append({'treatment':name,'edits':n,'n':len(values),'detection_rate':positive/len(values),'wilson_95':[lo,hi]})
    auc={}
    for n in edits:
        these=[t for t in trials if t.edits==n]
        auc[str(n)]=roc_auc([t.expected for t in these],[t.score for t in these])
    return {'protocol':'original-educational-watermark-not-synthid','seed':seed,'stride':stride,'threshold':threshold,'trials':[asdict(t) for t in trials],'summary':summary,'roc_auc_by_edits':auc}
