"""Evaluation with safeguards against empty cohorts and reporting leakage."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class BinaryMetrics:
    tp: int
    fp: int
    tn: int
    fn: int
    precision: float | None
    recall: float | None
    specificity: float | None
    f1: float | None
    accuracy: float | None


def _ratio(a: int, b: int) -> float | None:
    return a / b if b else None


def evaluate(pairs: Iterable[tuple[bool, bool]]) -> BinaryMetrics:
    tp = fp = tn = fn = 0
    for expected, predicted in pairs:
        if not isinstance(expected, bool) or not isinstance(predicted, bool):
            raise TypeError("boolean labels required")
        if expected and predicted: tp += 1
        elif not expected and predicted: fp += 1
        elif expected: fn += 1
        else: tn += 1
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    return BinaryMetrics(tp, fp, tn, fn, precision, recall, _ratio(tn, tn + fp), _ratio(2 * tp, 2 * tp + fp + fn), _ratio(tp + tn, tp + fp + tn + fn))
