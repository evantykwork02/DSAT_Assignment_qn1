from __future__ import annotations

import time
from typing import Any, List, Tuple

from fast_sll import FastSLL, Position

#This file is meant to be run to prove O(1) for each of the functions
#Can screenshot console results and use it in report


# ----------------------------
# Count dict operations on prev
# ----------------------------
class CountingDict(dict):
    """
    Wraps a dict and counts basic dictionary operations.
    If your algorithm is O(1), dict ops per method call should be constant across n.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ops = 0

    def reset(self) -> None:
        self.ops = 0

    def __getitem__(self, k):
        self.ops += 1
        return super().__getitem__(k)

    def __setitem__(self, k, v):
        self.ops += 1
        return super().__setitem__(k, v)

    def __delitem__(self, k):
        self.ops += 1
        return super().__delitem__(k)

    def __contains__(self, k):
        self.ops += 1
        return super().__contains__(k)


def attach_counting_prev(sll: FastSLL[Any]) -> CountingDict:
    cd = CountingDict(sll.prev)
    sll.prev = cd
    return cd


def build_list(n: int) -> Tuple[FastSLL[int], List[Position[int]]]:
    sll = FastSLL[int]()
    pos: List[Position[int]] = []
    for i in range(n):
        pos.append(sll.append(i))
    return sll, pos


def fmt_us(x: float) -> str:
    return f"{x:8.3f}"


def main() -> None:
    sizes_ops = [10, 1_000, 100_000, 300_000]
    sizes_time = [1_000, 10_000, 100_000, 300_000]

    reps_get = 200_000
    reps_upd = 50_000

    print("\n==============================")
    print(" FastSLL O(1) Evidence (Console)")
    print(" Position = node reference")
    print("==============================")

    # ----------------------------
    # A) Operation-count evidence
    # ----------------------------
    print("\n[A] Operation-count evidence (prev dict ops per single call)")
    print("    If O(1), counts should stay constant as n grows.\n")

    header = f"{'n':>10} | {'get(pos)':>8} | {'insert_after':>12} | {'remove':>8}"
    print(header)
    print("-" * len(header))

    for n in sizes_ops:
        sll, pos = build_list(n)
        cd = attach_counting_prev(sll)
        mid = pos[n // 2]

        # get(pos)
        cd.reset()
        sll.get(mid)
        ops_get = cd.ops

        # insert_after(pos)
        cd.reset()
        p_new = sll.insert_after(mid, -1)
        ops_ins = cd.ops

        # remove(pos)
        cd.reset()
        sll.remove(p_new)
        ops_rem = cd.ops

        print(f"{n:10d} | {ops_get:8d} | {ops_ins:12d} | {ops_rem:8d}")

    print("\nTip for report: screenshot this table. Constant counts = strong O(1) evidence.")

    # ----------------------------
    # B) Timing evidence
    # ----------------------------
    print("\n[B] Timing evidence (average microseconds per operation)")
    print("    If O(1), μs/op should stay roughly flat as n grows.\n")
    print(f"Repetitions: get={reps_get}, insert/remove={reps_upd}\n")

    header = f"{'n':>10} | {'get μs/op':>10} | {'insert μs/op':>12} | {'remove μs/op':>12}"
    print(header)
    print("-" * len(header))

    for n in sizes_time:
        sll, pos = build_list(n)
        mid = pos[n // 2]

        # get(pos)
        t0 = time.perf_counter()
        for _ in range(reps_get):
            sll.get(mid)
        t1 = time.perf_counter()
        get_us = (t1 - t0) * 1e6 / reps_get

        # insert_after(pos)
        inserted: List[Position[int]] = []
        t0 = time.perf_counter()
        for k in range(reps_upd):
            inserted.append(sll.insert_after(mid, -k))
        t1 = time.perf_counter()
        ins_us = (t1 - t0) * 1e6 / reps_upd

        # remove(pos)
        t0 = time.perf_counter()
        for p in inserted:
            sll.remove(p)
        t1 = time.perf_counter()
        rem_us = (t1 - t0) * 1e6 / reps_upd

        print(f"{n:10d} | {fmt_us(get_us)} | {fmt_us(ins_us)} | {fmt_us(rem_us)}")

    print("\nDone ✅  Screenshot both tables for your report.")


if __name__ == "__main__":
    main()
