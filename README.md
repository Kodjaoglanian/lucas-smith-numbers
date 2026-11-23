# Seven additional Lucas–Smith numbers

**Dataset and reproducible search for new indices `n` such that the Lucas number `L(n)` is a Smith number.**

## Summary

A **Smith number** is a composite integer whose decimal digit sum equals the sum of the decimal digits of its prime factors, counted with multiplicity. This repository reports **seven additional indices** for which the Lucas number `L(n)` is a Smith number:

> **1692, 1770, 1798, 1865, 1899, 2331, 7474**

The published sequence [OEIS A395686](https://oeis.org/A395686) previously ended at `1378`, with the explicit comment `a(15) >= 1423` (entry last modified 2026-09-06). A 2026 paper ([Dario, Gonçalves & Oliveira, arXiv:2609.01955](https://arxiv.org/abs/2609.01955)) asked whether further Lucas–Smith terms exist and noted that complete factorizations are the limiting factor.

Each index reported here was obtained by reconstructing a **complete prime factorization** from the compact factorization tables of Blair Kelly and testing the Smith condition exactly. The largest new term, `L(7474)`, has 1562 decimal digits.

## Results

| `n` | digits of `L(n)` | `S(L(n)) = P(L(n))` | distinct prime factors (with multiplicity) |
|----:|-----------------:|--------------------:|-------------------------------------------:|
| 1692 | 354 | 1609 | 14 |
| 1770 | 370 | 1674 | 15 |
| 1798 | 376 | 1695 | 9 |
| 1865 | 390 | 1753 | 10 |
| 1899 | 397 | 1777 | 9 |
| 2331 | 488 | 2101 | 22 |
| 7474 | 1562 | 6963 | 7 |

Machine-readable factorizations, SHA-256 checksums of each `L(n)`, and source-table hashes are in [`data/lucas_smith_terms.json`](data/lucas_smith_terms.json).

## Method

1. Download the compact BMS-format factorization tables from
   [mersennus.net/fibonacci](https://mersennus.net/fibonacci/). Algebraic factors are
   encoded as subscript references; the largest factor is omitted as `Pxxx` (prime)
   or `Cxxx` (composite).
2. Reconstruct each omitted factor by exact division:
   `P = L(n) / (algebraic part × listed factors)`, requiring exactly `xxx` digits and
   primality. Entries containing `Cxxx` are marked incomplete and excluded.
   Aurifeuillian factors of `L(5m)` are rebuilt from
   `A = 5F_m² − 5F_m + 1`, `B = 5F_m² + 5F_m + 1` (`m` odd).
3. Apply `S(N) = P(N)`, with `P` additive under multiplication, and require `N` composite.

Details, including validation against all previously known terms, are in [`METHOD.md`](METHOD.md).

## Verification

For each of the seven terms we checked that:

- the product of the reconstructed prime factors is **exactly** `L(n)`;
- every factor passes three independent primality tests: Miller–Rabin (24 rounds),
  `sympy.isprime` (BPSW) and `gmpy2.is_prime` (BPSW);
- `S(L(n)) = P(L(n))` and `L(n)` is composite.

The reconstruction code also reproduces **all 14 previously published Lucas–Smith indices** and all 19 published Fibonacci–Smith indices, which is a strong control against parser errors.

Run the independent verifier:

```bash
python3 -m pip install -r requirements.txt
python3 verify.py
```

## Scope and limitations

- These are **additional terms**, not necessarily the *next* terms. Between `1378` and `1692` there are **73 indices whose factorizations are incomplete** in the source tables; they could not be tested. No claim is made that `1692 = a(15)`.
- The search covered `n < 10000` and found no second index where both `F(n)` and `L(n)` are Smith numbers; `n = 827` remains the only known such index.
- BPSW has no known counterexample but is not a deterministic primality proof. ECPP certificates are **not** supplied. This is sufficient for a database extension, not for a formal primality claim in a journal article.

## Repository layout

| Path | Contents |
|---|---|
| `README.md` | This summary |
| `METHOD.md` | Full method, validation, and caveats |
| `data/lucas_smith_terms.json` | Complete factorizations and checksums |
| `src/smith_search.py` | Reproducible search / reconstruction script |
| `verify.py` | Independent verification of the dataset |
| `CITATION.cff` | Citation metadata |
| `LICENSE` | MIT license |

## Reproducing the search

```bash
python3 -m pip install -r requirements.txt
python3 src/smith_search.py --limit 10000
python3 src/smith_search.py --verify-only 1692 7474
```

The script caches downloaded tables in `./.cache/` by default.

## Sources and attribution

Factorization tables: **Blair Kelly**, *Fibonacci and Lucas factorizations*, <https://mersennus.net/fibonacci/>. SHA-256 of the exact files used are pinned in [`data/lucas_smith_terms.json`](data/lucas_smith_terms.json).

Smith numbers: Wilansky (1982). Lucas–Smith sequence: OEIS A395686 (R. P. Dario, 2026); Fibonacci–Smith sequence: OEIS A382922. The open question about a second common Fibonacci/Lucas index comes from arXiv:2609.01955.

## Cite

See [`CITATION.cff`](CITATION.cff).

## License

MIT — see [`LICENSE`](LICENSE). The underlying factorization tables are third-party data and remain the property of their maintainer; they are not redistributed here.
