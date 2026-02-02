from __future__ import annotations

import time
from typing import Any, List, Tuple

from fast_sll import FastSLL, Position


class CountingDict(dict):
    """Counts dict operations."""
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
    print(" FastSLL O(1) Evidence")
    print(" Position = node reference")
    print("==============================")

    # Part A: Operation counts
    print("\n[A] Operation-count evidence (prev dict ops per single call)")
    print("    If O(1), counts should stay constant as n grows.\n")

    header = f"{'n':>10} | {'get':>4} | {'prepend':>7} | {'ins_aft':>7} | {'ins_bef':>7} | {'remove':>6}"
    print(header)
    print("-" * len(header))

    for n in sizes_ops:
        sll, pos = build_list(n)
        cd = attach_counting_prev(sll)
        mid = pos[n // 2]

        cd.reset()
        sll.get(mid)
        ops_get = cd.ops

        cd.reset()
        p_prepend = sll.prepend(-1)
        ops_prepend = cd.ops

        cd.reset()
        p_ins_aft = sll.insert_after(mid, -2)
        ops_ins_aft = cd.ops

        cd.reset()
        p_ins_bef = sll.insert_before(mid, -3)
        ops_ins_bef = cd.ops

        cd.reset()
        sll.remove(p_ins_aft)
        ops_remove = cd.ops

        sll.remove(p_ins_bef)
        sll.remove(p_prepend)

        print(f"{n:10d} | {ops_get:4d} | {ops_prepend:7d} | {ops_ins_aft:7d} | {ops_ins_bef:7d} | {ops_remove:6d}")

    # Part B: Timing
    print("\n[B] Timing evidence (average microseconds per operation)")
    print("    If O(1), μs/op should stay roughly flat as n grows.\n")
    print(f"Repetitions: get={reps_get}, others={reps_upd}\n")

    header = f"{'n':>10} | {'get μs':>7} | {'prepend μs':>10} | {'ins_aft μs':>10} | {'ins_bef μs':>10} | {'remove μs':>9}"
    print(header)
    print("-" * len(header))

    for n in sizes_time:
        sll, pos = build_list(n)
        mid = pos[n // 2]

        t0 = time.perf_counter()
        for _ in range(reps_get):
            sll.get(mid)
        t1 = time.perf_counter()
        get_us = (t1 - t0) * 1e6 / reps_get

        prepended: List[Position[int]] = []
        t0 = time.perf_counter()
        for k in range(reps_upd):
            prepended.append(sll.prepend(-k))
        t1 = time.perf_counter()
        prepend_us = (t1 - t0) * 1e6 / reps_upd

        for p in prepended:
            sll.remove(p)

        ins_aft_positions: List[Position[int]] = []
        t0 = time.perf_counter()
        for k in range(reps_upd):
            ins_aft_positions.append(sll.insert_after(mid, -k))
        t1 = time.perf_counter()
        ins_aft_us = (t1 - t0) * 1e6 / reps_upd

        for p in ins_aft_positions:
            sll.remove(p)

        ins_bef_positions: List[Position[int]] = []
        t0 = time.perf_counter()
        for k in range(reps_upd):
            ins_bef_positions.append(sll.insert_before(mid, -k))
        t1 = time.perf_counter()
        ins_bef_us = (t1 - t0) * 1e6 / reps_upd

        t0 = time.perf_counter()
        for p in ins_bef_positions:
            sll.remove(p)
        t1 = time.perf_counter()
        rem_us = (t1 - t0) * 1e6 / reps_upd

        print(f"{n:10d} | {fmt_us(get_us)} | {fmt_us(prepend_us)} | {fmt_us(ins_aft_us)} | {fmt_us(ins_bef_us)} | {fmt_us(rem_us)}")


if __name__ == "__main__":
    main()