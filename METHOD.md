# Method, validation and caveats

## Definitions

For an integer `N > 1` with prime factorization `N = ∏ p_i^{a_i}`:

- `S(N)` = sum of decimal digits of `N`,
- `P(N)` = `Σ a_i · S(p_i)`,

with `P` additive: `P(ab) = P(a) + P(b)` for `a, b > 1`.

`N` is a **Smith number** iff `N` is composite and `S(N) = P(N)` [Wilansky 1982].

Lucas numbers satisfy `L_0 = 2`, `L_1 = 1`, `L_{n+2} = L_{n+1} + L_n`, and
`L_n = 2F_{n+1} − F_n`. Fibonacci numbers were computed by fast doubling in
`O(log n)` big-integer operations.

## Source data

Compact BMS-format tables of complete/partial factorizations, maintained by Blair Kelly:

- `https://mersennus.net/fibonacci/fibonacci.txt` — SHA-256 `121e7420972ab1549d84a7128ea084edf80ecf189f664963658e065da3404ac4`
- `https://mersennus.net/fibonacci/lucas.txt` — SHA-256 `874a97343fba23dd58f1266a8c46621d8576634aaa9b2b4d824b811d26f34d62`

Downloaded 2026-11-23. In this format, `(d1,d2,...)` lists subscripts whose
*primitive parts* contribute algebraic factors, and the final token `Pxxx` or
`Cxxx` denotes the largest omitted prime/composite cofactor with `xxx` digits.

## Reconstruction algorithm

For a table entry `E` with value `V(E)`:

1. Recursively obtain the primitive parts of every referenced subscript and multiply
   them into a denominator `D`.
2. Multiply every explicitly listed factor into `D` and into the factor list.
3. For an Aurifeuillian entry with tokens `A`, `B`, compute
   `A = 5F_m² − 5F_m + 1`, `B = 5F_m² + 5F_m + 1` with `n = 5m`, `m` odd, and
   include their complete factorizations.
4. Compute `q, r = divmod(V(E), D)`. Require `r = 0`.
5. If the entry ends in `Pxxx`, require `len(str(q)) = xxx` and `q` prime; add `q`
   to the factor list. If it ends in `Cxxx`, mark the entry incomplete and skip it.
6. The complete factorization of `E` is the union of referenced primitive parts,
   listed factors, and the reconstructed `q`.

For even `n = 2m`, Fibonacci factorizations are obtained from
`F_{2m} = F_m · L_m` (using the identity `P(F_{2m}) = P(F_m) + P(L_m)`).

## Smith test

For each `n`, compute `N = L(n)` (or `F(n)`), verify that the reconstructed factors
multiply back to `N`, that `N` is composite, and that
`S(N) = Σ S(q)` over all factors.

## Validation (control)

The reconstruction was checked against every term already published:

- Fibonacci (OEIS A382922): `31, 77, 231, 354, 523, 535, 631, 819, 827, 830, 991, 1234, 1440, 1554, 1596, 1863, 2256, 2277, 2559`.
- Lucas (OEIS A395686): `3, 95, 105, 114, 183, 437, 609, 682, 827, 902, 1090, 1153, 1215, 1378`.

All 33 control terms were reproduced and all passed the Smith test. Several
published worked examples were also matched exactly (e.g. `S(L_437) = P(L_437) = 416`,
`S(F_77) = P(F_77) = 86`, `S(L_827) = 802`).

## Independent primality checks

Each reconstructed factor of the seven new terms was tested with:

1. Miller–Rabin with 24 random bases (plus small-prime trial division);
2. `sympy.isprime` (Baillie–PSW);
3. `gmpy2.is_prime` (Baillie–PSW with additional checks).

All three agreed on every factor. `L(n)` itself was confirmed composite by the same
tests. BPSW has no known counterexample, but no ECPP certificate is provided, so
this is a probabilistic primality verification, not a formal proof.

## Coverage and known gaps

The scan covered `3 ≤ n < 10000` over entries with complete factorizations.
There are 73 indices between 1378 and 1692 with `Cxxx` cofactors that could not be
tested; therefore the seven reported indices are *additional terms*, not proven to
be the next seven terms of A395686.

No index below 10000 was found for which both `F(n)` and `L(n)` are Smith numbers;
`n = 827` remains the only known common index. A second one would strengthen the
open question posed in arXiv:2609.01955, but none was found in this search.

## References

- A. Wilansky, *Smith numbers*, Two-Year College Math. J. **13** (1982), 21.
- R. P. Dario, J. L. Gonçalves, M. P. N. De Oliveira, *When Fibonacci and Lucas Meet Smith: A Computational Exploration*, arXiv:2609.01955 (2026).
- OEIS A395686 (Lucas–Smith indices), OEIS A382922 (Fibonacci–Smith indices).
- B. Kelly, *Fibonacci and Lucas factorizations*, https://mersennus.net/fibonacci/.
