"""Alignment-free sequence similarity, near-duplicate indexing and cluster inference."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from .sequence import validate_sequence

def kmers(sequence: str, k: int = 3) -> set[str]:
    seq = validate_sequence(sequence)
    if k < 1: raise ValueError("k must be positive")
    return {seq[i:i+k] for i in range(max(0,len(seq)-k+1))}

def jaccard(left: str, right: str, k: int = 3) -> float:
    a,b=kmers(left,k),kmers(right,k)
    return len(a&b)/len(a|b) if a or b else 1.0

def minhash_signature(sequence: str, *, k: int = 3, permutations: int = 64) -> tuple[int,...]:
    if permutations < 1: raise ValueError("permutations must be positive")
    grams=kmers(sequence,k)
    return tuple(min(int.from_bytes(sha256(f'{i}:{gram}'.encode()).digest()[:8],'big') for gram in grams) if grams else 2**64-1 for i in range(permutations))

def signature_similarity(a: tuple[int,...], b: tuple[int,...]) -> float:
    if not a or len(a)!=len(b): raise ValueError("signature lengths must match")
    return sum(x==y for x,y in zip(a,b))/len(a)

@dataclass(frozen=True)
class SimilarityPair:
    first: str
    second: str
    score: float

def detect_near_duplicates(records, *, threshold: float=.8, k: int=3) -> list[SimilarityPair]:
    if not 0<=threshold<=1: raise ValueError("threshold outside [0,1]")
    items=list(records)
    grams=[kmers(r.sequence,k) for r in items]
    output=[]
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            a,b=grams[i],grams[j]
            score=len(a&b)/len(a|b) if a or b else 1.0
            if score>=threshold:output.append(SimilarityPair(items[i].identifier,items[j].identifier,score))
    return sorted(output,key=lambda p:(-p.score,p.first,p.second))

def cluster_records(records, *, threshold: float=.8, k: int=3) -> list[list[str]]:
    items=list(records)
    parent=list(range(len(items)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    identifiers={r.identifier:i for i,r in enumerate(items)}
    for pair in detect_near_duplicates(items,threshold=threshold,k=k):
        a,b=find(identifiers[pair.first]),find(identifiers[pair.second])
        parent[b]=a
    groups=defaultdict(list)
    for i,r in enumerate(items):groups[find(i)].append(r.identifier)
    return sorted([sorted(group) for group in groups.values()],key=lambda g:(-len(g),g))
