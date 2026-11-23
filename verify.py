#!/usr/bin/env python3
"""Independently verify data/lucas_smith_terms.json.

Recomputes L(n), multiplies the published factorization back, checks primality
with three independent tests, and checks the digit-sum equality.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import gmpy2
import sympy

sys.path.insert(0, str(Path(__file__).parent / "src"))
from smith_search import F, L, digsum, is_prime  # noqa: E402

DATA = Path(__file__).parent / "data" / "lucas_smith_terms.json"


def main() -> int:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    failures = []

    for term in doc["terms"]:
        n, factors = term["n"], term["factors"]
        value = L(n)
        checks = {
            "product": math.prod(factors) == value,
            "mr24": all(is_prime(q, 24) for q in factors),
            "sympy_bpsw": all(sympy.isprime(q) for q in factors),
            "gmpy2_bpsw": all(bool(gmpy2.is_prime(q)) for q in factors),
            "composite": not bool(gmpy2.is_prime(value)),
            "digit_sum": digsum(value) == sum(digsum(q) for q in factors),
            "digits": len(str(value)) == term["digits"],
            "s_value": digsum(value) == term["digit_sum"],
            "factor_count": len(factors) == term["factor_count"],
            "sha256": hashlib.sha256(str(value).encode()).hexdigest()
            == term["sha256_of_Ln"],
        }
        failed = [k for k, ok in checks.items() if not ok]
        if failed:
            failures.append((n, failed))
        print(f"L({n}): {'OK' if not failed else 'FAIL ' + ','.join(failed)} "
              f"(digits={len(str(value))}, S={digsum(value)}, factors={len(factors)})")

    if failures:
        print(f"\nFAILED: {len(failures)} term(s)")
        return 1
    print(f"\nAll {len(doc['terms'])} terms verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
