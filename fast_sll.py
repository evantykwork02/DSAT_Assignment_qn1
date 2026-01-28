from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Iterator, Optional, TypeVar

from node import Node

T = TypeVar("T")


@dataclass(frozen=True)
class Position(Generic[T]):
    """
    A Position is a handle (reference) to a specific node in the list.
    This is NOT an index.
    Using a Position allows O(1) access (get), insertion, and removal.
    """
    node: Node[T]


class FastSLL(Generic[T]):
    """
    Fast singly linked list ADT (Position-based).

    Requirements satisfied under this interpretation:
      - get(pos): O(1)   (pos directly references a node)
      - insert at a location: O(1) (constant pointer rewiring)
      - remove at a location: O(1) (uses prev-map to find predecessor in O(1))

    Key idea:
      prev_map[id(node)] = predecessor node (or None if node is head)

    Note:
      Python dict operations are assumed O(1) average-case (standard coursework assumption).
    """

    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None
        self.prev: Dict[int, Optional[Node[T]]] = {}  # maps node_id -> predecessor node
        self._size: int = 0

    # -----------------------------
    # Basic helpers
    # -----------------------------
    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def first(self) -> Optional[Position[T]]:
        return Position(self.head) if self.head else None

    def last(self) -> Optional[Position[T]]:
        return Position(self.tail) if self.tail else None

    def iter_values(self) -> Iterator[T]:
        cur = self.head
        while cur is not None:
            yield cur.data
            cur = cur.next

    def _validate(self, pos: Position[T]) -> Node[T]:
        """
        Ensures the given Position belongs to this list and is not stale.
        O(1) check using the prev-map.
        """
        node = pos.node
        if id(node) not in self.prev:
            raise ValueError("Invalid/foreign Position (node not in this list).")
        return node

    # -----------------------------
    # Core ADT operations
    # -----------------------------
    def get(self, pos: Position[T]) -> T:
        """
        O(1): direct node access via Position handle.
        """
        node = self._validate(pos)
        return node.data

    def append(self, value: T) -> Position[T]:
        """
        Append to tail in O(1).
        """
        new_node = Node(value)

        if self.head is None:
            # empty list
            self.head = self.tail = new_node
            self.prev[id(new_node)] = None
        else:
            assert self.tail is not None
            self.prev[id(new_node)] = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def prepend(self, value: T) -> Position[T]:
        """
        Insert at head in O(1).
        """
        new_node = Node(value, next=self.head)

        if self.head is None:
            # empty list
            self.head = self.tail = new_node
            self.prev[id(new_node)] = None
        else:
            # fix old head's predecessor
            old_head = self.head
            self.head = new_node
            self.prev[id(new_node)] = None
            self.prev[id(old_head)] = new_node

        self._size += 1
        return Position(new_node)

    def insert_after(self, pos: Position[T], value: T) -> Position[T]:
        """
        Insert in O(1) after the given position.
        """
        cur = self._validate(pos)
        new_node = Node(value, next=cur.next)

        # link cur -> new_node -> old_next
        cur.next = new_node

        # set predecessor map for new node
        self.prev[id(new_node)] = cur

        # if there was a node after cur, its predecessor becomes new_node
        if new_node.next is not None:
            self.prev[id(new_node.next)] = new_node
        else:
            # inserted at the tail
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def insert_before(self, pos: Position[T], value: T) -> Position[T]:
        """
        Insert in O(1) before the given position.
        Uses prev-map to find predecessor immediately.
        """
        target = self._validate(pos)
        pred = self.prev[id(target)]  # O(1)

        # If inserting before head
        if pred is None:
            return self.prepend(value)

        # Otherwise splice between pred and target
        new_node = Node(value, next=target)
        pred.next = new_node

        # update prev-map
        self.prev[id(new_node)] = pred
        self.prev[id(target)] = new_node

        self._size += 1
        return Position(new_node)

    def remove(self, pos: Position[T]) -> T:
        """
        Remove node at Position in O(1) using prev-map.
        """
        target = self._validate(pos)
        pred = self.prev[id(target)]  # O(1)
        nxt = target.next

        if pred is None:
            # removing head
            self.head = nxt
            if nxt is not None:
                self.prev[id(nxt)] = None
            else:
                # list becomes empty
                self.tail = None
        else:
            # bypass target
            pred.next = nxt
            if nxt is not None:
                self.prev[id(nxt)] = pred
            else:
                # removing tail
                self.tail = pred

        # remove from prev-map so stale Positions become invalid
        del self.prev[id(target)]
        self._size -= 1

        # optional: help debugging (not required)
        target.next = None

        return target.data

    def clear(self) -> None:
        """Remove all elements from the list in O(1)."""
        self.head = None
        self.tail = None
        self.prev.clear()
        self._size = 0

    def next(self, pos: Position[T]) -> Optional[Position[T]]:
        """
        Return Position after given position, or None if at end.
        O(1) operation.
        """
        node = self._validate(pos)
        nxt = node.next
        return Position(nxt) if nxt else None