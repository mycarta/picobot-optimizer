"""
Picobot Simulator
=================

A Python implementation of the Picobot robot simulator, originally developed
for Harvey Mudd College's CS for All (CS5) course.

What is Picobot?
----------------
Picobot is a simple robot that lives on a 2D grid. Its goal is to visit every
empty cell in its environment. The catch: Picobot can only sense its immediate
surroundings (the four adjacent cells) and has a very limited memory (a single
state number from 0 to 99).

Despite these limitations, Picobot can solve surprisingly complex problems
like navigating mazes, using only a small set of rules.

How Picobot Works
-----------------
1. Picobot starts at a random position in state 0.
2. At each step, Picobot checks its surroundings (NEWS: North, East, West, South).
3. It finds a rule that matches its current state and surroundings.
4. It moves in the specified direction and transitions to the new state.
5. Repeat until all cells are visited (success) or no rule matches (failure).

Rule Format
-----------
Rules follow this format:

    STATE SURROUNDINGS -> DIRECTION NEWSTATE

Where:
- STATE: Current state (0-99)
- SURROUNDINGS: 4-character string in NEWS order
    - 'N', 'E', 'W', 'S' = wall in that direction
    - 'x' = open (no wall) in that direction
    - '*' = wildcard (matches either wall or open)
- DIRECTION: Direction to move ('N', 'E', 'W', 'S') or 'X' to stay put
- NEWSTATE: State to transition to (0-99)

Example rule:
    0 x*** -> N 0
    "If in state 0 and nothing is blocking North, move North and stay in state 0"

Usage
-----
    >>> from picobot_simulator import Picobot, Room
    >>>
    >>> # Create an empty 5x5 room
    >>> room = Room.empty_room(5, 5)
    >>>
    >>> # Define some rules
    >>> rules_text = '''
    ... 0 x*** -> N 0
    ... 0 N*** -> X 1
    ... '''
    >>>
    >>> # Create and run the simulator
    >>> bot = Picobot(room, rules_text)
    >>> bot.run(max_steps=1000)
    >>> print(f"Coverage: {bot.coverage_percent():.1f}%")

Author: Matteo Niccoli (original solutions) & Claude (simulator implementation)
License: MIT
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# =============================================================================
# Constants
# =============================================================================

# The four cardinal directions in NEWS order (North, East, West, South)
# This order is canonical for Picobot and must not be changed.
DIRECTIONS = ('N', 'E', 'W', 'S')

# Movement vectors for each direction.
# Note: In our grid, row 0 is the top (North), so moving North decreases row.
MOVE_VECTORS = {
    'N': (-1, 0),   # North: decrease row (move up)
    'E': (0, 1),    # East: increase column (move right)
    'W': (0, -1),   # West: decrease column (move left)
    'S': (1, 0),    # South: increase row (move down)
    'X': (0, 0),    # Stay in place (no movement)
}


# =============================================================================
# Cell Types
# =============================================================================

class Cell(Enum):
    """
    Represents the type of cell in a Picobot room.

    Attributes
    ----------
    EMPTY : int
        An empty cell that Picobot can occupy. Value is 0.
    WALL : int
        A wall cell that Picobot cannot enter. Value is 1.

    Examples
    --------
    >>> cell = Cell.EMPTY
    >>> cell == Cell.WALL
    False
    """

    EMPTY = 0
    WALL = 1


# =============================================================================
# Room Class
# =============================================================================

class Room:
    """
    Represents a 2D grid environment for Picobot.

    The room is a rectangular grid where each cell is either empty (Picobot
    can move there) or a wall (Picobot cannot enter). The room is always
    surrounded by walls on all four sides.

    Parameters
    ----------
    grid : list[list[Cell]]
        A 2D list representing the room layout. Each element is a Cell enum
        value (either Cell.EMPTY or Cell.WALL).

    Attributes
    ----------
    height : int
        The number of rows in the room (including walls).
    width : int
        The number of columns in the room (including walls).
    grid : list[list[Cell]]
        The 2D grid representing the room layout.

    Examples
    --------
    >>> room = Room.empty_room(5, 5)
    >>> room.height
    5
    >>> room.width
    5
    >>> room.is_wall(0, 0)  # Top-left corner is always a wall
    True
    >>> room.is_wall(2, 2)  # Center of a 5x5 room is empty
    False
    """

    def __init__(self, grid: list[list[Cell]]) -> None:
        """
        Initialize a Room with a given grid.

        Parameters
        ----------
        grid : list[list[Cell]]
            A 2D list representing the room layout.

        Raises
        ------
        ValueError
            If the grid is empty or rows have inconsistent lengths.
        """
        # Validate that the grid is not empty
        if not grid or not grid[0]:
            raise ValueError("Grid cannot be empty.")

        # Validate that all rows have the same length
        row_length = len(grid[0])
        for i, row in enumerate(grid):
            if len(row) != row_length:
                raise ValueError(
                    f"Inconsistent row lengths: row 0 has {row_length} columns, "
                    f"but row {i} has {len(row)} columns."
                )

        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])

    def is_wall(self, row: int, col: int) -> bool:
        """
        Check if a cell is a wall.

        Parameters
        ----------
        row : int
            The row index (0-indexed, from top).
        col : int
            The column index (0-indexed, from left).

        Returns
        -------
        bool
            True if the cell is a wall or out of bounds, False if empty.

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> room.is_wall(0, 0)  # Boundary wall
        True
        >>> room.is_wall(2, 2)  # Interior cell
        False
        >>> room.is_wall(100, 100)  # Out of bounds treated as wall
        True
        """
        # Out of bounds is treated as a wall (safety feature)
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return True

        return self.grid[row][col] == Cell.WALL

    def is_empty(self, row: int, col: int) -> bool:
        """
        Check if a cell is empty (not a wall).

        Parameters
        ----------
        row : int
            The row index (0-indexed, from top).
        col : int
            The column index (0-indexed, from left).

        Returns
        -------
        bool
            True if the cell is empty, False if it's a wall or out of bounds.

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> room.is_empty(2, 2)
        True
        >>> room.is_empty(0, 0)
        False
        """
        return not self.is_wall(row, col)

    def count_empty_cells(self) -> int:
        """
        Count the total number of empty cells in the room.

        Returns
        -------
        int
            The number of cells that are not walls.

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> room.count_empty_cells()  # 3x3 interior in a 5x5 room
        9
        """
        count = 0
        for row in self.grid:
            for cell in row:
                if cell == Cell.EMPTY:
                    count += 1
        return count

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """
        Get a list of all empty cell positions.

        Returns
        -------
        list[tuple[int, int]]
            A list of (row, col) tuples for all empty cells.

        Examples
        --------
        >>> room = Room.empty_room(3, 3)
        >>> room.get_empty_cells()
        [(1, 1)]
        """
        empty_cells = []
        for row_idx in range(self.height):
            for col_idx in range(self.width):
                if self.grid[row_idx][col_idx] == Cell.EMPTY:
                    empty_cells.append((row_idx, col_idx))
        return empty_cells

    @classmethod
    def empty_room(cls, height: int, width: int) -> Room:
        """
        Create an empty rectangular room with walls only on the boundary.

        This is the classic "empty room" environment for Picobot. The interior
        is completely open, with walls only on the perimeter.

        Parameters
        ----------
        height : int
            Total height of the room (including walls). Must be at least 3.
        width : int
            Total width of the room (including walls). Must be at least 3.

        Returns
        -------
        Room
            A new Room instance with an empty interior.

        Raises
        ------
        ValueError
            If height or width is less than 3 (minimum for a room with interior).

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> room.is_wall(0, 2)  # Top wall
        True
        >>> room.is_empty(2, 2)  # Center
        True

        Notes
        -----
        The standard Picobot empty room is 25x25, but any size >= 3x3 works.
        """
        if height < 3 or width < 3:
            raise ValueError(
                f"Room must be at least 3x3 to have an interior. "
                f"Got {height}x{width}."
            )

        # Build the grid row by row
        grid = []

        for row_idx in range(height):
            row = []
            for col_idx in range(width):
                # Cell is a wall if it's on the boundary
                is_boundary = (
                    row_idx == 0 or              # Top edge
                    row_idx == height - 1 or     # Bottom edge
                    col_idx == 0 or              # Left edge
                    col_idx == width - 1         # Right edge
                )

                if is_boundary:
                    row.append(Cell.WALL)
                else:
                    row.append(Cell.EMPTY)

            grid.append(row)

        return cls(grid)

    @classmethod
    def from_string(cls, room_string: str) -> Room:
        """
        Create a room from a string representation.

        This is useful for defining custom rooms and mazes. Each character
        represents one cell:
        - '#' or 'W' = Wall
        - '.' or ' ' = Empty

        Parameters
        ----------
        room_string : str
            A multi-line string where each line is a row of the room.
            All lines must have the same length.

        Returns
        -------
        Room
            A new Room instance matching the string layout.

        Raises
        ------
        ValueError
            If the string contains invalid characters or has inconsistent
            row lengths.

        Examples
        --------
        >>> maze_str = '''
        ... #####
        ... #...#
        ... #.#.#
        ... #...#
        ... #####
        ... '''
        >>> room = Room.from_string(maze_str)
        >>> room.is_wall(2, 2)  # The middle '#' in row 2
        True
        """
        # Split into lines and remove empty lines
        lines = [line for line in room_string.strip().split('\n') if line]

        if not lines:
            raise ValueError("Room string cannot be empty.")

        grid = []
        expected_width = len(lines[0])

        for row_idx, line in enumerate(lines):
            # Check consistent width
            if len(line) != expected_width:
                raise ValueError(
                    f"Inconsistent row width: row 0 has {expected_width} chars, "
                    f"but row {row_idx} has {len(line)} chars."
                )

            row = []
            for col_idx, char in enumerate(line):
                if char in ('#', 'W'):
                    row.append(Cell.WALL)
                elif char in ('.', ' '):
                    row.append(Cell.EMPTY)
                else:
                    raise ValueError(
                        f"Invalid character '{char}' at row {row_idx}, "
                        f"col {col_idx}. Use '#' or 'W' for walls, "
                        f"'.' or ' ' for empty cells."
                    )
            grid.append(row)

        return cls(grid)

    def to_string(self, visited: Optional[set[tuple[int, int]]] = None,
                  picobot_pos: Optional[tuple[int, int]] = None) -> str:
        """
        Convert the room to a string representation for display.

        Parameters
        ----------
        visited : set[tuple[int, int]], optional
            A set of (row, col) positions that have been visited.
            Visited cells are shown with a different character.
        picobot_pos : tuple[int, int], optional
            The current position of Picobot as (row, col).

        Returns
        -------
        str
            A multi-line string representation of the room.

        Notes
        -----
        Characters used:
        - '#' = Wall
        - '.' = Empty (not visited)
        - 'o' = Visited
        - 'P' = Picobot's current position

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> print(room.to_string())
        #####
        #...#
        #...#
        #...#
        #####
        """
        if visited is None:
            visited = set()

        lines = []

        for row_idx in range(self.height):
            line = ""
            for col_idx in range(self.width):
                pos = (row_idx, col_idx)

                if picobot_pos is not None and pos == picobot_pos:
                    # Picobot's current position
                    line += 'P'
                elif self.grid[row_idx][col_idx] == Cell.WALL:
                    # Wall
                    line += '#'
                elif pos in visited:
                    # Visited empty cell
                    line += 'o'
                else:
                    # Unvisited empty cell
                    line += '.'

            lines.append(line)

        return '\n'.join(lines)


# =============================================================================
# Rule Parsing and Matching
# =============================================================================

@dataclass
class Rule:
    """
    Represents a single Picobot rule.

    A rule specifies what Picobot should do when it's in a particular state
    and sees a particular pattern of surroundings.

    Parameters
    ----------
    state : int
        The state this rule applies to (0-99).
    surroundings_pattern : str
        A 4-character pattern (NEWS order) that this rule matches.
        Can contain wildcards ('*').
    direction : str
        The direction to move ('N', 'E', 'W', 'S', or 'X' for stay).
    new_state : int
        The state to transition to after this rule fires.
    line_number : int, optional
        The line number in the source file (for error messages).

    Attributes
    ----------
    state : int
        The state this rule applies to.
    surroundings_pattern : str
        The surroundings pattern to match.
    direction : str
        The direction to move.
    new_state : int
        The state to transition to.
    line_number : int
        The source line number (0 if not from a file).

    Examples
    --------
    >>> rule = Rule(0, "x***", "N", 0)
    >>> rule.matches(0, "xxxx")
    True
    >>> rule.matches(0, "Nxxx")
    False
    """

    state: int
    surroundings_pattern: str
    direction: str
    new_state: int
    line_number: int = 0

    def matches(self, current_state: int, surroundings: str) -> bool:
        """
        Check if this rule matches the given state and surroundings.

        Parameters
        ----------
        current_state : int
            Picobot's current state.
        surroundings : str
            The current surroundings as a 4-character string (NEWS order).
            Each character is either the direction letter (wall) or 'x' (open).

        Returns
        -------
        bool
            True if this rule matches, False otherwise.

        Notes
        -----
        A rule matches if:
        1. The state matches exactly.
        2. Each character in the surroundings pattern either:
           - Matches the corresponding surroundings character exactly, or
           - Is a wildcard ('*'), which matches anything.

        Examples
        --------
        >>> rule = Rule(0, "x***", "N", 0)
        >>> rule.matches(0, "xxxx")  # x matches x, * matches anything
        True
        >>> rule.matches(0, "xEWS")  # x matches x, * matches E, W, S
        True
        >>> rule.matches(0, "Nxxx")  # N doesn't match x
        False
        >>> rule.matches(1, "xxxx")  # Wrong state
        False
        """
        # State must match exactly
        if current_state != self.state:
            return False

        # Check each direction (NEWS order)
        for pattern_char, surr_char in zip(self.surroundings_pattern, surroundings):
            # Wildcard matches anything
            if pattern_char == '*':
                continue

            # Non-wildcard must match exactly
            if pattern_char != surr_char:
                return False

        return True

    def __str__(self) -> str:
        """Return a human-readable string representation of the rule."""
        return f"{self.state} {self.surroundings_pattern} -> {self.direction} {self.new_state}"


def parse_rules(rules_text: str) -> list[Rule]:
    """
    Parse a string containing Picobot rules into Rule objects.

    Parameters
    ----------
    rules_text : str
        A string containing one or more Picobot rules, one per line.
        Comments (starting with #) and blank lines are ignored.

    Returns
    -------
    list[Rule]
        A list of Rule objects parsed from the input.

    Raises
    ------
    ValueError
        If any rule has invalid syntax.

    Examples
    --------
    >>> rules_text = '''
    ... # This is a comment
    ... 0 x*** -> N 0
    ... 0 N*** -> E 1
    ... '''
    >>> rules = parse_rules(rules_text)
    >>> len(rules)
    2
    >>> rules[0].direction
    'N'

    Notes
    -----
    Rule syntax:
        STATE SURROUNDINGS -> DIRECTION NEWSTATE

    - STATE: integer 0-99
    - SURROUNDINGS: exactly 4 characters, each one of: N, E, W, S, x, *
    - DIRECTION: one of N, E, W, S, X (X means stay in place)
    - NEWSTATE: integer 0-99

    The arrow (->) is required and can have optional spaces around it.
    """
    rules = []

    # Regular expression to match a rule
    # Format: STATE SURROUNDINGS -> DIRECTION NEWSTATE
    # Example: 0 x*** -> N 0
    rule_pattern = re.compile(
        r'^(\d+)\s+'           # STATE: one or more digits
        r'([NEWSxX*]{4})\s*'   # SURROUNDINGS: exactly 4 characters
        r'->\s*'               # Arrow separator
        r'([NEWSX])\s+'        # DIRECTION: single character
        r'(\d+)\s*$',          # NEWSTATE: one or more digits
        re.IGNORECASE
    )

    for line_num, line in enumerate(rules_text.split('\n'), start=1):
        # Remove comments (everything after #)
        if '#' in line:
            line = line[:line.index('#')]

        # Skip empty lines
        line = line.strip()
        if not line:
            continue

        # Try to match the rule pattern
        match = rule_pattern.match(line)

        if not match:
            raise ValueError(
                f"Invalid rule syntax at line {line_num}: '{line}'\n"
                f"Expected format: STATE SURROUNDINGS -> DIRECTION NEWSTATE\n"
                f"Example: 0 x*** -> N 0"
            )

        # Extract components
        state = int(match.group(1))
        surroundings = match.group(2).upper()  # Normalize to uppercase
        direction = match.group(3).upper()
        new_state = int(match.group(4))

        # Validate state range
        if not 0 <= state <= 99:
            raise ValueError(
                f"Invalid state {state} at line {line_num}. "
                f"State must be between 0 and 99."
            )

        if not 0 <= new_state <= 99:
            raise ValueError(
                f"Invalid new_state {new_state} at line {line_num}. "
                f"State must be between 0 and 99."
            )

        # Normalize surroundings: lowercase 'x' for open, uppercase for walls
        normalized_surroundings = ""
        for i, char in enumerate(surroundings):
            if char == 'X' and i < 4:  # In surroundings, X means open (same as x)
                normalized_surroundings += 'x'
            elif char == '*':
                normalized_surroundings += '*'
            elif char in 'NEWS':
                normalized_surroundings += char
            elif char == 'x':
                normalized_surroundings += 'x'
            else:
                raise ValueError(
                    f"Invalid surroundings character '{char}' at line {line_num}."
                )

        # Create and store the rule
        rule = Rule(
            state=state,
            surroundings_pattern=normalized_surroundings,
            direction=direction,
            new_state=new_state,
            line_number=line_num
        )
        rules.append(rule)

    return rules


# =============================================================================
# Picobot Simulator
# =============================================================================

@dataclass
class SimulationStep:
    """
    Records a single step in the Picobot simulation.

    This is useful for debugging, visualization, and understanding how
    Picobot navigates the environment.

    Attributes
    ----------
    step_number : int
        The step number (0-indexed).
    position : tuple[int, int]
        Picobot's position as (row, col) at the START of this step.
    state : int
        Picobot's state at the START of this step.
    surroundings : str
        The surroundings string at this position.
    rule_applied : Rule | None
        The rule that was applied (None if no matching rule).
    new_position : tuple[int, int]
        Picobot's position AFTER this step.
    new_state : int
        Picobot's state AFTER this step.
    """

    step_number: int
    position: tuple[int, int]
    state: int
    surroundings: str
    rule_applied: Optional[Rule]
    new_position: tuple[int, int]
    new_state: int


class Picobot:
    """
    The main Picobot simulator class.

    This class manages the simulation of a Picobot navigating a room using
    a set of rules. It tracks the robot's position, state, visited cells,
    and provides methods to run the simulation and analyze coverage.

    Parameters
    ----------
    room : Room
        The room environment for Picobot to navigate.
    rules : str | list[Rule]
        Either a string containing rules (to be parsed) or a list of
        Rule objects.
    start_position : tuple[int, int], optional
        The starting position as (row, col). If None, Picobot starts at
        the first empty cell found (top-to-bottom, left-to-right).

    Attributes
    ----------
    room : Room
        The room environment.
    rules : list[Rule]
        The list of rules governing Picobot's behavior.
    position : tuple[int, int]
        Current position as (row, col).
    state : int
        Current state (0-99).
    visited : set[tuple[int, int]]
        Set of all visited positions.
    history : list[SimulationStep]
        Record of all simulation steps taken.

    Examples
    --------
    >>> room = Room.empty_room(5, 5)
    >>> rules = '''
    ... 0 x*** -> N 0
    ... 0 N*** -> X 1
    ... '''
    >>> bot = Picobot(room, rules)
    >>> bot.step()  # Take one step
    True
    >>> print(f"Position: {bot.position}, State: {bot.state}")
    """

    def __init__(
        self,
        room: Room,
        rules: str | list[Rule],
        start_position: Optional[tuple[int, int]] = None
    ) -> None:
        """
        Initialize the Picobot simulator.

        Parameters
        ----------
        room : Room
            The room environment.
        rules : str | list[Rule]
            Rules as a string (to be parsed) or list of Rule objects.
        start_position : tuple[int, int], optional
            Starting position. Defaults to first empty cell.

        Raises
        ------
        ValueError
            If start_position is a wall or out of bounds.
        """
        self.room = room

        # Parse rules if given as string
        if isinstance(rules, str):
            self.rules = parse_rules(rules)
        else:
            self.rules = rules

        # Find starting position
        if start_position is None:
            # Default to first empty cell
            empty_cells = room.get_empty_cells()
            if not empty_cells:
                raise ValueError("Room has no empty cells!")
            start_position = empty_cells[0]
        else:
            # Validate provided position
            row, col = start_position
            if room.is_wall(row, col):
                raise ValueError(
                    f"Starting position ({row}, {col}) is a wall or out of bounds."
                )

        self.position = start_position
        self.state = 0  # Picobot always starts in state 0

        # Track visited cells (starting position counts as visited)
        self.visited: set[tuple[int, int]] = {start_position}

        # Record simulation history
        self.history: list[SimulationStep] = []

        # Simulation status
        self._halted = False
        self._halt_reason = ""

    def get_surroundings(self) -> str:
        """
        Get Picobot's current surroundings as a NEWS string.

        Returns
        -------
        str
            A 4-character string representing surroundings in NEWS order.
            Each character is either the direction letter (wall present)
            or 'x' (no wall / open).

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> bot = Picobot(room, [], start_position=(1, 1))
        >>> bot.get_surroundings()  # Top-left interior corner
        'NxWx'
        """
        row, col = self.position
        surroundings = ""

        # Check each direction in NEWS order
        for direction in DIRECTIONS:
            d_row, d_col = MOVE_VECTORS[direction]
            neighbor_row = row + d_row
            neighbor_col = col + d_col

            if self.room.is_wall(neighbor_row, neighbor_col):
                # Wall in this direction: use the direction letter
                surroundings += direction
            else:
                # Open in this direction: use 'x'
                surroundings += 'x'

        return surroundings

    def find_matching_rule(self, state: int, surroundings: str) -> Optional[Rule]:
        """
        Find the first rule that matches the given state and surroundings.

        Parameters
        ----------
        state : int
            The current state.
        surroundings : str
            The current surroundings string.

        Returns
        -------
        Rule | None
            The first matching rule, or None if no rule matches.

        Notes
        -----
        Rules are checked in order. The first matching rule is used.
        This means rule order matters when multiple rules could match!
        """
        for rule in self.rules:
            if rule.matches(state, surroundings):
                return rule
        return None

    def step(self) -> bool:
        """
        Execute a single simulation step.

        Returns
        -------
        bool
            True if the step was successful, False if simulation has halted.

        Notes
        -----
        A step consists of:
        1. Check if already halted -> return False
        2. Get current surroundings
        3. Find a matching rule
        4. If no rule matches -> halt
        5. Move in the specified direction (if valid)
        6. Update state
        7. Mark new position as visited
        8. Record the step in history
        """
        # Check if already halted
        if self._halted:
            return False

        # Get current state
        current_position = self.position
        current_state = self.state
        surroundings = self.get_surroundings()

        # Find matching rule
        rule = self.find_matching_rule(current_state, surroundings)

        if rule is None:
            # No matching rule - halt
            self._halted = True
            self._halt_reason = (
                f"No rule matches state {current_state} "
                f"with surroundings {surroundings}"
            )

            # Record the failed step
            self.history.append(SimulationStep(
                step_number=len(self.history),
                position=current_position,
                state=current_state,
                surroundings=surroundings,
                rule_applied=None,
                new_position=current_position,
                new_state=current_state
            ))
            return False

        # Calculate new position
        d_row, d_col = MOVE_VECTORS[rule.direction]
        new_row = current_position[0] + d_row
        new_col = current_position[1] + d_col
        new_position = (new_row, new_col)

        # Validate move (can't move into a wall)
        if self.room.is_wall(new_row, new_col):
            self._halted = True
            self._halt_reason = (
                f"Rule '{rule}' tried to move into wall at ({new_row}, {new_col})"
            )

            # Record the failed step
            self.history.append(SimulationStep(
                step_number=len(self.history),
                position=current_position,
                state=current_state,
                surroundings=surroundings,
                rule_applied=rule,
                new_position=current_position,  # Didn't actually move
                new_state=current_state
            ))
            return False

        # Execute the move
        self.position = new_position
        self.state = rule.new_state
        self.visited.add(new_position)

        # Record successful step
        self.history.append(SimulationStep(
            step_number=len(self.history),
            position=current_position,
            state=current_state,
            surroundings=surroundings,
            rule_applied=rule,
            new_position=new_position,
            new_state=rule.new_state
        ))

        return True

    def run(
        self,
        max_steps: int = 10000,
        stop_on_full_coverage: bool = True,
        verbose: bool = False
    ) -> dict:
        """
        Run the simulation until completion or max steps reached.

        Parameters
        ----------
        max_steps : int, optional
            Maximum number of steps to run. Default is 10000.
        stop_on_full_coverage : bool, optional
            If True, stop when all empty cells have been visited.
            Default is True.
        verbose : bool, optional
            If True, print progress information. Default is False.

        Returns
        -------
        dict
            A dictionary containing:
            - 'success': bool - True if full coverage achieved
            - 'steps': int - Number of steps taken
            - 'coverage': float - Percentage of cells covered (0-100)
            - 'visited': int - Number of cells visited
            - 'total': int - Total number of empty cells
            - 'halted': bool - True if simulation halted early
            - 'halt_reason': str - Reason for halt (if any)

        Examples
        --------
        >>> room = Room.empty_room(5, 5)
        >>> rules = "0 x*** -> N 0\\n0 N*** -> E 1"
        >>> bot = Picobot(room, rules)
        >>> result = bot.run(max_steps=100)
        >>> print(f"Coverage: {result['coverage']:.1f}%")
        """
        total_empty = self.room.count_empty_cells()
        steps_taken = 0

        for step in range(max_steps):
            # Check for full coverage
            if stop_on_full_coverage and len(self.visited) >= total_empty:
                if verbose:
                    print(f"Full coverage achieved in {step} steps!")
                break

            # Take a step
            success = self.step()
            steps_taken = step + 1

            if not success:
                if verbose:
                    print(f"Simulation halted at step {step}: {self._halt_reason}")
                break

            if verbose and step % 1000 == 0 and step > 0:
                coverage = 100 * len(self.visited) / total_empty
                print(f"Step {step}: {coverage:.1f}% coverage")

        # Compile results
        coverage_percent = 100 * len(self.visited) / total_empty

        return {
            'success': len(self.visited) >= total_empty,
            'steps': steps_taken,
            'coverage': coverage_percent,
            'visited': len(self.visited),
            'total': total_empty,
            'halted': self._halted,
            'halt_reason': self._halt_reason
        }

    def coverage_percent(self) -> float:
        """
        Get the current coverage percentage.

        Returns
        -------
        float
            Percentage of empty cells that have been visited (0-100).
        """
        total = self.room.count_empty_cells()
        if total == 0:
            return 100.0
        return 100 * len(self.visited) / total

    def is_complete(self) -> bool:
        """
        Check if Picobot has visited all empty cells.

        Returns
        -------
        bool
            True if all empty cells have been visited.
        """
        return len(self.visited) >= self.room.count_empty_cells()

    def display(self) -> str:
        """
        Get a string representation of the current room state.

        Returns
        -------
        str
            A multi-line string showing the room with Picobot's position
            and visited cells marked.
        """
        return self.room.to_string(
            visited=self.visited,
            picobot_pos=self.position
        )

    def reset(self, start_position: Optional[tuple[int, int]] = None) -> None:
        """
        Reset the simulation to its initial state.

        Parameters
        ----------
        start_position : tuple[int, int], optional
            New starting position. If None, uses the first empty cell.
        """
        if start_position is None:
            empty_cells = self.room.get_empty_cells()
            if empty_cells:
                start_position = empty_cells[0]
            else:
                raise ValueError("Room has no empty cells!")

        self.position = start_position
        self.state = 0
        self.visited = {start_position}
        self.history = []
        self._halted = False
        self._halt_reason = ""


# =============================================================================
# Utility Functions
# =============================================================================

def test_rules_all_positions(
    room: Room,
    rules: str | list[Rule],
    max_steps: int = 10000,
    verbose: bool = False
) -> dict:
    """
    Test a set of rules from every possible starting position.

    This is the true test of a Picobot solution: it must achieve full
    coverage regardless of where Picobot starts.

    Parameters
    ----------
    room : Room
        The room to test in.
    rules : str | list[Rule]
        The rules to test.
    max_steps : int, optional
        Maximum steps per run. Default is 10000.
    verbose : bool, optional
        If True, print progress. Default is False.

    Returns
    -------
    dict
        A dictionary containing:
        - 'success': bool - True if full coverage from ALL positions
        - 'positions_tested': int - Number of starting positions tested
        - 'positions_passed': int - Number that achieved full coverage
        - 'failures': list - List of (position, result) for failures
        - 'max_steps_used': int - Maximum steps needed across all runs
        - 'avg_steps': float - Average steps to completion

    Examples
    --------
    >>> room = Room.empty_room(5, 5)
    >>> rules = "0 x*** -> N 0"  # Incomplete rules
    >>> result = test_rules_all_positions(room, rules)
    >>> result['success']
    False
    """
    empty_cells = room.get_empty_cells()
    failures = []
    steps_list = []
    passed = 0

    for i, start_pos in enumerate(empty_cells):
        if verbose:
            print(f"Testing position {i+1}/{len(empty_cells)}: {start_pos}")

        # Create fresh simulator
        bot = Picobot(room, rules, start_position=start_pos)
        result = bot.run(max_steps=max_steps, verbose=False)

        if result['success']:
            passed += 1
            steps_list.append(result['steps'])
        else:
            failures.append((start_pos, result))

    return {
        'success': len(failures) == 0,
        'positions_tested': len(empty_cells),
        'positions_passed': passed,
        'failures': failures,
        'max_steps_used': max(steps_list) if steps_list else 0,
        'avg_steps': sum(steps_list) / len(steps_list) if steps_list else 0
    }


def count_rules(rules: str | list[Rule]) -> int:
    """
    Count the number of rules in a ruleset.

    Parameters
    ----------
    rules : str | list[Rule]
        Rules as a string or list.

    Returns
    -------
    int
        The number of rules.
    """
    if isinstance(rules, str):
        rules = parse_rules(rules)
    return len(rules)


def count_states(rules: str | list[Rule]) -> int:
    """
    Count the number of distinct states used in a ruleset.

    Parameters
    ----------
    rules : str | list[Rule]
        Rules as a string or list.

    Returns
    -------
    int
        The number of unique states referenced (both current and new states).
    """
    if isinstance(rules, str):
        rules = parse_rules(rules)

    states = set()
    for rule in rules:
        states.add(rule.state)
        states.add(rule.new_state)

    return len(states)


# =============================================================================
# Main - Demo
# =============================================================================

if __name__ == "__main__":
    # Demo: Run a simple test
    print("=" * 60)
    print("Picobot Simulator Demo")
    print("=" * 60)

    # Create a small empty room
    room = Room.empty_room(7, 7)
    print("\nEmpty 7x7 room:")
    print(room.to_string())

    # Simple rules: just go North until hitting a wall
    demo_rules = """
    # Go North until we hit a wall
    0 x*** -> N 0

    # When we hit the North wall, go East
    0 N*x* -> E 0

    # If we hit NE corner, go South
    0 NEx* -> S 1

    # In state 1, keep going South
    1 ***x -> S 1

    # If we hit South wall, go West
    1 ***S -> W 1

    # If we hit SW corner, go North
    1 **WS -> N 0
    """

    print("\nDemo rules:")
    for rule in parse_rules(demo_rules):
        print(f"  {rule}")

    print(f"\nRule count: {count_rules(demo_rules)}")
    print(f"State count: {count_states(demo_rules)}")

    # Run simulation
    bot = Picobot(room, demo_rules, start_position=(3, 3))
    print(f"\nStarting position: {bot.position}")
    print(f"Initial state: {bot.state}")

    result = bot.run(max_steps=200, verbose=True)

    print(f"\nFinal state:")
    print(bot.display())
    print(f"\nCoverage: {result['coverage']:.1f}%")
    print(f"Steps taken: {result['steps']}")
    print(f"Success: {result['success']}")
