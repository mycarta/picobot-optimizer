"""
Matteo Niccoli's Initial Picobot Solutions
==========================================

Transcribed from the Initial_solutions.pdf file dated 1/19/2015.

These are the INITIAL solutions, not the final optimized versions.
The goal is to verify they work, then compare against the final
optimized solutions Matteo developed.

Solution Summary
----------------
- Empty Room: 7 rules, 3 states (0, 1, 2)
- Maze: 16 rules, 4 states (0, 1, 2, 3)

Targets for Optimization (noted in margins)
-------------------------------------------
- Empty Room: Can potentially be done in 6 rules
- Maze: Can potentially be done in 8 rules
"""

# =============================================================================
# EMPTY ROOM SOLUTION - 7 Rules
# =============================================================================
#
# Strategy: Boustrophedon (ox-turning) pattern
#
# State meanings:
#   State 0: Moving North (until hitting north wall)
#   State 1: Moving East (to reach east wall, then switch to west sweep)
#   State 2: Moving West (sweeping west, then drop south)
#
# The pattern:
#   1. Go North until hitting the north wall
#   2. If there's room to the East, go East (transition to state 1)
#   3. In state 1, keep going East until hitting east wall
#   4. When hitting east wall, switch to going West (state 2)
#   5. In state 2, go West until hitting west wall
#   6. When hitting west wall, drop down one row (go South) and continue East
#
# Note from original: There's an OR branch to handle starting near the East wall

EMPTY_ROOM_INITIAL = """
# ============================================
# EMPTY ROOM SOLUTION - Initial Version
# 7 rules, 3 states
# ============================================

# State 0: Going North
# --------------------
# (initial) state 0 with nothing to the N: go N
0 x*** -> N 0

# state 0 with a wall N but none E: go E (start eastward sweep)
0 Nx** -> E 1

# state 0 with a wall N and wall E: go W (start westward sweep)
# This handles the case where we're in the NE area
0 NE** -> W 2

# State 1: Going East
# -------------------
# state 1 with nothing E: keep going E
1 *x** -> E 1

# state 1 with a wall E: go W (finished eastward, now go west)
1 *E** -> W 2

# State 2: Going West
# -------------------
# state 2 with nothing W: keep going W
2 **x* -> W 2

# state 2 with a wall W: go S (drop down a row), switch to state 1 to go East
2 **W* -> S 1
"""


# =============================================================================
# MAZE SOLUTION - 16 Rules
# =============================================================================
#
# Strategy: Right-hand rule (wall follower)
#
# State meanings - each state represents the direction Picobot is "facing":
#   State 0: Facing North (right hand on East wall)
#   State 1: Facing East (right hand on South wall)
#   State 2: Facing West (right hand on North wall)
#   State 3: Facing South (right hand on West wall)
#
# Right-hand rule logic:
#   1. CORRIDOR: If wall on right and space ahead â†’ go forward, stay in state
#   2. INTERSECTION: If no wall on right â†’ turn right (go that direction, change state)
#   3. DEAD END: If wall ahead â†’ turn left (change state)
#   4. FULL DEAD END: If walls on 3 sides â†’ turn around (go back, change state)
#
# Each state has 4 rules to handle these cases.

MAZE_INITIAL = """
# ============================================
# MAZE SOLUTION - Initial Version  
# 16 rules, 4 states
# Right-hand wall follower algorithm
# ============================================

# ------------------------------------------
# STATE 0: FACING NORTH (right hand on East)
# ------------------------------------------

# CORRIDOR: wall to East, nothing to North â†’ keep going North
0 xE** -> N 0

# INTERSECTION: nothing to East â†’ turn right (go East, face East)
0 *x** -> E 1

# DEAD END: walls North and East, nothing West â†’ turn left (go West, face West)
0 NEx* -> W 2

# FULL DEAD END: walls N, E, W â†’ turn around (go South, face South)
0 NEWx -> S 3

# ------------------------------------------
# STATE 1: FACING EAST (right hand on South)
# ------------------------------------------

# CORRIDOR: wall to South, nothing to East â†’ keep going East
1 *x*S -> E 1

# INTERSECTION: nothing to South â†’ turn right (go South, face South)
1 ***x -> S 3

# DEAD END: walls East and South, nothing North â†’ turn left (go North, face North)
1 xE*S -> N 0

# FULL DEAD END: walls E, S, N â†’ turn around (go West, face West)
1 NExS -> W 2

# ------------------------------------------
# STATE 2: FACING WEST (right hand on North)
# ------------------------------------------

# CORRIDOR: wall to North, nothing to West â†’ keep going West
2 N*x* -> W 2

# INTERSECTION: nothing to North â†’ turn right (go North, face North)
2 x*** -> N 0

# DEAD END: walls West and North, nothing South â†’ turn left (go South, face South)
2 N*Wx -> S 3

# FULL DEAD END: walls W, N, S â†’ turn around (go East, face East)
2 NxWS -> E 1

# ------------------------------------------
# STATE 3: FACING SOUTH (right hand on West)
# ------------------------------------------

# CORRIDOR: wall to West, nothing to South â†’ keep going South
3 **Wx -> S 3

# INTERSECTION: nothing to West â†’ turn right (go West, face West)
3 **x* -> W 2

# DEAD END: walls South and West, nothing East â†’ turn left (go East, face East)
3 *xWS -> E 1

# FULL DEAD END: walls S, W, E â†’ turn around (go North, face North)
3 xEWS -> N 0
"""


# =============================================================================
# FIRST EXPERIMENT - Go to Origin
# =============================================================================
#
# This appears to be an early experiment from the document,
# possibly testing basic movement. Goes to bottom-left corner.

FIRST_EXPERIMENT = """
# ============================================
# FIRST EXPERIMENT - Go to Origin (Bottom Left)
# From early notes, probably just testing syntax
# ============================================

0 **** -> X 3
3 ***x -> S 3
3 ***S -> W 2
2 **x* -> W 2
2 **W* -> X 0
"""


# =============================================================================
# Rule strings for easy access
# =============================================================================

def get_empty_room_rules() -> str:
    """
    Get the initial empty room solution rules.

    Returns
    -------
    str
        The 7-rule solution for the empty room.
    """
    return EMPTY_ROOM_INITIAL


def get_maze_rules() -> str:
    """
    Get the initial maze solution rules.

    Returns
    -------
    str
        The 16-rule solution for the maze.
    """
    return MAZE_INITIAL


# =============================================================================
# Main - Display the solutions
# =============================================================================

if __name__ == "__main__":
    from picobot_simulator import parse_rules, count_rules, count_states

    print("=" * 60)
    print("Matteo's Initial Picobot Solutions")
    print("=" * 60)

    # Empty room
    print("\n" + "-" * 60)
    print("EMPTY ROOM SOLUTION")
    print("-" * 60)
    print(EMPTY_ROOM_INITIAL)

    rules = parse_rules(EMPTY_ROOM_INITIAL)
    print(f"\nParsed: {count_rules(rules)} rules, {count_states(rules)} states")

    # Maze
    print("\n" + "-" * 60)
    print("MAZE SOLUTION")
    print("-" * 60)
    print(MAZE_INITIAL)

    rules = parse_rules(MAZE_INITIAL)
    print(f"\nParsed: {count_rules(rules)} rules, {count_states(rules)} states")
