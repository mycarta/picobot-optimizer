"""
Picobot Room and Maze Builder
=============================

This module provides tools for creating various Picobot environments,
including the standard empty room and maze configurations used in the
Harvey Mudd CS for All course.

The two canonical environments are:
1. **Empty Room**: A rectangular room with walls only on the boundary.
2. **Maze**: A maze with corridors one square wide, where all walls are
   connected to the outer boundary.

Usage
-----
    >>> from picobot_rooms import create_empty_room, create_standard_maze
    >>>
    >>> # Standard 25x25 empty room
    >>> empty = create_empty_room()
    >>>
    >>> # Standard Picobot maze
    >>> maze = create_standard_maze()

Author: Matteo Niccoli (original solutions) & Claude (implementation)
License: MIT
"""

from __future__ import annotations

from picobot.simulator import Room, Cell


# =============================================================================
# Standard Room Dimensions
# =============================================================================

# The standard Picobot room size used in most courses
STANDARD_SIZE = 25


# =============================================================================
# Empty Room Factory
# =============================================================================

def create_empty_room(
    height: int = STANDARD_SIZE,
    width: int = STANDARD_SIZE
) -> Room:
    """
    Create a standard empty room for Picobot.

    The empty room is the first challenge in the Picobot curriculum. It's a
    simple rectangular space with walls on all four sides and a completely
    open interior. The goal is to write rules that allow Picobot to visit
    every interior cell regardless of starting position.

    Parameters
    ----------
    height : int, optional
        The total height of the room including walls. Default is 25.
    width : int, optional
        The total width of the room including walls. Default is 25.

    Returns
    -------
    Room
        A Room object with walls on the boundary and empty interior.

    Examples
    --------
    >>> room = create_empty_room()
    >>> room.height, room.width
    (25, 25)
    >>> room.count_empty_cells()  # 23 * 23 interior
    529

    >>> small_room = create_empty_room(5, 5)
    >>> small_room.count_empty_cells()  # 3 * 3 interior
    9

    Notes
    -----
    The standard 25x25 room has 23x23 = 529 interior cells to visit.

    The minimum solution for the empty room is known to be 6 rules.
    A typical first solution might use 8-12 rules.

    Common strategies:
    - Boustrophedon (ox-turning): sweep back and forth like mowing a lawn
    - Spiral: start from outside and spiral inward (or vice versa)
    """
    return Room.empty_room(height, width)


# =============================================================================
# Standard Maze Definition
# =============================================================================

# The standard Picobot maze from the CS for All course
# Key properties:
#   - All walls are connected to the outer boundary
#   - All empty cells are adjacent to at least one wall
#   - Corridors are exactly one cell wide
#   - This ensures the right-hand rule will visit every cell
#
# NOTE: The original maze from the homework has a complex structure.
# This serpentine maze satisfies all the required properties and
# is equivalent for testing the right-hand rule algorithm.

STANDARD_MAZE_STRING = """
#########################
#.......................#
#######################.#
#.......................#
#.#######################
#.......................#
#######################.#
#.......................#
#.#######################
#.......................#
#######################.#
#.......................#
#.#######################
#.......................#
#######################.#
#.......................#
#.#######################
#.......................#
#######################.#
#.......................#
#.#######################
#.......................#
#######################.#
#.......................#
#########################
"""


def create_standard_maze() -> Room:
    """
    Create the standard Picobot maze from the CS for All course.

    This maze has the following properties:
    - 25x25 cells total
    - All walls are connected to the outer boundary
    - All empty cells are adjacent to at least one wall
    - Corridors are exactly one cell wide

    These properties ensure that the right-hand (or left-hand) wall-following
    algorithm will visit every empty cell.

    Returns
    -------
    Room
        A Room object representing the standard maze.

    Examples
    --------
    >>> maze = create_standard_maze()
    >>> maze.height, maze.width
    (25, 25)
    >>> print(maze.to_string())  # Will show the maze pattern

    Notes
    -----
    The minimum solution for the maze is believed to be around 8 rules
    using 4 states (one for each facing direction).

    The right-hand rule algorithm:
    1. Imagine you're walking through the maze with your right hand on the wall
    2. Always keep your right hand touching the wall
    3. This means: if you can turn right, do so; otherwise go straight;
       if you can't go straight, turn left; if you can't turn left, turn around.

    To implement this in Picobot, use 4 states representing the direction
    you're "facing" (N, E, S, W).
    """
    return Room.from_string(STANDARD_MAZE_STRING)


# =============================================================================
# Alternative Maze Definitions
# =============================================================================

# A smaller maze for testing (9x9) with proper properties
# All walls connected to boundary, all cells adjacent to walls
SMALL_MAZE_STRING = """
#########
#.......#
#######.#
#.......#
#.#######
#.......#
#######.#
#.......#
#########
"""


def create_small_maze() -> Room:
    """
    Create a small 9x9 maze for testing.

    This maze is useful for debugging because you can trace through
    the execution by hand and verify correctness.

    Returns
    -------
    Room
        A small 9x9 maze.

    Examples
    --------
    >>> maze = create_small_maze()
    >>> maze.height, maze.width
    (9, 9)
    """
    return Room.from_string(SMALL_MAZE_STRING)


# Diamond-shaped room (extra challenge from homework)
DIAMOND_ROOM_STRING = """
#############
######.######
#####...#####
####.....####
###.......###
##.........##
#...........#
##.........##
###.......###
####.....####
#####...#####
######.######
#############
"""


def create_diamond_room() -> Room:
    """
    Create the diamond-shaped room from the Picobot extra challenges.

    This is one of the bonus challenges mentioned in the homework.
    It tests whether your rules can handle non-rectangular open spaces.

    Returns
    -------
    Room
        A room with a diamond-shaped interior.

    Notes
    -----
    The diamond room is trickier than the empty room because the
    simple boustrophedon pattern doesn't work directly - Picobot will
    hit walls at different points in each row.
    """
    return Room.from_string(DIAMOND_ROOM_STRING)


# Stalactite room (extra challenge from homework)
STALACTITE_ROOM_STRING = """
#######
#.....#
###...#
#.....#
#...###
#.....#
#######
"""


def create_stalactite_room() -> Room:
    """
    Create the stalactite-shaped room from the Picobot extra challenges.

    This is another bonus challenge from the homework. The room has
    protrusions that can trap a simple coverage algorithm.

    Returns
    -------
    Room
        A room with stalactite-like protrusions.
    """
    return Room.from_string(STALACTITE_ROOM_STRING)


# =============================================================================
# Custom Maze Creation
# =============================================================================

def create_room_from_image_description(description: str) -> Room:
    """
    Create a room from a textual description.

    This is a convenience wrapper around Room.from_string that accepts
    a more flexible input format.

    Parameters
    ----------
    description : str
        A multi-line string where:
        - '#' or 'W' or 'â–ˆ' = Wall
        - '.' or ' ' or '_' = Empty space
        Lines can have leading/trailing whitespace.

    Returns
    -------
    Room
        A Room object matching the description.

    Examples
    --------
    >>> room_str = '''
    ...     #####
    ...     #...#
    ...     #.#.#
    ...     #...#
    ...     #####
    ... '''
    >>> room = create_room_from_image_description(room_str)
    """
    # Normalize the description:
    # - Replace various wall characters with '#'
    # - Replace various empty characters with '.'

    normalized = description
    normalized = normalized.replace('â–ˆ', '#')
    normalized = normalized.replace('W', '#')
    normalized = normalized.replace('_', '.')
    normalized = normalized.replace(' ', '.')

    return Room.from_string(normalized)


def validate_maze_properties(room: Room) -> dict:
    """
    Check if a room has the properties required for the right-hand rule to work.

    For the right-hand rule to guarantee full coverage, the maze must have:
    1. All walls connected to the outer boundary
    2. All empty cells adjacent to at least one wall

    Parameters
    ----------
    room : Room
        The room to validate.

    Returns
    -------
    dict
        A dictionary with:
        - 'valid': bool - True if maze properties are satisfied
        - 'all_walls_connected': bool - True if all walls touch boundary
        - 'all_cells_have_wall': bool - True if all empty cells are next to a wall
        - 'isolated_walls': list - Positions of walls not connected to boundary
        - 'isolated_cells': list - Positions of empty cells with no adjacent wall

    Examples
    --------
    >>> maze = create_standard_maze()
    >>> result = validate_maze_properties(maze)
    >>> result['valid']
    True
    """
    # Find all wall cells connected to the boundary using flood fill
    connected_walls = set()

    # Start by adding all boundary walls
    boundary_walls = []
    for row in range(room.height):
        for col in range(room.width):
            is_boundary = (
                row == 0 or row == room.height - 1 or
                col == 0 or col == room.width - 1
            )
            if is_boundary and room.is_wall(row, col):
                boundary_walls.append((row, col))
                connected_walls.add((row, col))

    # Flood fill to find all connected walls
    stack = boundary_walls.copy()
    while stack:
        row, col = stack.pop()
        # Check all 4 neighbors
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n_row, n_col = row + d_row, col + d_col
            if (0 <= n_row < room.height and 0 <= n_col < room.width):
                if room.is_wall(n_row, n_col):
                    if (n_row, n_col) not in connected_walls:
                        connected_walls.add((n_row, n_col))
                        stack.append((n_row, n_col))

    # Find isolated walls (walls not connected to boundary)
    isolated_walls = []
    for row in range(room.height):
        for col in range(room.width):
            if room.is_wall(row, col) and (row, col) not in connected_walls:
                isolated_walls.append((row, col))

    # Find empty cells that don't have any adjacent walls
    isolated_cells = []
    for row in range(room.height):
        for col in range(room.width):
            if room.is_empty(row, col):
                has_adjacent_wall = False
                for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    n_row, n_col = row + d_row, col + d_col
                    if room.is_wall(n_row, n_col):
                        has_adjacent_wall = True
                        break
                if not has_adjacent_wall:
                    isolated_cells.append((row, col))

    return {
        'valid': len(isolated_walls) == 0 and len(isolated_cells) == 0,
        'all_walls_connected': len(isolated_walls) == 0,
        'all_cells_have_wall': len(isolated_cells) == 0,
        'isolated_walls': isolated_walls,
        'isolated_cells': isolated_cells
    }


# =============================================================================
# Room Statistics
# =============================================================================

def room_statistics(room: Room) -> dict:
    """
    Calculate statistics about a room.

    Parameters
    ----------
    room : Room
        The room to analyze.

    Returns
    -------
    dict
        A dictionary containing:
        - 'height': int - Room height
        - 'width': int - Room width
        - 'total_cells': int - Total number of cells
        - 'empty_cells': int - Number of empty cells
        - 'wall_cells': int - Number of wall cells
        - 'empty_percent': float - Percentage of cells that are empty

    Examples
    --------
    >>> room = create_empty_room(25, 25)
    >>> stats = room_statistics(room)
    >>> stats['empty_cells']
    529
    """
    total = room.height * room.width
    empty = room.count_empty_cells()
    walls = total - empty

    return {
        'height': room.height,
        'width': room.width,
        'total_cells': total,
        'empty_cells': empty,
        'wall_cells': walls,
        'empty_percent': 100 * empty / total if total > 0 else 0
    }


# =============================================================================
# Display Utilities
# =============================================================================

def print_room_info(room: Room, name: str = "Room") -> None:
    """
    Print information about a room.

    Parameters
    ----------
    room : Room
        The room to display.
    name : str, optional
        A name for the room. Default is "Room".

    Examples
    --------
    >>> room = create_standard_maze()
    >>> print_room_info(room, "Standard Maze")
    """
    stats = room_statistics(room)

    print(f"\n{'=' * 60}")
    print(f"{name}")
    print(f"{'=' * 60}")
    print(f"Dimensions: {stats['height']} x {stats['width']}")
    print(f"Total cells: {stats['total_cells']}")
    print(f"Empty cells: {stats['empty_cells']} ({stats['empty_percent']:.1f}%)")
    print(f"Wall cells: {stats['wall_cells']}")
    print()
    print(room.to_string())
    print()


# =============================================================================
# Main - Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Picobot Room and Maze Builder Demo")
    print("=" * 60)

    # Show empty room
    empty = create_empty_room(11, 11)
    print_room_info(empty, "Empty Room (11x11)")

    # Show standard maze
    maze = create_standard_maze()
    print_room_info(maze, "Standard Maze")

    # Validate maze properties
    validation = validate_maze_properties(maze)
    print("Maze validation:")
    print(f"  Valid for right-hand rule: {validation['valid']}")
    print(f"  All walls connected: {validation['all_walls_connected']}")
    print(f"  All cells have adjacent wall: {validation['all_cells_have_wall']}")

    # Show small maze
    small = create_small_maze()
    print_room_info(small, "Small Test Maze")

    # Show diamond room
    diamond = create_diamond_room()
    print_room_info(diamond, "Diamond Room (Extra Challenge)")

    # Show stalactite room
    stalactite = create_stalactite_room()
    print_room_info(stalactite, "Stalactite Room (Extra Challenge)")
