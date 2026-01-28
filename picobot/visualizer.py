"""
Picobot Visualization Module
============================

Creates animated GIFs showing Picobot solving rooms and mazes.

This module provides tools to visualize Picobot's movement patterns,
making it easy to understand how different rule sets achieve coverage.
The visualizations use a color scheme optimized for accessibility
(dichromatic-friendly).

Features
--------
- Animated GIF generation from any Picobot solution
- Random or fixed starting positions
- Configurable animation speed and frame capture rate
- Non-looping option for post-production editing
- Accessibility-friendly color scheme (purple robot, green visited)

Example Usage
-------------
    >>> from picobot_visualizer import create_animation, EMPTY_ROOM_6_RULES
    >>> from picobot_rooms import create_empty_room
    >>> room = create_empty_room(15, 15)
    >>> create_animation(
    ...     rules=EMPTY_ROOM_6_RULES,
    ...     room=room,
    ...     seed=42,
    ...     filename="my_animation.gif"
    ... )

Author: Matteo Niccoli (original solutions, 2015)
Documentation & Visualization: Claude AI (2026)
"""

import io
import random
from typing import Optional

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for GIF generation
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Import Picobot simulator components
from picobot.simulator import Picobot, Room
from picobot.rooms import create_empty_room, create_standard_maze, create_small_maze


# =============================================================================
# COLOR SCHEME (Dichromatic-friendly)
# =============================================================================

COLORS = {
    'wall': '#1a365d',       # Dark blue - room boundaries
    'unvisited': '#e2e8f0',  # Light gray - cells not yet covered
    'visited': '#9ae6b4',    # Light green - cells Picobot has covered
    'robot_fill': '#9333ea', # Purple - Picobot (visible to colorblind users)
    'robot_edge': '#581c87', # Dark purple - Picobot outline
    'grid_line': '#718096',  # Medium gray - cell boundaries
}


# =============================================================================
# OPTIMIZED SOLUTIONS
# =============================================================================

EMPTY_ROOM_6_RULES = """
# 6-Rule Empty Room Solution (Boustrophedon Pattern)
# ==================================================
# State 0: Going North until hitting wall
# State 1: Check East / Go East (or switch to West)
# State 2: Going West until hitting wall, then drop South

0 x*** -> N 0
0 N*** -> X 1
1 *x** -> E 1
1 *E** -> W 2
2 **x* -> W 2
2 **W* -> S 1
"""

MAZE_12_RULES = """
# 12-Rule Maze Solution (Right-Hand Wall Following)
# =================================================
# State 0: Going North (wall expected on East)
# State 1: Going East (wall expected on South)
# State 2: Going West (wall expected on North)
# State 3: Going South (wall expected on West)

0 *x** -> E 1
0 xE** -> N 0
0 NE** -> X 2

1 ***x -> S 3
1 *x*S -> E 1
1 *E*S -> X 0

2 x*** -> N 0
2 N*x* -> W 2
2 N*W* -> X 3

3 **x* -> W 2
3 **Wx -> S 3
3 **WS -> X 1
"""


# =============================================================================
# FRAME CREATION
# =============================================================================

def create_frame(
    room: Room,
    visited: set,
    position: tuple,
    state: int,
    step: int,
    coverage_pct: float,
    title: Optional[str] = None,
    figsize: tuple = (5, 5.5)
) -> Image.Image:
    """
    Create a single frame of the Picobot visualization.

    Parameters
    ----------
    room : Room
        The room object containing wall/empty cell information.
    visited : set
        Set of (row, col) tuples representing visited cells.
    position : tuple
        Current Picobot position as (row, col).
    state : int
        Current Picobot state number.
    step : int
        Current simulation step number.
    coverage_pct : float
        Percentage of room covered (0-100).
    title : str, optional
        Title to display above the visualization.
    figsize : tuple, optional
        Figure size in inches (width, height). Default (5, 5.5).

    Returns
    -------
    Image.Image
        PIL Image object containing the rendered frame.

    Notes
    -----
    The coordinate system is flipped vertically so that row 0 appears
    at the top (matching typical grid representations).
    """
    rows = room.height
    cols = room.width

    fig, ax = plt.subplots(figsize=figsize)

    # Draw each cell
    for r in range(rows):
        for c in range(cols):
            # Determine cell color based on state
            if room.is_wall(r, c):
                color = COLORS['wall']
            elif (r, c) in visited:
                color = COLORS['visited']
            else:
                color = COLORS['unvisited']

            # Create rectangle (flip y-axis so row 0 is at top)
            rect = patches.Rectangle(
                (c, rows - 1 - r),  # Position (x, y)
                1, 1,               # Width, height
                linewidth=0.5,
                edgecolor=COLORS['grid_line'],
                facecolor=color
            )
            ax.add_patch(rect)

    # Draw Picobot as a purple circle
    pr, pc = position
    circle = patches.Circle(
        (pc + 0.5, rows - 1 - pr + 0.5),  # Center of cell
        0.4,                               # Radius
        facecolor=COLORS['robot_fill'],
        edgecolor=COLORS['robot_edge'],
        linewidth=2
    )
    ax.add_patch(circle)

    # Configure axes
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')

    # Add title if provided
    if title:
        ax.set_title(title, fontsize=11, fontweight='bold', pad=10)

    # Add status bar at bottom
    info_text = f"Step: {step}  |  State: {state}  |  Coverage: {coverage_pct:.1f}%"
    fig.text(0.5, 0.02, info_text, ha='center', fontsize=9,
             fontfamily='monospace')

    plt.tight_layout()

    # Convert matplotlib figure to PIL Image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buf.seek(0)
    img = Image.open(buf).convert('RGB')  # Force RGB (no transparency issues)
    img = img.copy()  # Copy to allow buffer closure
    plt.close(fig)
    buf.close()

    return img


# =============================================================================
# ANIMATION CREATION
# =============================================================================

def create_animation(
    rules: str,
    room: Room,
    seed: Optional[int] = None,
    start_pos: Optional[tuple] = None,
    start_state: int = 0,
    filename: str = "picobot.gif",
    duration: int = 80,
    loop: bool = False,
    max_steps: int = 5000
) -> str:
    """
    Create an animated GIF of Picobot solving a room.

    This is the main entry point for creating visualizations. It handles
    random start position selection, simulation execution, and GIF export.

    Parameters
    ----------
    rules : str
        Picobot rules as a string (one rule per line).
    room : Room
        The room for Picobot to navigate.
    seed : int, optional
        Random seed for reproducible start positions. If None and start_pos
        is None, a random position is chosen without fixed seed.
    start_pos : tuple, optional
        Explicit starting position as (row, col). Overrides seed if provided.
    start_state : int, optional
        Initial state for Picobot. Default 0.
        - State 0: Goes North first
        - State 1: Goes East first
        - State 2: Goes West first
    filename : str, optional
        Output filename for the GIF. Default "picobot.gif".
    duration : int, optional
        Milliseconds per frame. Default 80 (~12.5 fps).
    loop : bool, optional
        If True, GIF loops forever. If False, plays once. Default False.
    max_steps : int, optional
        Maximum simulation steps before stopping. Default 5000.

    Returns
    -------
    str
        Path to the saved GIF file.

    Examples
    --------
    Create animation starting East (State 1):

        >>> create_animation(EMPTY_ROOM_6_RULES, room, seed=42,
        ...                  start_state=1, filename="east_start.gif")
    """
    # Determine starting position
    if start_pos is None:
        if seed is not None:
            random.seed(seed)
        # Pick random position inside room (not on walls)
        start_row = random.randint(1, room.height - 2)
        start_col = random.randint(1, room.width - 2)
        start_pos = (start_row, start_col)

    # Direction names for title
    state_directions = {0: "North", 1: "East", 2: "West"}
    direction = state_directions.get(start_state, f"State {start_state}")
    
    # Create title showing start position and direction
    title = f"6-Rule Boustrophedon (start: row {start_pos[0]}, col {start_pos[1]}, going {direction})"

    # Initialize Picobot
    bot = Picobot(room, rules, start_pos)
    bot.state = start_state  # Set initial state
    total_open = room.count_empty_cells()

    # Collect frames
    frames = []
    step = 0

    # Capture initial state
    coverage_pct = len(bot.visited) / total_open * 100
    frames.append(create_frame(
        room, bot.visited, bot.position, bot.state,
        step, coverage_pct, title
    ))

    # Run simulation
    while not bot.is_complete() and step < max_steps:
        bot.step()
        step += 1
        coverage_pct = len(bot.visited) / total_open * 100
        frames.append(create_frame(
            room, bot.visited, bot.position, bot.state,
            step, coverage_pct, title
        ))

    print(f"Simulation complete: {step} steps, {len(frames)} frames")

    # Save GIF
    loop_count = 0 if loop else 1  # 0 = infinite loop, 1 = play once
    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop_count
    )
    print(f"Saved: {filename}")

    return filename


def create_north_start_animation(
    rules: str,
    room: Room,
    seed: Optional[int] = None,
    filename: str = "picobot_north.gif",
    duration: int = 80,
    loop: bool = False,
    max_steps: int = 5000
) -> str:
    """
    Create animation starting from a position that shows the North run.

    This places Picobot in the middle-bottom area of the room so the
    initial "go North until wall" behavior is clearly visible before
    the boustrophedon pattern begins.

    Parameters
    ----------
    rules : str
        Picobot rules as a string.
    room : Room
        The room for Picobot to navigate.
    seed : int, optional
        Random seed for horizontal position variation.
    filename : str, optional
        Output filename. Default "picobot_north.gif".
    duration : int, optional
        Milliseconds per frame. Default 80.
    loop : bool, optional
        If True, GIF loops forever. Default False.
    max_steps : int, optional
        Maximum simulation steps. Default 5000.

    Returns
    -------
    str
        Path to the saved GIF file.

    Notes
    -----
    The starting row is set to approximately 2/3 down the room to
    ensure a visible "going North" phase before the East-West sweeping
    begins.
    """
    if seed is not None:
        random.seed(seed)

    # Start in lower portion of room (2/3 down) for visible North run
    start_row = int(room.height * 2 / 3)
    start_col = random.randint(1, room.width - 2)

    # Ensure we're not on a wall
    start_row = max(1, min(start_row, room.height - 2))

    return create_animation(
        rules=rules,
        room=room,
        start_pos=(start_row, start_col),
        filename=filename,
        duration=duration,
        loop=loop,
        max_steps=max_steps
    )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_empty_room_demo(
    room_size: int = 15,
    seed: int = 7,
    filename: str = "empty_room_demo.gif",
    duration: int = 80
) -> str:
    """
    Create a demo animation of the 6-rule empty room solution.

    Parameters
    ----------
    room_size : int, optional
        Size of square room. Default 15.
    seed : int, optional
        Random seed for starting position. Default 7.
    filename : str, optional
        Output filename. Default "empty_room_demo.gif".
    duration : int, optional
        Milliseconds per frame. Default 80.

    Returns
    -------
    str
        Path to saved GIF.
    """
    room = create_empty_room(room_size, room_size)
    return create_animation(
        EMPTY_ROOM_6_RULES, room, seed=seed,
        filename=filename, duration=duration
    )


def create_maze_demo(
    filename: str = "maze_demo.gif",
    duration: int = 80
) -> str:
    """
    Create a demo animation of the 12-rule maze solution.

    Parameters
    ----------
    filename : str, optional
        Output filename. Default "maze_demo.gif".
    duration : int, optional
        Milliseconds per frame. Default 80.

    Returns
    -------
    str
        Path to saved GIF.
    """
    maze = create_small_maze()
    return create_animation(
        MAZE_12_RULES, maze, seed=1,
        filename=filename, duration=duration
    )


# =============================================================================
# MAIN - Demo execution
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Picobot Visualization Demo")
    print("=" * 60)

    # Create output directory reference
    output_dir = "/home/claude/picobot"

    # Demo 1: Random start position
    print("\n1. Creating random-start animation (seed 7)...")
    create_empty_room_demo(
        seed=7,
        filename=f"{output_dir}/demo_random.gif"
    )

    # Demo 2: North-start animation (shows initial North run)
    print("\n2. Creating North-start animation...")
    room = create_empty_room(15, 15)
    create_north_start_animation(
        EMPTY_ROOM_6_RULES, room, seed=42,
        filename=f"{output_dir}/demo_north_start.gif"
    )

    # Demo 3: Maze solution
    print("\n3. Creating maze animation...")
    create_maze_demo(filename=f"{output_dir}/demo_maze.gif")

    print("\n" + "=" * 60)
    print("Done! Check output files in:", output_dir)
    print("=" * 60)
