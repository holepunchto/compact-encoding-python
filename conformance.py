"""Checks this port against the compact-encoding corpus.

The contract is CONFORMANCE.md in compact-encoding-test; this is the harness it
describes, translated from the reference conformance.js.
"""

import json
import math
import re
import sys
from pathlib import Path

import compact_encoding as cenc

FIXTURES = Path(__file__).parent / "node_modules" / "compact-encoding-test" / "fixtures"

FIELDS = ("hex", "refused", "decodes", "read", "bits", "rejects")
INTEGER_CATEGORIES = {"integers", "big-endian-integers", "big-integers"}
RECORDS = {"record", "orderedRecord"}
MAX_SAFE_INTEGER = 2**53 - 1
WIDE = re.compile(r"-?[0-9]+n")
TOKENS = {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf, "-0": -0.0}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def value(category, given):
    """A case's input, read as CODECS.md writes it."""
    if category == "buffers":
        return None if given is None else bytes.fromhex(given)
    if isinstance(given, dict) and "units" in given:
        units = b"".join(unit.to_bytes(2, "little") for unit in given["units"])
        return units.decode("utf-16-le", "surrogatepass")
    if isinstance(given, str):
        if category in INTEGER_CATEGORIES and WIDE.fullmatch(given):
            return int(given[:-1])
        if given in TOKENS:
            return TOKENS[given]
    if category == "floats" and isinstance(given, int):
        return float(given)
    return given


def token(decoded):
    """A decoded value, written as an answer writes it."""
    if decoded is None or isinstance(decoded, bool):
        return decoded
    if isinstance(decoded, (bytes, bytearray)):
        return decoded.hex()
    if isinstance(decoded, int):
        if -MAX_SAFE_INTEGER <= decoded <= MAX_SAFE_INTEGER:
            return decoded
        return f"{decoded}n"
    if isinstance(decoded, float):
        if math.isnan(decoded):
            return "NaN"
        if decoded == math.inf:
            return "Infinity"
        if decoded == -math.inf:
            return "-Infinity"
        if decoded == 0.0 and math.copysign(1.0, decoded) < 0:
            return "-0"
        return decoded
    if isinstance(decoded, list):
        return [token(item) for item in decoded]
    if isinstance(decoded, dict):
        return {key: token(item) for key, item in decoded.items()}
    return decoded


def build(declaration):
    if isinstance(declaration, int):
        return declaration
    built = [build(of) for of in declaration.get("of", [])]
    named = getattr(cenc, declaration["name"], None)
    if named is None:
        raise LookupError(declaration["name"])
    return named(*built) if built else named


def shaped(declaration, given):
    if declaration is not None and declaration["name"] in RECORDS:
        return dict(given)
    return given


def encoded(codec, given):
    return cenc.encode(codec, given).hex()


def decoded(codec, given):
    state = cenc.State(bytes.fromhex(given))
    return codec.decode(state), state.start


def answered(codec, example, category, declaration):
    given = example["input"]

    if "bytes" in given:
        try:
            decodes, read = decoded(codec, given["bytes"])
        except Exception:
            return {"rejects": True}
        answer = {"decodes": token(decodes), "read": read}
        if isinstance(decodes, float) and math.isnan(decodes):
            answer["bits"] = encoded(codec, decodes)
        return answer

    encodes = shaped(declaration, value(category, given["value"]))

    try:
        return {"hex": encoded(codec, encodes)}
    except Exception:
        return {"refused": True}


def alike(given, expected):
    """Field by field: the order keys appear in carries no meaning."""
    if isinstance(given, bool) or isinstance(expected, bool):
        return given is expected
    if isinstance(given, list) and isinstance(expected, list):
        return len(given) == len(expected) and all(map(alike, given, expected))
    if isinstance(given, dict) and isinstance(expected, dict):
        return given.keys() == expected.keys() and all(
            alike(given[key], expected[key]) for key in given
        )
    return given == expected


def conformant(given, example, unrepresentable):
    def same(answer):
        return answer is not None and all(
            alike(given.get(field), answer.get(field)) for field in FIELDS
        )

    if same(example["answer"]):
        return True
    if any(same(answer) for answer in example.get("alternatives", [])):
        return True
    if given.get("unrepresentable") is True:
        return any(rule in unrepresentable for rule in example["rules"])

    return False


def run():
    unrepresentable = set(read_json(FIXTURES / "unrepresentable.json"))
    report = []

    for directory in sorted(path for path in FIXTURES.iterdir() if path.is_dir()):
        loaded = read_json(directory / "cases.json")
        category, cases = loaded["category"], loaded["cases"]
        declaration = loaded.get("codec")
        entry = {
            "codec": directory.name,
            "category": category,
            "supported": True,
            "reason": loaded.get("reason"),
            "matched": [],
            "cases": [case["id"] for case in cases],
            "total": len(cases),
            "diverged": [],
        }

        if not cases:
            report.append(entry)
            continue

        try:
            codec = (
                getattr(cenc, directory.name)
                if declaration is None
                else build(declaration)
            )
        except (AttributeError, LookupError):
            entry["supported"] = False
            report.append(entry)
            continue

        answers = read_json(directory / "answers.json")

        for case in cases:
            expected = {**case, "answer": answers.get(case["id"])}
            given = answered(codec, case, category, declaration)

            if conformant(given, expected, unrepresentable):
                entry["matched"].append(case["id"])
            else:
                entry["diverged"].append(
                    {"id": case["id"], "expected": expected["answer"], "given": given}
                )

        report.append(entry)

    return report


def versions():
    corpus = read_json(FIXTURES.parent / "package.json")["version"]
    pyproject = (Path(__file__).parent / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE)
    return corpus, f"compact-encoding-python {version.group(1)}"


def shape(report):
    """The report CONFORMANCE.md specifies, the same in every language."""
    corpus, implementation = versions()
    unsupported = sorted(
        entry["codec"] for entry in report if entry["total"] and not entry["supported"]
    )
    uncovered = {
        entry["codec"]: entry["reason"] for entry in report if not entry["total"]
    }
    matched = sorted(case for entry in report for case in entry["matched"])
    unrun = sorted(
        case
        for entry in report
        if entry["total"] and not entry["supported"]
        for case in entry["cases"]
    )
    diverged = {
        case["id"]: {"corpus": case["expected"], "port": case["given"]}
        for entry in report
        for case in entry["diverged"]
    }

    return {
        "corpus": corpus,
        "implementation": implementation,
        "summary": {
            "matched": len(matched),
            "diverged": len(diverged),
            "unrun": len(unrun),
            "unsupported": len(unsupported),
            "uncovered": len(uncovered),
        },
        "unsupported": unsupported,
        "uncovered": dict(sorted(uncovered.items())),
        "diverged": dict(sorted(diverged.items())),
        "unrun": unrun,
        "matched": matched,
    }


def readable(report, summary):
    for entry in report:
        for case in entry["diverged"]:
            print("DIVERGES " + case["id"])
            print("  corpus: " + json.dumps(case["expected"]))
            print("  port:   " + json.dumps(case["given"]))

    print()
    for entry in report:
        if not entry["total"]:
            continue
        if entry["supported"]:
            tail = ", ".join(case["id"] for case in entry["diverged"])
            count = f"{len(entry['matched'])}/{entry['total']}"
        else:
            tail, count = "not provided by this port", f"0/{entry['total']}"
        print(f"  {entry['category']:<22}{entry['codec']:<26}{count:>7}  {tail}")

    counts = summary["summary"]
    print()
    print(f"{counts['matched']} cases matched, {counts['diverged']} diverged")
    print(
        f"{counts['unrun']} cases unrun in {counts['unsupported']} codecs"
        + (": " + ", ".join(summary["unsupported"]) if summary["unsupported"] else "")
    )
    print(f"{counts['uncovered']} capabilities carry no cases in the corpus")


def main():
    if not FIXTURES.is_dir():
        sys.exit(f"corpus not found at {FIXTURES}, run: npm install")

    report = run()
    summary = shape(report)

    if "--json" in sys.argv[1:]:
        print(json.dumps(summary, indent=2))
    else:
        readable(report, summary)


if __name__ == "__main__":
    main()
