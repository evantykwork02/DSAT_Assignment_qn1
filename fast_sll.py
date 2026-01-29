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
    Position-based singly linked list with O(1) operations.
    Uses predecessor map to achieve O(1) removal without doubly linking.
    prev[id(node)] = node's predecessor (or None if head)
    """

    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None

        # Key innovation: prev maps each node to its predecessor, enabling
        # O(1) removal and insert_before in a singly linked list
        self.prev: Dict[int, Optional[Node[T]]] = {}  # maps node_id -> predecessor node
        self._size: int = 0

    
    # Basic helpers
    
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
        """Validate position belongs to this list. O(1) check."""    
        node = pos.node
        if id(node) not in self.prev:
            raise ValueError("Invalid/foreign Position (node not in this list).")
        return node

    
    # Core ADT operations
    
    def get(self, pos: Position[T]) -> T:
        """Return value at position. O(1)."""
        node = self._validate(pos)
        return node.data

    def append(self, value: T) -> Position[T]:
        """Add element to end. O(1)."""
        new_node = Node(value)

        if self.head is None:
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
        """Add element at beginning. O(1)."""
        new_node = Node(value, next=self.head)

        if self.head is None:
            self.head = self.tail = new_node
            self.prev[id(new_node)] = None
        else:
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

        cur.next = new_node

        self.prev[id(new_node)] = cur

        if new_node.next is not None:
            self.prev[id(new_node.next)] = new_node
        else:
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def insert_before(self, pos: Position[T], value: T) -> Position[T]:
        """Insert before given position. O(1) via predecessor map."""
        target = self._validate(pos)
        pred = self.prev[id(target)]  

        if pred is None:
            return self.prepend(value)

        new_node = Node(value, next=target)
        pred.next = new_node

        self.prev[id(new_node)] = pred
        self.prev[id(target)] = new_node

        self._size += 1
        return Position(new_node)

    def remove(self, pos: Position[T]) -> T:
        """Remove and return element at position. O(1)."""
        target = self._validate(pos)
        pred = self.prev[id(target)]  
        nxt = target.next

        if pred is None:
            # Removing head
            self.head = nxt
            if nxt is not None:
                self.prev[id(nxt)] = None
            else:
                self.tail = None
        else:
            # Removing from middle or tail
            pred.next = nxt
            if nxt is not None:
                self.prev[id(nxt)] = pred
            else:
                self.tail = pred

        
        del self.prev[id(target)] # Invalidate position
        self._size -= 1

       
        target.next = None

        return target.data

    def clear(self) -> None:
        """Remove all elements. O(1)."""
        self.head = None
        self.tail = None
        self.prev.clear()
        self._size = 0

    def next(self, pos: Position[T]) -> Optional[Position[T]]:
        """Return next position, or None if at end. O(1)."""
        node = self._validate(pos)
        nxt = node.next
        return Position(nxt) if nxt else None