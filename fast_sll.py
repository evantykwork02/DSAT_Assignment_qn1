from __future__ import annotations   #To use type hints as strings for cleaner code
from dataclasses import dataclass   #To create simple classes for storing data
from typing import Dict, Generic, Iterator, Optional, TypeVar   #Importing necessary types for type hinting
from node import Node   #Import our node module

T = TypeVar("T")   #creates a placeholder type variable T for generics

@dataclass(frozen=True)
class Position(Generic[T]):
    """
    This class is an immutable reference to a node(Not an index) that enables O(1) all 3 operations:
    get(i), insert, and remove.
    """
    node: Node[T]

class FastSLL(Generic[T]):
    """
    This class is a singly linked list that supports the insert, remove, and get(i) operations in O(1).
    Uses predecessor map to achieve O(1) removal without doubly linking.
    prev[id(node)] = node's predecessor (or None if head)
    """

    #Constructor that runs when list is created.
    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None  #Starts with no first node
        self.tail: Optional[Node[T]] = None  #Starts with no last node

        # Key innovation: prev maps each node to its predecessor, enabling
        # O(1) removal and insert_before in a singly linked list
        self.prev: Dict[int, Optional[Node[T]]] = {}  # maps node_id -> predecessor node
        self._size: int = 0  #Tracks how many nodes are in the list
    
    # Basic helpers

    def __len__(self) -> int:
        """Function to get length of list."""
        return self._size

    def is_empty(self) -> bool:
        """Function to check if list is empty."""
        return self._size == 0

    def first(self) -> Optional[Position[T]]:
        """Function to get first position in list."""
        return Position(self.head) if self.head else None

    def last(self) -> Optional[Position[T]]:
        """Function to get last position in list."""
        return Position(self.tail) if self.tail else None

    def value_iterator(self) -> Iterator[T]:
        """Function to go through the list of nodes and yields the data in each node."""
        cur = self.head
        while cur is not None:
            yield cur.data  #Yield is used to create a generator to produce values 1 at a time as well as for memory efficiency + O(n)
            cur = cur.next

    def _validate(self, pos: Position[T]) -> Node[T]:
        """
        Safety function to ensure position is valid for the list and returns the actual node.
        This is necessary to prevent corruption of the list by foreign positions.
        """    
        node = pos.node
        if id(node) not in self.prev:
            raise ValueError("Invalid/foreign Position (node not in this list).")
        return node

    # Core ADT operations
    
    def get(self, pos: Position[T]) -> T:
        """Function to validate node position and return its value."""
        node = self._validate(pos)
        return node.data

    def append(self, value: T) -> Position[T]:
        """Function to add new node at tail of list."""
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
        """Function to add new node at head of list."""
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
        """Function to insert a new node after the node referenced by the given position."""
        cur = self._validate(pos)
        new_node = Node(value, next=cur.next)
        cur.next = new_node

        self.prev[id(new_node)] = cur

        if new_node.next is not None:  #If there is a node after current node, update predecessor to be new_node not cur anymore
            self.prev[id(new_node.next)] = new_node
        else:
            self.tail = new_node

        self._size += 1
        return Position(new_node)

    def insert_before(self, pos: Position[T], value: T) -> Position[T]:
        """Function to insert before given position. O(1) via predecessor map."""
        target = self._validate(pos)
        pred = self.prev[id(target)]  

        #If no predecessor, target will be head, so can proceeed to call prepend straightaway.
        if pred is None:
            return self.prepend(value)

        new_node = Node(value, next=target)
        pred.next = new_node

        #Updating prev map
        self.prev[id(new_node)] = pred
        self.prev[id(target)] = new_node
        self._size += 1

        return Position(new_node)

    def remove(self, pos: Position[T]) -> T:
        """Function to remove and return element at position in O(1)."""
        target = self._validate(pos)
        pred = self.prev[id(target)]  #find predecessor
        nxt = target.next  #Find next node

        if pred is None:   # Removing head when there is no predecessor
            self.head = nxt
            if nxt is not None:  #If there is a next node, update its predecessor to None
                self.prev[id(nxt)] = None
            else:  # List is now empty
                self.tail = None
        else:  # Removing from middle or tail when predecessor exists
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
        """Function to clear head and tail pointers and prev map in O(1) (No traversal)."""
        self.head = None
        self.tail = None
        self.prev.clear()
        self._size = 0

    def next(self, pos: Position[T]) -> Optional[Position[T]]:
        """Function to return the position of node after the given position."""
        node = self._validate(pos)
        nxt = node.next
        return Position(nxt) if nxt else None  #Return None if no next node (At end of list)