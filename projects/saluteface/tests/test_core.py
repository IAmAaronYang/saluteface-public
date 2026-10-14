import json
import pytest
from saluteface.sequence import validate_sequence, SequenceRecord
from saluteface.errors import InvalidSequence, InvalidDataset
from saluteface.fasta import read_fasta, write_fasta
from saluteface.dataset import assign_split, build_entries, serialize_jsonl, parse_jsonl, manifest
from saluteface.watermark import WatermarkCodec
from saluteface.evaluate import evaluate
from saluteface.provenance import create_provenance


def test_sequence_normalization():
    assert validate_sequence(" acd ef ") == "ACDEF"

@pytest.mark.parametrize("bad", ["", "AXG", "M*", "123", "-", "aczu"])
def test_invalid_residues(bad):
    with pytest.raises(InvalidSequence): validate_sequence(bad)


def test_fasta_roundtrip():
    rows = [SequenceRecord("s1", "ACDEFG", "example"), SequenceRecord("s2", "MSTVWY")]
    assert list(read_fasta(write_fasta(rows).splitlines())) == rows


def test_duplicate_fasta():
    with pytest.raises(InvalidDataset): list(read_fasta([">a", "ACD", ">a", "ACD"]))


def test_split_determinism():
    assert assign_split("s1") == assign_split("s1")


def test_dataset_contract():
    entries = build_entries([SequenceRecord("s1", "ACDEFG")], source="synthetic-example")
    serialized = serialize_jsonl(entries)
    assert parse_jsonl(serialized) == entries
    assert manifest(entries, serialized.encode())["records"] == 1


def test_dataset_reject_unknown_fields():
    with pytest.raises(InvalidDataset): parse_jsonl('{"oops": 1}')


def test_watermark_is_deterministic():
    codec = WatermarkCodec(b"example-secret")
    input_seq = "ACDEFGHIKLMNPQRSTVWY" * 10
    assert codec.embed(input_seq) == codec.embed(input_seq)
    assert len(codec.embed(input_seq)) == len(input_seq)


def test_watermark_invalid_key():
    with pytest.raises(ValueError): WatermarkCodec(b"")


def test_metrics():
    m = evaluate([(True, True), (True, False), (False, True), (False, False)])
    assert m.accuracy == 0.5
    assert m.precision == 0.5
    assert m.f1 == 0.5


def test_empty_metrics():
    assert evaluate([]).accuracy is None


def test_provenance():
    record = create_provenance(b"abc", tool="test")
    assert len(record.artifact_sha256) == 64
    assert "Self-reported" in record.declaration
