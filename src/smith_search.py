#!/usr/bin/env python3
"""Busca números de Smith nas sequências de Fibonacci e Lucas.

Reconstrói fatorações completas a partir das tabelas compactas de Blair Kelly
(https://mersennus.net/fibonacci/) e testa S(N) = P(N).

Uso:
    python3 scripts/smith_search.py --limit 10000
    python3 scripts/smith_search.py --verify-only 1692 1770 1798 1865 1899 2331
"""
import argparse
import os
import re
import urllib.request
from functools import lru_cache

BASE = "https://mersennus.net/fibonacci/"
FILES = {"fibonacci.txt": BASE + "fibonacci.txt", "lucas.txt": BASE + "lucas.txt"}


def get_table(name, cache):
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        os.makedirs(cache, exist_ok=True)
        urllib.request.urlretrieve(FILES[name], path)
    return path


@lru_cache(maxsize=None)
def fib_pair(n):
    if n == 0:
        return (0, 1)
    a, b = fib_pair(n >> 1)
    c, d = a * (2 * b - a), a * a + b * b
    return (d, c + d) if n & 1 else (c, d)


def F(n):
    return fib_pair(n)[0]


def L(n):
    return 2 if n == 0 else 2 * F(n + 1) - F(n)


def digsum(n):
    return sum(map(int, str(n)))


def is_prime(n, rounds=24):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    import random
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in list((2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)) + [
        random.randrange(2, n - 1) for _ in range(rounds)
    ]:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def load_entries(cache):
    entries = {}
    pattern = re.compile(r"^([FL]\d+[AB]?)\s+(?:\(([^)]*)\)\s*)?(.*)$")
    for name, prefix in (("fibonacci.txt", "F"), ("lucas.txt", "L")):
        with open(get_table(name, cache), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line.startswith(prefix):
                    continue
                m = pattern.match(line)
                if not m:
                    continue
                key, refs, rest = m.group(1), m.group(2), m.group(3).strip()
                refs = [r.strip() for r in refs.split(",") if r.strip()] if refs else []
                toks = [t.strip() for t in rest.split(".") if t.strip()]
                entries[key] = (refs, toks)
    return entries


class Search:
    def __init__(self, cache):
        self.entries = load_entries(cache)
        self.memo = {}

    def value(self, key):
        n = int(key[1:].rstrip("AB"))
        suffix = key[-1] if key[-1] in "AB" else ""
        if suffix == "A":
            f = F(n // 5)
            return 5 * f * f - 5 * f + 1
        if suffix == "B":
            f = F(n // 5)
            return 5 * f * f + 5 * f + 1
        return F(n) if key[0] == "F" else L(n)

    def primitive(self, key):
        """Fatores primos da parte primitiva de `key` (sem referências algébricas)."""
        if key in self.memo:
            return self.memo[key]
        refs, toks = self.entries[key]
        prod, factors = 1, []
        for ref in refs:
            rk = ref if ref.startswith(("F", "L")) else key[0] + ref
            rf, ok = self.primitive(rk) if rk in self.entries else (None, False)
            if not ok:
                self.memo[key] = ([], False)
                return self.memo[key]
            for q in rf:
                prod *= q
        bigtok = None
        for tok in toks:
            tok = tok.rstrip("*")
            if tok.isdigit():
                q = int(tok)
                factors.append(q)
                prod *= q
            elif tok[0] == "P":
                bigtok = tok
            elif tok[0] == "C":
                self.memo[key] = ([], False)  # cofactor composto desconhecido
                return self.memo[key]
            elif tok in ("A", "B"):
                sub = key + tok
                if sub not in self.entries:
                    self.memo[key] = ([], False)
                    return self.memo[key]
                sf, ok = self.entry_factors(sub)
                if not ok:
                    self.memo[key] = ([], False)
                    return self.memo[key]
                for q in sf:
                    prod *= q
            else:
                raise ValueError((key, tok))
        quot, rem = divmod(self.value(key), prod)
        if rem != 0:
            self.memo[key] = ([], False)
            return self.memo[key]
        if bigtok is not None:
            want = int(bigtok[1:])
            if len(str(quot)) != want or not is_prime(quot):
                self.memo[key] = ([], False)
                return self.memo[key]
            factors.append(quot)
        elif quot != 1:
            self.memo[key] = ([], False)
            return self.memo[key]
        self.memo[key] = (sorted(factors), True)
        return self.memo[key]

    def entry_factors(self, key):
        """(fatoração prima completa, ok) da entrada `key`."""
        refs, toks = self.entries[key]
        fs = []
        for ref in refs:
            rk = ref if ref.startswith(("F", "L")) else key[0] + ref
            rf, ok = self.primitive(rk)
            if not ok:
                return [], False
            fs += rf
        pf, ok = self.primitive(key)
        if not ok:
            return [], False
        fs += pf
        for tok in toks:
            if tok in ("A", "B"):
                sub = key + tok
                sf, ok = self.entry_factors(sub) if sub in self.entries else ([], False)
                if not ok:
                    return [], False
                fs += sf
        return sorted(fs), True

    def factors(self, key):
        fs, ok = self.entry_factors(key)
        return fs if ok else None


def is_smith(n, factors, rounds=24):
    prod = 1
    for q in factors:
        prod *= q
    return (
        prod == n
        and n > 1
        and not is_prime(n, rounds)
        and digsum(n) == sum(digsum(q) for q in factors)
        and all(is_prime(q, rounds) for q in factors)
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--cache", default=".cache")
    ap.add_argument("--verify-only", type=int, nargs="*")
    args = ap.parse_args()

    s = Search(args.cache)
    if args.verify_only:
        for n in args.verify_only:
            for tag in ("F", "L"):
                fs = s.factors(f"{tag}{n}")
                if fs is None:
                    print(f"{tag}({n}): fatoração incompleta")
                    continue
                num = F(n) if tag == "F" else L(n)
                print(
                    f"{tag}({n}): digits={len(str(num))} "
                    f"S={digsum(num)} P={sum(digsum(q) for q in fs)} "
                    f"smith={is_smith(num, fs, 40)}"
                )
        return

    fsmith, lsmith, ffac, lfac = [], [], {}, {}
    for n in range(3, args.limit):
        lf = s.factors(f"L{n}")
        if lf:
            lfac[n] = lf
            if is_smith(L(n), lf):
                lsmith.append(n)
        if n & 1:
            ff = s.factors(f"F{n}")
        else:
            fm, lm = ffac.get(n // 2), lfac.get(n // 2)
            ff = sorted(fm + lm) if fm and lm else None
        if ff:
            ffac[n] = ff
            if is_smith(F(n), ff):
                fsmith.append(n)

    print("F Smith:", fsmith)
    print("L Smith:", lsmith)
    print("COMMON:", sorted(set(fsmith) & set(lsmith)))


if __name__ == "__main__":
    main()
