"""Global pairwise alignment (Needleman-Wunsch) and edit distance with traceback."""
from __future__ import annotations
from dataclasses import dataclass
from .sequence import validate_sequence

@dataclass(frozen=True)
class Alignment:
    left: str
    right: str
    score: int
    matches: int
    mismatches: int
    gaps: int
    identity: float

def align_global(left: str, right: str, *, match: int=2,mismatch:int=-1,gap:int=-2,max_cells:int=2_000_000)->Alignment:
    a,b=validate_sequence(left),validate_sequence(right)
    if (len(a)+1)*(len(b)+1)>max_cells:raise ValueError('alignment too large')
    m,n=len(a),len(b)
    dp=[[0]*(n+1) for _ in range(m+1)]
    for i in range(1,m+1):dp[i][0]=i*gap
    for j in range(1,n+1):dp[0][j]=j*gap
    for i in range(1,m+1):
        for j in range(1,n+1):
            dp[i][j]=max(dp[i-1][j-1]+(match if a[i-1]==b[j-1] else mismatch),dp[i-1][j]+gap,dp[i][j-1]+gap)
    i,j=m,n;la=[];lb=[]
    while i or j:
        if i and j and dp[i][j]==dp[i-1][j-1]+(match if a[i-1]==b[j-1] else mismatch):
            la.append(a[i-1]);lb.append(b[j-1]);i-=1;j-=1
        elif i and dp[i][j]==dp[i-1][j]+gap:
            la.append(a[i-1]);lb.append('-');i-=1
        else:la.append('-');lb.append(b[j-1]);j-=1
    la=''.join(reversed(la));lb=''.join(reversed(lb))
    matches=sum(x==y for x,y in zip(la,lb));gaps=sum('-' in (x,y) for x,y in zip(la,lb))
    mismatches=len(la)-matches-gaps
    return Alignment(la,lb,dp[m][n],matches,mismatches,gaps,matches/len(la) if la else 0)

def levenshtein(left: str,right: str)->int:
    a,b=validate_sequence(left),validate_sequence(right)
    if len(b)>len(a):a,b=b,a
    previous=list(range(len(b)+1))
    for i,c in enumerate(a,1):
        current=[i]
        for j,d in enumerate(b,1):current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(c!=d)))
        previous=current
    return previous[-1]
