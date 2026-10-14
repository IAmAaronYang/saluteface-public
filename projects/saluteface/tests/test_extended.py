import json
from pathlib import Path
import pytest
from saluteface.mutations import perturb
from saluteface.features import kmers, shannon_entropy, longest_run, extract_features
from saluteface.quality import audit_dataset
from saluteface.benchmark import run_benchmark, benchmark_dict
from saluteface.dataset import DatasetEntry
from saluteface.sequence import SequenceRecord
from saluteface.watermark import WatermarkCodec
from saluteface.io_utils import atomic_json_write
from saluteface.cli import main

SEQ = "ACDEFGHIKLMNPQRSTVWY" * 6

@pytest.mark.parametrize("kind", ["substitution", "insertion", "deletion"])
def test_deterministic_mutations(kind):
    a = perturb(SEQ, kind, 3, seed=17, identifier="x")
    b = perturb(SEQ, kind, 3, seed=17, identifier="x")
    assert a == b
    assert a.result != a.source
    assert len(a.result) == len(SEQ) + {"substitution":0,"insertion":3,"deletion":-3}[kind]

@pytest.mark.parametrize("kind,count", [("deletion",120),("insertion",-1),("substitution",121),("alien",1)])
def test_bad_mutations(kind, count):
    with pytest.raises(ValueError): perturb(SEQ, kind, count)

def test_sequence_features():
    assert kmers("AAAA",2) == {"AA":3}
    assert shannon_entropy("AAAA") == 0
    assert longest_run("AAEEEA") == 3
    f = extract_features(SEQ)
    assert f.length == len(SEQ)
    assert f.distinct_residues == 20
    assert 0 < f.kmer_diversity <= 1

@pytest.mark.parametrize("k",[0,8])
def test_invalid_k(k):
    with pytest.raises(ValueError): kmers("ACDE",k)

def test_audit_detects_leakage():
    entries = [DatasetEntry("a",SEQ,"train","original","fixture"), DatasetEntry("b",SEQ,"test","modified","fixture")]
    report = audit_dataset(entries)
    assert report.cross_split_leaks == [["a","b"]]
    assert report.conflicting_labels == [["a","b"]]
    assert len(report.duplicate_sequence_groups) == 1

def test_empty_audit():
    assert audit_dataset([]).mean_entropy is None

def test_benchmark_deterministic():
    codec = WatermarkCodec(b"unit-test")
    records = [SequenceRecord("x", SEQ), SequenceRecord("y", SEQ[::-1])]
    a=benchmark_dict(run_benchmark(records,codec,seed=7))
    b=benchmark_dict(run_benchmark(records,codec,seed=7))
    assert a==b
    assert a["examples"] == 2
    assert len(a["rows"]) == 10

def test_empty_benchmark():
    with pytest.raises(ValueError): run_benchmark([], WatermarkCodec(b"key"))

def test_atomic_json(tmp_path):
    output = tmp_path / "nested" / "report.json"
    atomic_json_write(output,{"ok": True})
    assert json.loads(output.read_text()) == {"ok":True}

def test_cli_features(tmp_path):
    fasta=tmp_path/"input.fasta"; fasta.write_text(">one\n"+SEQ+"\n")
    out=tmp_path/"features.jsonl"
    assert main(["features",str(fasta),str(out)])==0
    assert json.loads(out.read_text())["identifier"]=="one"

def test_cli_audit(tmp_path):
    from saluteface.dataset import serialize_jsonl
    source=tmp_path/"data.jsonl"; source.write_text(serialize_jsonl([DatasetEntry("a",SEQ,"train","original","fixture")]))
    assert main(["audit",str(source)])==0

def test_cli_benchmark(tmp_path, monkeypatch):
    fasta=tmp_path/"input.fasta"; fasta.write_text(">one\n"+SEQ+"\n")
    monkeypatch.setenv("SALUTEFACE_EXPERIMENT_KEY","demo-only-key")
    out=tmp_path/"benchmark.json"
    assert main(["benchmark",str(fasta),str(out)])==0
    assert json.loads(out.read_text())["examples"]==1
