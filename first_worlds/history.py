"""history.py

A minimal undo/redo stack. Stores callables to apply and revert actions.

This is deliberately simple: each action has two functions: do() and undo().
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Action:
    do: Callable[[], None]
    undo: Callable[[], None]


class History:
    def __init__(self) -> None:
        self._done: List[Action] = []
        self._undone: List[Action] = []

    def apply(self, action: Action) -> None:
        action.do()
        self._done.append(action)
        self._undone.clear()

    def undo(self) -> bool:
        if not self._done:
            return False
        action = self._done.pop()
        action.undo()
        self._undone.append(action)
        return True

    def redo(self) -> bool:
        if not self._undone:
            return False
        action = self._undone.pop()
        action.do()
        self._done.append(action)
        return True

    def clear(self) -> None:
        self._done.clear()
        self._undone.clear()
