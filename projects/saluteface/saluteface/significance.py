"""Statistical assessment, bootstrap confidence intervals and permutation testing."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
import random

def wilson_interval(success:int,total:int,z:float=1.96)->tuple[float,float]:
    if total<=0 or not 0<=success<=total:raise ValueError('invalid observations')
    p=success/total;z2=z*z;den=1+z2/total
    center=(p+z2/(2*total))/den
    half=z*sqrt((p*(1-p)+z2/(4*total))/total)/den
    return max(0,center-half),min(1,center+half)

def bootstrap_mean_interval(values:list[float],*,repetitions:int=1000,seed:int=42,confidence:float=.95)->tuple[float,float]:
    if not values or repetitions<20 or not 0<confidence<1:raise ValueError('invalid bootstrap parameters')
    rng=random.Random(seed);n=len(values)
    samples=sorted(sum(rng.choices(values,k=n))/n for _ in range(repetitions))
    a=(1-confidence)/2
    return samples[int(a*(repetitions-1))],samples[int((1-a)*(repetitions-1))]

def permutation_mean_pvalue(control:list[float],treated:list[float],*,repetitions:int=1000,seed:int=42)->float:
    if not control or not treated or repetitions<1:raise ValueError('invalid experiment')
    a=len(control);pooled=list(control)+list(treated)
    observed=abs(sum(control)/a-sum(treated)/len(treated))
    rng=random.Random(seed);extreme=0
    for _ in range(repetitions):
        rng.shuffle(pooled)
        diff=abs(sum(pooled[:a])/a-sum(pooled[a:])/(len(pooled)-a))
        extreme+=(diff>=observed-1e-12)
    return (extreme+1)/(repetitions+1)

def roc_auc(labels:list[int],scores:list[float])->float:
    if len(labels)!=len(scores) or not labels or any(x not in (0,1) for x in labels):raise ValueError('invalid scores')
    pos=[s for y,s in zip(labels,scores) if y];neg=[s for y,s in zip(labels,scores) if not y]
    if not pos or not neg:raise ValueError('both classes required')
    return sum((p>n)+.5*(p==n) for p in pos for n in neg)/(len(pos)*len(neg))
