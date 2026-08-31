"""
Assignment bot state machine node.

This module defines AssignmentStateNode, a compact representation of a user's
state encoded as a binary string. The bit layout is:

  [ logged_in | (quiz1_assigned, quiz1_completed) | (quiz2_assigned, quiz2_completed) | ... ]

Each quiz consumes two bits: assigned (1/0) then completed (1/0). The first
bit indicates whether the user is logged in.

Behavior:
- Completing quiz N marks quiz N as completed and (if present) assigns quiz N+1.
- The state can be serialized/deserialized to/from a binary string.

Example (3 quizzes):
  logged_in=1, quiz1 assigned/completed=(1,1), quiz2=(1,0), quiz3=(0,0)
  bitstring = "1 11 10 00" -> "111100"

"""
from __future__ import annotations

from typing import List, Optional


class AssignmentStateNode:
    """Represents a user's assignment/completion/login state as a binary string.

    Bits layout:
      index 0: logged_in (1 = logged in, 0 = logged out)
      index 1-2: quiz 1 (assigned, completed)
      index 3-4: quiz 2 (assigned, completed)
      etc.

    The class exposes convenience methods to mutate state (login/logout,
    assign_quiz, complete_quiz) and to serialize/deserialize to bitstrings.
    """

    def __init__(
        self,
        num_quizzes: int,
        bitstring: Optional[str] = None,
        logged_in: Optional[bool] = None,
        assigned: Optional[List[bool]] = None,
        completed: Optional[List[bool]] = None,
    ) -> None:
        if num_quizzes < 1:
            raise ValueError("num_quizzes must be >= 1")
        self.num_quizzes = num_quizzes

        # initialize default lists
        if assigned is None:
            assigned = [False] * num_quizzes
        if completed is None:
            completed = [False] * num_quizzes

        # parse bitstring if provided, otherwise use explicit flags
        if bitstring is not None:
            self._from_bitstring(bitstring)
        else:
            # If logged_in explicitly provided, use it; default False
            self.logged_in = bool(logged_in) if logged_in is not None else False
            if len(assigned) != num_quizzes or len(completed) != num_quizzes:
                raise ValueError("assigned and completed lists must have length num_quizzes")
            self.assigned = list(bool(x) for x in assigned)
            self.completed = list(bool(x) for x in completed)

    # --- internal helpers -------------------------------------------------
    def _from_bitstring(self, bitstring: str) -> None:
        s = bitstring.strip()
        if any(c not in "01" for c in s):
            raise ValueError("bitstring must contain only '0' and '1'")

        expected_len = 1 + 2 * self.num_quizzes
        if len(s) != expected_len:
            raise ValueError(f"bitstring length {len(s)} does not match expected {expected_len}")

        self.logged_in = s[0] == "1"
        self.assigned = []
        self.completed = []
        idx = 1
        for _ in range(self.num_quizzes):
            assigned_bit = s[idx] == "1"
            completed_bit = s[idx + 1] == "1"
            self.assigned.append(assigned_bit)
            self.completed.append(completed_bit)
            idx += 2

    def to_bitstring(self) -> str:
        parts = ["1" if self.logged_in else "0"]
        for a, c in zip(self.assigned, self.completed):
            parts.append("1" if a else "0")
            parts.append("1" if c else "0")
        return "".join(parts)

    # --- state mutations -------------------------------------------------
    def login(self) -> None:
        self.logged_in = True

    def logout(self) -> None:
        self.logged_in = False

    def assign_quiz(self, n: int) -> None:

        self._validate_quiz_index(n)
        self.assigned[n - 1] = True

    def unassign_quiz(self, n: int) -> None:
        self._validate_quiz_index(n)
        self.assigned[n - 1] = False

    def is_assigned(self, n: int) -> bool:
        self._validate_quiz_index(n)
        return bool(self.assigned[n - 1])

    def is_completed(self, n: int) -> bool:
        self._validate_quiz_index(n)
        return bool(self.completed[n - 1])

    def complete_quiz(self, n: int) -> None:
        """Mark quiz n as completed and assign quiz n+1 if it exists.

        If the quiz is already completed this is a no-op. After completion the
        method will ensure the user is assigned the next quiz (n+1) unless the
        next quiz is already completed.
        """
        self._validate_quiz_index(n)
        if self.completed[n - 1]:
            return
        self.completed[n - 1] = True
        self.assigned[n - 1] = True

        next_idx = n
        if next_idx < self.num_quizzes:
            if not self.completed[next_idx]:
                self.assigned[next_idx] = True

    # --- utilities -------------------------------------------------------
    def _validate_quiz_index(self, n: int) -> None:
        if not (1 <= n <= self.num_quizzes):
            raise IndexError(f"quiz index out of range: {n}")

    def summary(self) -> dict:
        return {
            "logged_in": self.logged_in,
            "assigned": list(self.assigned),
            "completed": list(self.completed),
            "bitstring": self.to_bitstring(),
        }

    def __repr__(self) -> str:
        return f"AssignmentStateNode(num_quizzes={self.num_quizzes}, bitstring='{self.to_bitstring()}')"


if __name__ == "__main__":
    node = AssignmentStateNode(num_quizzes=3)
    node.login()
    node.assign_quiz(1)
    print(node)
    node.complete_quiz(1)
    print(node.summary())
