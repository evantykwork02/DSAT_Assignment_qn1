from __future__ import annotations
import random
from typing import List, Optional   #typing helpers

from fast_sll import FastSLL, Position
from node import Node

#function to print current list contents
def print_list(sll: FastSLL[int]) -> None:
    print("Current list:", list(sll.value_iterator()))

def check_invariants(sll: FastSLL[int]) -> None:
    """
    Ensures list is consistent especially in predecessor part. This function will start from head and perform various checks.
    """
    cur = sll.head   #start traversal from head
    prev: Optional[Node[int]] = None
    count = 0  #counts number of nodes covered

    while cur is not None:   #loops through all the nodes. (Assert helps to raise error if any inconsistency found in nodes)
        assert id(cur) in sll.prev, "Node missing from prev map"
        assert sll.prev[id(cur)] is prev, "prev map incorrect"
        prev = cur   
        cur = cur.next  #move to next node if correct
        count += 1

    assert len(sll) == count, "Size mismatch"
    assert len(sll.prev) == count, "prev-map size mismatch"

    #simple checker to ensure head/tail/prev are correct.
    if count == 0:
        assert sll.head is None and sll.tail is None
    else:
        assert sll.prev[id(sll.head)] is None
        assert sll.tail is not None and sll.tail.next is None

#Function to test for valueError.
def expect_value_error(fn, msg: str) -> None:
    try:
        fn()  #calls the passed function
        raise AssertionError("Expected ValueError but none thrown: " + msg)
    except ValueError:
        print("Correctly raised ValueError:", msg)

#Test 1: Empty list behavior
def test_1_empty_list() -> None:
    print("\n[TEST 1] Empty list behavior")
    sll = FastSLL[int]()
    assert sll.is_empty()  #create empty list and check is_empty
    assert len(sll) == 0
    assert list(sll.value_iterator()) == []
    print("Empty list basics OK")
    check_invariants(sll)

    foreign = Position(Node(999))  #create foreign position not in list to check if ADT will throw error
    expect_value_error(lambda: sll.remove(foreign), "remove(foreign) on empty")
    expect_value_error(lambda: sll.get(foreign), "get(foreign) on empty")
    expect_value_error(lambda: sll.insert_after(foreign, 1), "insert_after(foreign)")
    expect_value_error(lambda: sll.insert_before(foreign, 1), "insert_before(foreign)")
    check_invariants(sll)

#test 2: Single element append/get/remove checker
def test_2_single_element() -> None:
    print("\n[TEST 2] Single element append/get/remove")
    sll = FastSLL[int]()

    p = sll.append(10)
    print(" - append(10)")
    print_list(sll)

    assert sll.get(p) == 10
    print("get(pos) correct")

    removed = sll.remove(p)
    print(" - remove(pos) =>", removed)
    print_list(sll)

    assert removed == 10
    assert sll.is_empty()
    check_invariants(sll)

    # stale position should now be invalid
    expect_value_error(lambda: sll.get(p), "get(stale position)")
    expect_value_error(lambda: sll.remove(p), "remove(stale position)")

#test 3: Insertion at any location
def test_3_insert_any_location() -> None:
    print("\n[TEST 3] Insertion at any location (prepend/insert_before/insert_after/append)")
    sll = FastSLL[int]()

    p20 = sll.append(20)         # [20]
    p10 = sll.prepend(10)        # [10,20]
    p30 = sll.append(30)         # [10,20,30]
    p15 = sll.insert_after(p10, 15)   # [10,15,20,30]
    p25 = sll.insert_before(p30, 25)  # [10,15,20,25,30]

    print_list(sll)

    assert list(sll.value_iterator()) == [10, 15, 20, 25, 30]
    assert sll.get(p10) == 10
    assert sll.get(p15) == 15
    assert sll.get(p20) == 20
    assert sll.get(p25) == 25
    assert sll.get(p30) == 30

    print("All insertion variants correct")
    check_invariants(sll)

#test 4: Removal at head/middle/tail
def test_4_remove_head_mid_tail() -> None:
    print("\n[TEST 4] Removal at head/middle/tail")
    sll = FastSLL[int]()

    p10 = sll.append(10)
    p20 = sll.append(20)
    p30 = sll.append(30)
    p40 = sll.append(40)
    print(" - built [10,20,30,40]")
    print_list(sll)

    assert sll.remove(p10) == 10   # head
    print(" - removed head (10)")
    print_list(sll)
    check_invariants(sll)

    assert sll.remove(p30) == 30   # middle
    print(" - removed middle (30)")
    print_list(sll)
    check_invariants(sll)

    assert sll.remove(p40) == 40   # tail
    print(" - removed tail (40)")
    print_list(sll)
    check_invariants(sll)

    assert sll.remove(p20) == 20   # last remaining
    print(" - removed last (20)")
    print_list(sll)
    check_invariants(sll)

    print("remove(pos) correct for all locations")

#test 5: Foreign position rejection
def test_5_foreign_positions_rejected() -> None:
    print("\n[TEST 5] Foreign positions rejected (robustness)")
    sll = FastSLL[int]()
    p1 = sll.append(1)
    sll.append(2)
    print_list(sll)

    foreign = Position(Node(12345))
    expect_value_error(lambda: sll.get(foreign), "get(foreign)")
    expect_value_error(lambda: sll.remove(foreign), "remove(foreign)")
    expect_value_error(lambda: sll.insert_after(foreign, 9), "insert_after(foreign)")
    expect_value_error(lambda: sll.insert_before(foreign, 9), "insert_before(foreign)")

    assert sll.get(p1) == 1
    print("list unchanged and still valid")
    check_invariants(sll)

#test 6: Random stress test, keep random seed constant and loop fixed.
def test_6_stress_random_ops(seed: int = 7, ops: int = 20000) -> None:
    print("\n[TEST 6] Random stress test (20,000 ops) vs reference model")
    random.seed(seed)  #for reproducibility (important stuff)

    #creates FastSLL and reference model
    sll = FastSLL[int]()
    ref_vals: List[int] = []
    ref_pos: List[Position[int]] = []

    for step in range(ops):
        action = random.choice(["append", "prepend", "insert_after", "insert_before", "remove", "get"])

        if action == "append":
            x = random.randint(-1000, 1000)  #random value to append
            p = sll.append(x)
            ref_vals.append(x)
            ref_pos.append(p)

        elif action == "prepend":
            x = random.randint(-1000, 1000)
            p = sll.prepend(x)
            ref_vals.insert(0, x)
            ref_pos.insert(0, p)

        elif action == "insert_after" and ref_vals:
            k = random.randrange(len(ref_vals))
            x = random.randint(-1000, 1000)
            p_new = sll.insert_after(ref_pos[k], x)
            ref_vals.insert(k + 1, x)
            ref_pos.insert(k + 1, p_new)

        elif action == "insert_before" and ref_vals:
            k = random.randrange(len(ref_vals))
            x = random.randint(-1000, 1000)
            p_new = sll.insert_before(ref_pos[k], x)
            ref_vals.insert(k, x)
            ref_pos.insert(k, p_new)

        elif action == "remove" and ref_vals:
            k = random.randrange(len(ref_vals))
            got = sll.remove(ref_pos[k])
            exp = ref_vals.pop(k)
            ref_pos.pop(k)
            assert got == exp

        elif action == "get" and ref_vals:
            k = random.randrange(len(ref_vals))
            assert sll.get(ref_pos[k]) == ref_vals[k]

        #Added a quick checker for every 5000 operations to ensure ADT performing correctly.
        if step % 5000 == 0 and step != 0:
            check_invariants(sll)
            assert list(sll.value_iterator()) == ref_vals
            print(f"{step} ops OK")

    #Final checks once loop ends
    check_invariants(sll)
    assert list(sll.value_iterator()) == ref_vals
    print("Stress test passed")

#test 7: Clear operation
def test_7_clear() -> None:
    print("\n[TEST 7] clear() operation")
    sll = FastSLL[int]()
    for i in range(10):
        sll.append(i)
    
    sll.clear()
    assert len(sll) == 0
    assert sll.is_empty()
    check_invariants(sll)

    # Verify list works after clear
    sll.append(99)
    assert len(sll) == 1

#test 8: next() navigation
def test_8_next() -> None:
    print("\n[TEST 8] next() navigation")
    sll = FastSLL[int]()
    
    p1 = sll.append(10)
    p2 = sll.append(20)
    p3 = sll.append(30)
    
    assert sll.next(p1) == p2
    assert sll.next(p2) == p3
    assert sll.next(p3) is None
    
    # Test foreign position rejection
    sll2 = FastSLL[int]()
    p_other = sll2.append(99)
    expect_value_error(lambda: sll.next(p_other), "next(foreign)")  #confirm valueError raised
    
    print("next() OK")

#main function starting point (Testing all cases one by one)
def main() -> None:
    print("========== FastSLL Test Cases ==========")

    test_1_empty_list()
    test_2_single_element()
    test_3_insert_any_location()
    test_4_remove_head_mid_tail()
    test_5_foreign_positions_rejected()
    test_6_stress_random_ops()
    test_7_clear()
    test_8_next()

    print("\n ALL TESTS PASSED (edge cases + invariants + stress)")
    print("============================================")

#if run file directly, will just call main function.
if __name__ == "__main__":
    main()
