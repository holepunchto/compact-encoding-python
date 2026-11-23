import pytest

import conformance

pytestmark = pytest.mark.skipif(
    not conformance.FIXTURES.is_dir(),
    reason="corpus not resolved, run npm install",
)


def test_no_case_diverges():
    assert conformance.shape(conformance.run())["diverged"] == {}


def test_every_case_is_accounted_for():
    report = conformance.run()
    counts = conformance.shape(report)["summary"]
    accounted = counts["matched"] + counts["diverged"] + counts["unrun"]
    assert accounted == sum(entry["total"] for entry in report)
