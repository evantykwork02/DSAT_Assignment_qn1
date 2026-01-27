"""
This file contains simple correctness tests for FastSLL.

Goal:
- Verify that the list behaves correctly for:
  1) building a list (append)
  2) reading a value at a position (get)
  3) inserting after a position (insert_after)
  4) removing nodes (remove) in the middle, at the head, and at the tail
"""

from fast_sll import FastSLL


def main() -> None:
    # Create an empty FastSLL of integers
    sll = FastSLL[int]()

    # ------------------------------------------------------------
    # Test 1: Append elements to build a list
    # Expected list after appends: 10 -> 20 -> 30
    # append returns a Position handle to the newly added node
    # ------------------------------------------------------------
    p10 = sll.append(10)
    p20 = sll.append(20)
    p30 = sll.append(30)

    # iter_values() walks through the list (for testing only)
    # We check that the list content matches what we expect.
    assert list(sll.iter_values()) == [10, 20, 30], "Append failed to build correct list"

    # ------------------------------------------------------------
    # Test 2: get(pos)
    # Ensure get returns the correct value when given a Position
    # ------------------------------------------------------------
    assert sll.get(p20) == 20, "get(pos) did not return correct value"

    # ------------------------------------------------------------
    # Test 3: Insert after a given position
    # Insert 25 after the node containing 20:
    # Expected: 10 -> 20 -> 25 -> 30
    # ------------------------------------------------------------
    p25 = sll.insert_after(p20, 25)
    assert list(sll.iter_values()) == [10, 20, 25, 30], "insert_after failed"

    # ------------------------------------------------------------
    # Test 4: Remove a middle node
    # Remove the node at p25:
    # Expected: 10 -> 20 -> 30
    # ------------------------------------------------------------
    removed_value = sll.remove(p25)
    assert removed_value == 25, "remove(pos) did not return removed value"
    assert list(sll.iter_values()) == [10, 20, 30], "remove(pos) failed for middle node"

    # ------------------------------------------------------------
    # Test 5: Remove head node
    # Remove the node at p10 (head):
    # Expected: 20 -> 30
    # ------------------------------------------------------------
    assert sll.remove(p10) == 10, "remove(pos) failed for head node"
    assert list(sll.iter_values()) == [20, 30], "List incorrect after removing head"

    # ------------------------------------------------------------
    # Test 6: Remove tail node
    # Remove the node at p30 (tail):
    # Expected: 20
    # ------------------------------------------------------------
    assert sll.remove(p30) == 30, "remove(pos) failed for tail node"
    assert list(sll.iter_values()) == [20], "List incorrect after removing tail"

    # ------------------------------------------------------------
    # Final: Print success if all assertions passed
    # ------------------------------------------------------------
    print("All tests passed ✅")


if __name__ == "__main__":
    # Running this file directly will execute the tests above.
    main()
