"""Recompute every problem of this set by brute force; the result must equal the option at the key letter and no other option. Run: python pruefung.py"""
from itertools import combinations, permutations


def a1():
    return 3 * 6 - 5


def a2():
    # 4 lines from the top corner meet the base in 4 points; every pair of lines bounds one triangle
    return len(list(combinations(range(4), 2)))


def a3():
    hits = [n for n in range(2, 200, 2) if n // 2 - 4 == 6]
    assert len(hits) == 1
    return hits[0]


def a4():
    kids = ["Ali", "Bea", "Cem", "Dora", "Eva"]
    hits = []
    for order in permutations(kids):
        p = {k: i for i, k in enumerate(order)}  # smaller = faster
        if p["Dora"] < p["Bea"] < p["Eva"] < p["Cem"] and p["Ali"] == 4:
            hits.append(order[2])
    assert len(hits) == 1
    return hits[0]


def a5():
    hits = [k for k in range(0, 9) if 4 * k + 2 * (8 - k) == 22]
    assert len(hits) == 1
    return hits[0]


def a6():
    return sum(str(n).count("3") for n in range(1, 41))


KEY = {1: (a1, [4, 9, 13, 18, 23], "C"), 2: (a2, [3, 4, 5, 6, 7], "D"), 3: (a3, [16, 20, 24, 28, 32], "B"),
       4: (a4, ["Ali", "Bea", "Cem", "Dora", "Eva"], "E"), 5: (a5, [3, 4, 5, 6, 7], "A"), 6: (a6, [4, 10, 13, 14, 15], "D")}

if __name__ == "__main__":
    bad = 0
    for nr, (f, options, letter) in KEY.items():
        got = f()
        ok = len(options) == 5 and options["ABCDE".index(letter)] == got and options.count(got) == 1
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} Aufgabe {nr}: berechnet {got} = ({letter})" if ok
              else f"FAIL Aufgabe {nr}: berechnet {got}, Schluessel ({letter}), Optionen {options}")
    raise SystemExit(1 if bad else 0)
