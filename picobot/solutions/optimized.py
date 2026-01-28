"""
Matteo Niccoli's Optimized Picobot Solutions
============================================

These are the OPTIMIZED solutions, developed after the initial working
versions through careful analysis of rule redundancy and state reuse.

Transcribed from handwritten notes and typed solutions dated 1/27/2015.

Solution Summary
----------------
- Empty Room: 6 rules, 3 states (down from 7 rules) - 14% reduction
- Maze: 12 rules, 4 states (down from 16 rules) - 25% reduction

The Journey
-----------
Initial solutions (1/19/2015): 7 rules (empty), 16 rules (maze)
Optimized solutions (1/27/2015): 6 rules (empty), 12 rules (maze)

Key Optimization Insights
-------------------------
Both optimizations share the same core insight: X (stay put) is not a 
wasted move â€” it's a STATE TRANSITION WITHOUT MOVEMENT that enables
reusing logic from the destination state instead of duplicating it.

Empty Room Insight (7 â†’ 6):
    "C and F are the same 'nothing to the east' if we ignore everything else"
    Collapsed two north-wall rules into one by using X to transition to
    state 1, which already knows how to handle "check east and decide."

Maze Insight (16 â†’ 12):
    Collapse 4 rules per state to 3 rules by combining dead ends and left
    turns into a single rule. Key realization: rule ordering matters because
    rules are evaluated top-to-bottom. Position "G" in the maze diagram was
    the critical test case that validated the rule ordering.
"""

# =============================================================================
# EMPTY ROOM SOLUTION - OPTIMIZED - 6 Rules
# =============================================================================
#
# Strategy: Boustrophedon (ox-turning / bustrofedica) pattern
#
# State meanings:
#   State 0: Moving North (until hitting north wall)
#   State 1: Checking East / Moving East
#   State 2: Moving West
#
# The key optimization:
#   When hitting the north wall, DON'T immediately decide east vs west.
#   Instead, STAY PUT (X) and switch to state 1, which already has the
#   logic to check east and decide which way to go.

EMPTY_ROOM_OPTIMIZED = """
# ============================================
# EMPTY ROOM SOLUTION - Optimized Version
# 6 rules, 3 states (the known minimum)
# Dated: 1/27/2015, 11:08 AM
# ============================================

# State 0: Going North
# --------------------
# Keep going north until we hit the north wall
0 x*** -> N 0

# When we hit the north wall, STAY PUT and switch to state 1
# State 1 will figure out whether to go east or west
# THIS IS THE KEY OPTIMIZATION - reuse state 1's logic
0 N*** -> X 1

# State 1: Check East / Go East  
# ------------------------------
# If nothing to the east, go east (handles both "along north wall"
# and "just dropped down from west wall" cases)
1 *x** -> E 1

# If wall to the east, switch to going west
1 *E** -> W 2

# State 2: Going West
# -------------------
# Keep going west until we hit the west wall
2 **x* -> W 2

# When we hit the west wall, drop down one row (go south)
# and switch to state 1 to go east
2 **W* -> S 1
"""


# =============================================================================
# MAZE SOLUTION - OPTIMIZED - 12 Rules
# =============================================================================
#
# Strategy: Right-hand rule (wall follower) with collapsed rules
#
# State meanings - each state represents the direction Picobot is "facing":
#   State 0: Facing North (right hand on East wall)
#   State 1: Facing East (right hand on South wall)
#   State 2: Facing West (right hand on North wall)
#   State 3: Facing South (right hand on West wall)
#
# The optimization: Collapse from 4 rules per state to 3 rules by:
#   1. Rule for wall on the right (keep going forward)
#   2. Rule for losing wall (turn right)
#   3. Rule for dead ends AND left turns combined (use X to transition)
#
# CRITICAL: Rule ordering matters! Rules are evaluated top-to-bottom.
# The working solution required swapping the order of rules (1) and (2)
# in state 0. "Key is G" refers to a maze position that validated this.

MAZE_OPTIMIZED = """
# ============================================
# MAZE SOLUTION - Optimized Version
# 12 rules, 4 states (down from 16 rules)
# Dated: 1/27/2015
# Note: "This works!!"
# ============================================

# ------------------------------------------
# STATE 0: FACING NORTH (right hand on East)
# ------------------------------------------
# Rule ordering is critical here - these were swapped from original attempt

# INTERSECTION: nothing to East â†’ turn right (go East, face East)
# NOTE: This rule comes FIRST (was rule 2, now rule 1)
0 *x** -> E 1

# CORRIDOR: wall to East, nothing to North â†’ keep going North
# NOTE: This rule comes SECOND (was rule 1, now rule 2)
0 xE** -> N 0

# DEAD END / LEFT TURN: wall North and East â†’ stay put, switch to West state
0 NE** -> X 2

# ------------------------------------------
# STATE 1: FACING EAST (right hand on South)
# ------------------------------------------

# INTERSECTION: nothing to South â†’ turn right (go South, face South)
1 ***x -> S 3

# CORRIDOR: wall to South, nothing to East â†’ keep going East
1 *x*S -> E 1

# DEAD END / LEFT TURN: wall East and South â†’ stay put, switch to North state
1 *E*S -> X 0

# ------------------------------------------
# STATE 2: FACING WEST (right hand on North)
# ------------------------------------------

# INTERSECTION: nothing to North â†’ turn right (go North, face North)
2 x*** -> N 0

# CORRIDOR: wall to North, nothing to West â†’ keep going West
2 N*x* -> W 2

# DEAD END / LEFT TURN: wall North and West â†’ stay put, switch to South state
2 N*W* -> X 3

# ------------------------------------------
# STATE 3: FACING SOUTH (right hand on West)
# ------------------------------------------

# INTERSECTION: nothing to West â†’ turn right (go West, face West)
3 **x* -> W 2

# CORRIDOR: wall to West, nothing to South â†’ keep going South
3 **Wx -> S 3

# DEAD END / LEFT TURN: wall West and South â†’ stay put, switch to East state
3 **WS -> X 1
"""


# =============================================================================
# Comparison: Initial vs Optimized (Empty Room)
# =============================================================================

EMPTY_ROOM_COMPARISON = """
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘          INITIAL (7 rules)    â†’    OPTIMIZED (6 rules)           â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                  â•‘
â•‘  STATE 0: Going North                                            â•‘
â•‘  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                           â•‘
â•‘  0 x*** -> N 0              â”‚  0 x*** -> N 0      (same)         â•‘
â•‘  0 Nx** -> E 1              â”‚                                    â•‘
â•‘  0 NE** -> W 2              â”‚  0 N*** -> X 1      (COLLAPSED)    â•‘
â•‘                                                                  â•‘
â•‘  STATE 1: Going East                                             â•‘
â•‘  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                             â•‘
â•‘  1 *x** -> E 1              â”‚  1 *x** -> E 1      (same)         â•‘
â•‘  1 *E** -> W 2              â”‚  1 *E** -> W 2      (same)         â•‘
â•‘                                                                  â•‘
â•‘  STATE 2: Going West                                             â•‘
â•‘  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                                             â•‘
â•‘  2 **x* -> W 2              â”‚  2 **x* -> W 2      (same)         â•‘
â•‘  2 **W* -> S 1              â”‚  2 **W* -> S 1      (same)         â•‘
â•‘                                                                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

The insight: X (stay put) is not a wasted move â€” it's a state transition
that lets you REUSE existing logic instead of duplicating it.
"""


# =============================================================================
# Comparison: Initial vs Optimized (Maze)
# =============================================================================

MAZE_COMPARISON = """
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘          INITIAL (16 rules)   â†’    OPTIMIZED (12 rules)          â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                  â•‘
â•‘  Each state: 4 rules â†’ 3 rules                                   â•‘
â•‘                                                                  â•‘
â•‘  INITIAL per state:                OPTIMIZED per state:          â•‘
â•‘  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€             â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€        â•‘
â•‘  1. Corridor (wall right)     â†’    1. Wall on right (corridor)   â•‘
â•‘  2. Intersection (no wall)    â†’    2. Losing wall (turn right)   â•‘
â•‘  3. Dead end (wall ahead)     â†’    3. Dead end + left turn       â•‘
â•‘  4. Full dead end (3 walls)        (COMBINED using X)            â•‘
â•‘                                                                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

The insight: Dead ends and left turns can share a rule because both
are handled by staying put (X) and switching to the perpendicular state.
Rule ordering is critical â€” "Key is G" validated the correct order.
"""


# =============================================================================
# Accessor functions
# =============================================================================

def get_empty_room_optimized() -> str:
    """
    Get the optimized empty room solution rules.

    Returns
    -------
    str
        The 6-rule solution for the empty room.
    
    Notes
    -----
    This is the known minimum for the empty room problem.
    Achieved through the insight that X (stay put) enables
    state reuse rather than rule duplication.
    """
    return EMPTY_ROOM_OPTIMIZED


def get_maze_optimized() -> str:
    """
    Get the optimized maze solution rules.

    Returns
    -------
    str
        The 12-rule solution for the maze.
    
    Notes
    -----
    Achieved 25% reduction (16 â†’ 12 rules) by:
    - Combining dead ends and left turns into one rule per state
    - Using X (stay put) for state transitions
    - Careful attention to rule ordering (top-to-bottom evaluation)
    
    The target of 8 rules was explored but not achieved.
    """
    return MAZE_OPTIMIZED


def print_empty_room_comparison() -> None:
    """Print the before/after comparison of empty room solutions."""
    print(EMPTY_ROOM_COMPARISON)


def print_maze_comparison() -> None:
    """Print the before/after comparison of maze solutions."""
    print(MAZE_COMPARISON)


# =============================================================================
# Main - Verify both optimized solutions
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/mnt/project')
    
    from picobot_simulator import (
        parse_rules, count_rules, count_states, test_rules_all_positions
    )
    from picobot_rooms import create_empty_room, create_standard_maze, create_small_maze
    
    print("=" * 60)
    print("Matteo's Optimized Picobot Solutions")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # EMPTY ROOM
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("OPTIMIZED EMPTY ROOM SOLUTION")
    print("-" * 60)
    print(EMPTY_ROOM_OPTIMIZED)
    
    rules = parse_rules(EMPTY_ROOM_OPTIMIZED)
    print(f"Parsed: {count_rules(rules)} rules, {count_states(rules)} states")
    
    print("\nVerifying against all starting positions (25x25 room)...")
    room = create_empty_room(25, 25)
    result = test_rules_all_positions(room, rules, max_steps=50000)
    
    if result['success']:
        print(f"âœ“ VERIFIED: Full coverage from all {result['positions_tested']} positions")
        print(f"  Max steps: {result['max_steps_used']}, Avg: {result['avg_steps']:.1f}")
    else:
        print(f"âœ— FAILED: {len(result['failures'])} positions did not achieve coverage")
    
    # -------------------------------------------------------------------------
    # MAZE
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("OPTIMIZED MAZE SOLUTION")
    print("-" * 60)
    print(MAZE_OPTIMIZED)
    
    rules = parse_rules(MAZE_OPTIMIZED)
    print(f"Parsed: {count_rules(rules)} rules, {count_states(rules)} states")
    
    # Test on small maze first
    print("\nVerifying against small maze (9x9)...")
    maze_small = create_small_maze()
    result = test_rules_all_positions(maze_small, rules, max_steps=50000)
    
    if result['success']:
        print(f"âœ“ VERIFIED: Full coverage from all {result['positions_tested']} positions")
        print(f"  Max steps: {result['max_steps_used']}, Avg: {result['avg_steps']:.1f}")
    else:
        print(f"âœ— FAILED: {len(result['failures'])} positions did not achieve coverage")
        for pos, fail_result in result['failures'][:3]:
            print(f"  Position {pos}: {fail_result['coverage']:.1f}% coverage")
    
    # Test on standard maze
    print("\nVerifying against standard maze (25x25)...")
    maze_standard = create_standard_maze()
    result = test_rules_all_positions(maze_standard, rules, max_steps=50000)
    
    if result['success']:
        print(f"âœ“ VERIFIED: Full coverage from all {result['positions_tested']} positions")
        print(f"  Max steps: {result['max_steps_used']}, Avg: {result['avg_steps']:.1f}")
    else:
        print(f"âœ— FAILED: {len(result['failures'])} positions did not achieve coverage")
        for pos, fail_result in result['failures'][:3]:
            print(f"  Position {pos}: {fail_result['coverage']:.1f}% coverage")
    
    # -------------------------------------------------------------------------
    # COMPARISONS
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("OPTIMIZATION COMPARISONS")
    print("-" * 60)
    print_empty_room_comparison()
    print_maze_comparison()
