"""Sequence composition and simple physicochemical descriptors; NOT structure prediction."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass,asdict
from .sequence import validate_sequence

# Approximate average residue masses, excluding terminal water.
RESIDUE_MASS={'A':71.0788,'R':156.1875,'N':114.1038,'D':115.0886,'C':103.1388,'E':129.1155,'Q':128.1307,'G':57.0519,'H':137.1411,'I':113.1594,'L':113.1594,'K':128.1741,'M':131.1926,'F':147.1766,'P':97.1167,'S':87.0782,'T':101.1051,'W':186.2132,'Y':163.1760,'V':99.1326}
HYDROPATHY={'A':1.8,'R':-4.5,'N':-3.5,'D':-3.5,'C':2.5,'E':-3.5,'Q':-3.5,'G':-0.4,'H':-3.2,'I':4.5,'L':3.8,'K':-3.9,'M':1.9,'F':2.8,'P':-1.6,'S':-0.8,'T':-0.7,'W':-0.9,'Y':-1.3,'V':4.2}
@dataclass(frozen=True)
class Descriptors:
    length:int
    molecular_mass_da:float
    mean_hydropathy:float
    aromatic_fraction:float
    charged_fraction:float
    cysteine_count:int
    proline_count:int
    simple_charge_proxy:int

def descriptors(sequence:str)->Descriptors:
    seq=validate_sequence(sequence);counts=Counter(seq)
    return Descriptors(len(seq),round(sum(RESIDUE_MASS[aa] for aa in seq)+18.01528,4),round(sum(HYDROPATHY[aa] for aa in seq)/len(seq),5),round(sum(counts[aa] for aa in 'FWY')/len(seq),5),round(sum(counts[aa] for aa in 'DEKRH')/len(seq),5),counts['C'],counts['P'],counts['K']+counts['R']-counts['D']-counts['E'])

def sliding_hydropathy(sequence:str,window:int=9)->list[float]:
    seq=validate_sequence(sequence)
    if window<1 or window>len(seq):raise ValueError('invalid window')
    return [round(sum(HYDROPATHY[c] for c in seq[i:i+window])/window,5) for i in range(len(seq)-window+1)]
