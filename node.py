from __future__ import annotations
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class Node(Generic[T]):
    """
    Singly linked list node.
    Stores one data item and a pointer to the next node.
    """
    __slots__ = ("data", "next")

    def __init__(self, data: T, next: Optional["Node[T]"] = None) -> None:
        self.data = data
        self.next = next

