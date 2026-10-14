import json
from pathlib import Path
import pytest
from saluteface.sequence import SequenceRecord
from saluteface.alignment import align_global, levenshtein
from saluteface.similarity import jaccard, minhash_signature, signature_similarity,detect_near_duplicates,cluster_records
from saluteface.structure import descriptors,sliding_hydropathy
from saluteface.significance import wilson_interval,bootstrap_mean_interval,permutation_mean_pvalue,roc_auc
from saluteface.splits import group_split,split_counts
from saluteface.dataset import DatasetEntry
from saluteface.hub_export import export_dataset
from saluteface.pipeline import run_pipeline,PipelineConfig
from saluteface.experiment import run_experiment
from saluteface.report import experiment_markdown
from saluteface.cli import main

SEQ='ACDEFGHIKLMNPQRSTVWY'*4

def test_global_identity():
    result=align_global('ACDE','ACDE');assert result.score==8 and result.identity==1 and result.gaps==0

def test_global_gap():
    result=align_global('ACDE','ACD');assert result.gaps==1 and result.matches==3

def test_alignment_limit():
    with pytest.raises(ValueError):align_global(SEQ,SEQ,max_cells=9)

def test_edit_distance():
    assert levenshtein('ACDE','ACD')==1
    assert levenshtein('ACDE','ACDE')==0

def test_jaccard_exact():assert jaccard(SEQ,SEQ)==1

def test_minhash_exact():
    a=minhash_signature(SEQ);assert a==minhash_signature(SEQ) and signature_similarity(a,a)==1

def test_similarity_cluster():
    items=[SequenceRecord('a',SEQ),SequenceRecord('b',SEQ),SequenceRecord('c','Y'*80)]
    assert detect_near_duplicates(items,threshold=1)[0].score==1
    assert cluster_records(items,threshold=1)[0]==['a','b']

def test_similarity_threshold_error():
    with pytest.raises(ValueError):detect_near_duplicates([],threshold=2)

def test_descriptors_mass():
    result=descriptors('ACDE');assert result.length==4 and result.molecular_mass_da>300

def test_hydropathy():assert len(sliding_hydropathy(SEQ,window=9))==len(SEQ)-8

def test_hydropathy_reject():
    with pytest.raises(ValueError):sliding_hydropathy('ACD',window=4)

def test_wilson():
    lo,hi=wilson_interval(5,10);assert 0<lo<.5<hi<1

def test_wilson_invalid():
    with pytest.raises(ValueError):wilson_interval(1,0)

def test_bootstrap_reproducible():
    a=bootstrap_mean_interval([1,2,3],seed=12);assert a==bootstrap_mean_interval([1,2,3],seed=12)

def test_permutation():assert permutation_mean_pvalue([0,0,0],[1,1,1],seed=1)<.1

def test_auc():assert roc_auc([0,1,0,1],[.1,.8,.2,.9])==1

def test_group_splits_together():
    records=[SequenceRecord('a',SEQ),SequenceRecord('b',SEQ),SequenceRecord('c','Y'*80)]
    assigned=group_split(records);assert assigned['a']==assigned['b'] and sum(split_counts(assigned).values())==3

def test_group_duplicate_ids():
    with pytest.raises(ValueError):group_split([SequenceRecord('a',SEQ),SequenceRecord('a',SEQ)])

def test_hub_export(tmp_path):
    entries=[DatasetEntry('a',SEQ,'train','original','demo'),DatasetEntry('b',SEQ,'test','modified','demo')]
    manifest=export_dataset(entries,tmp_path);assert manifest['total']==2 and (tmp_path/'README.md').exists()

def test_pipeline(tmp_path):
    source=tmp_path/'input.fasta';source.write_text('>one\n'+SEQ+'\n>two\n'+'Y'*80+'\n')
    out=tmp_path/'out'; report=run_pipeline(source,out)
    assert report['records']==2 and (out/'huggingface'/'manifest.json').exists()
    assert json.loads((out/'pipeline_report.json').read_text())['records']==2

def test_experiment_reproducible():
    a=run_experiment([SEQ],key=b'demo',edits=(0,1),seed=2)
    b=run_experiment([SEQ],key=b'demo',edits=(0,1),seed=2)
    assert a==b and len(a['trials'])==4
    assert 'ROC AUC' in experiment_markdown(a)

def test_experiment_invalid():
    with pytest.raises(ValueError):run_experiment([],key=b'x')

def test_cli_align(capsys):
    assert main(['align','ACDE','ACDE'])==0
    assert json.loads(capsys.readouterr().out)['identity']==1

def test_cli_pipeline(tmp_path):
    f=tmp_path/'i.fasta';f.write_text('>one\n'+SEQ+'\n')
    assert main(['pipeline',str(f),str(tmp_path/'out')])==0

def test_cli_experiment(tmp_path,monkeypatch):
    f=tmp_path/'i.fasta';f.write_text('>one\n'+SEQ+'\n')
    monkeypatch.setenv('SALUTEFACE_EXPERIMENT_KEY','local-demo-key')
    out=tmp_path/'e.json'
    assert main(['experiment',str(f),str(out)])==0 and out.with_suffix('.md').exists()
