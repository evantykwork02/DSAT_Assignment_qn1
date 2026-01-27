# node.py

"""
PSEUDOCODE (Node structure):

STRUCT Node
    data        // element stored in the list
    next        // reference to next node (or null)
END STRUCT
"""

from __future__ import annotations
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class Node(Generic[T]):
    __slots__ = ("data", "next")

    def __init__(self, data: T, next: Optional["Node[T]"] = None) -> None:
        self.data = data
        self.next = next

    def __repr__(self) -> str:
        return f"Node({self.data})"
