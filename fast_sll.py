# fast_sll.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Generic, Iterator, Optional, TypeVar

from node import Node

T = TypeVar("T")


@dataclass(frozen=True)
class Position(Generic[T]):
    """
    A Position is a handle to a node in the list.
    This is what the assignment refers to as "position i".
    """
    node: Node[T]


class FastSLL(Generic[T]):
    """
    FastSLL implements a singly linked list ADT.

    - The actual data is stored in singly linked list nodes.
    - An auxiliary map (prev) is used to achieve O(1) removal.
    """

    def __init__(self) -> None:
        # Pointer to the first node
        self.head: Optional[Node[T]] = None

        # Pointer to the last node (for O(1) append)
        self.tail: Optional[Node[T]] = None

        # Number of elements in the list
        self._size: int = 0

        # Auxiliary structure:
        # prev[id(node)] = predecessor of node (or None if node is head)
        # This allows O(1) removal in a singly linked list.
        self.prev: Dict[int, Optional[Node[T]]] = {}

    # --------------------------------------------------
    # Basic utility methods
    # --------------------------------------------------

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def first(self) -> Optional[Position[T]]:
        # Return a Position handle to the head node
        return Position(self.head) if self.head else None

    def next(self, pos: Position[T]) -> Optional[Position[T]]:
        # Return the Position of the next node after pos
        nxt = pos.node.next
        return Position(nxt) if nxt else None

    def iter_values(self) -> Iterator[T]:
        # Utility iterator for testing / debugging
        cur = self.head
        while cur:
            yield cur.data
            cur = cur.next

    # --------------------------------------------------
    # Required ADT operations
    # --------------------------------------------------

    def get(self, pos: Position[T]) -> T:
        """
        Return the value stored at a given position.

        O(1) because:
        - Position directly stores a reference to the node
        - No traversal is required
        """
        return pos.node.data

    def append(self, value: T) -> Position[T]:
        """
        Append a new value to the end of the list.

        O(1) because:
        - The tail pointer gives direct access to the last node
        """
        new_node = Node(value)

        if self.head is None:
            # List is empty
            self.head = self.tail = new_node
            self.prev[id(new_node)] = None
        else:
            # Attach new node after current tail
            assert self.tail is not None
            self.tail.next = new_node
            self.prev[id(new_node)] = self.tail
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def insert_after(self, pos: Position[T], value: T) -> Position[T]:
        """
        Insert a new value immediately after the given position.

        O(1) because:
        - We already have direct access to the node at pos
        - Only a constant number of pointer updates are performed
        """
        cur = pos.node
        new_node = Node(value)

        # Save the current next node
        old_next = cur.next

        # Insert new_node after cur
        cur.next = new_node
        new_node.next = old_next

        # Update predecessor map
        self.prev[id(new_node)] = cur

        if old_next is not None:
            # old_next's predecessor is now new_node
            self.prev[id(old_next)] = new_node
        else:
            # cur was the tail, so new_node becomes the new tail
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def remove(self, pos: Position[T]) -> T:
        """
        Remove the node at the given position and return its value.

        O(1) because:
        - The predecessor of the node is retrieved directly from the map
        - No traversal of the list is required
        """
        target = pos.node
        target_id = id(target)

        if target_id not in self.prev:
            raise ValueError("Position does not belong to this list")

        # Retrieve predecessor in O(1)
        pred = self.prev[target_id]
        nxt = target.next

        # Bypass the target node in the singly linked list
        if pred is None:
            # Removing the head node
            self.head = nxt
        else:
            pred.next = nxt

        # Update predecessor map for the next node
        if nxt is not None:
            self.prev[id(nxt)] = pred
        else:
            # Removing the tail node
            self.tail = pred

        # Remove target from predecessor map
        del self.prev[target_id]
        self._size -= 1

        # Reset structure if list becomes empty
        if self._size == 0:
            self.head = None
            self.tail = None
            self.prev.clear()

        return target.data
