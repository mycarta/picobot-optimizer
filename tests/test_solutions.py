"""
Picobot Solution Tester
=======================

This script tests Picobot solutions to verify they achieve full coverage
from any starting position.

Usage
-----
    python test_solutions.py

This will test:
1. The empty room solution (7 rules)
2. The maze solution (16 rules)

Both are tested from multiple starting positions to ensure robustness.
"""

from picobot.simulator import (
    Picobot,
    Room,
    parse_rules,
    count_rules,
    count_states,
    test_rules_all_positions
)
from picobot.rooms import create_empty_room, create_standard_maze, create_small_maze
from picobot.solutions.initial import EMPTY_ROOM_INITIAL, MAZE_INITIAL


def test_solution(
    name: str,
    room: Room,
    rules_text: str,
    test_all_positions: bool = False,
    sample_positions: int = 5
) -> bool:
    """
    Test a Picobot solution and report results.

    Parameters
    ----------
    name : str
        Name of the test (for display).
    room : Room
        The room to test in.
    rules_text : str
        The rules to test.
    test_all_positions : bool
        If True, test from every possible starting position.
        If False, test from a sample of positions.
    sample_positions : int
        Number of random positions to sample (if not testing all).

    Returns
    -------
    bool
        True if all tests passed.
    """
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"{'=' * 60}")

    # Parse and display rule info
    rules = parse_rules(rules_text)
    n_rules = count_rules(rules)
    n_states = count_states(rules)

    print(f"Rules: {n_rules}")
    print(f"States: {n_states}")
    print(f"Room: {room.height}x{room.width}")
    print(f"Empty cells to visit: {room.count_empty_cells()}")

    # Get all empty cells
    empty_cells = room.get_empty_cells()

    if test_all_positions:
        # Test every position
        print(f"\nTesting from ALL {len(empty_cells)} starting positions...")
        result = test_rules_all_positions(room, rules, max_steps=50000)

        if result['success']:
            print(f"âœ“ PASSED - Full coverage from all positions!")
            print(f"  Max steps needed: {result['max_steps_used']}")
            print(f"  Avg steps: {result['avg_steps']:.1f}")
        else:
            print(f"âœ— FAILED - {len(result['failures'])} positions failed")
            for pos, fail_result in result['failures'][:5]:
                print(f"  Position {pos}: {fail_result['coverage']:.1f}% coverage")
                if fail_result['halted']:
                    print(f"    Halt reason: {fail_result['halt_reason']}")

        return result['success']

    else:
        # Test sample positions
        import random
        random.seed(42)  # Reproducible

        # Always include corners and center
        positions_to_test = []

        # Add corners (interior corners)
        corners = [
            (1, 1),                          # Top-left interior
            (1, room.width - 2),             # Top-right interior
            (room.height - 2, 1),            # Bottom-left interior
            (room.height - 2, room.width - 2)  # Bottom-right interior
        ]
        for pos in corners:
            if pos in empty_cells:
                positions_to_test.append(pos)

        # Add center
        center = (room.height // 2, room.width // 2)
        if center in empty_cells:
            positions_to_test.append(center)

        # Add random positions
        remaining = [p for p in empty_cells if p not in positions_to_test]
        if remaining and sample_positions > len(positions_to_test):
            n_random = min(sample_positions - len(positions_to_test), len(remaining))
            positions_to_test.extend(random.sample(remaining, n_random))

        print(f"\nTesting from {len(positions_to_test)} sample positions...")

        all_passed = True
        for pos in positions_to_test:
            bot = Picobot(room, rules, start_position=pos)
            result = bot.run(max_steps=50000)

            status = "âœ“" if result['success'] else "âœ—"
            print(f"  {status} Position {pos}: {result['coverage']:.1f}% in {result['steps']} steps")

            if not result['success']:
                all_passed = False
                if result['halted']:
                    print(f"      Halt: {result['halt_reason']}")

        if all_passed:
            print(f"\nâœ“ PASSED all sample tests!")
        else:
            print(f"\nâœ— FAILED some tests")

        return all_passed


def run_single_demo(room: Room, rules_text: str, start_pos: tuple = None):
    """
    Run a single simulation and show the trace.
    
    Useful for debugging.
    """
    if start_pos is None:
        start_pos = room.get_empty_cells()[0]

    bot = Picobot(room, rules_text, start_position=start_pos)

    print(f"Starting at {start_pos}, state {bot.state}")
    print(f"Initial surroundings: {bot.get_surroundings()}")
    print("\nInitial room:")
    print(bot.display())

    # Run and show first few steps
    print("\nFirst 10 steps:")
    for i in range(10):
        if not bot.step():
            print(f"  Step {i}: HALTED - {bot._halt_reason}")
            break

        step = bot.history[-1]
        rule_str = str(step.rule_applied) if step.rule_applied else "None"
        print(f"  Step {i}: {step.surroundings} -> {rule_str} -> pos={step.new_position}, state={step.new_state}")

    # Complete the run
    result = bot.run(max_steps=50000)

    print(f"\nFinal state after {result['steps']} total steps:")
    print(bot.display())
    print(f"Coverage: {result['coverage']:.1f}%")
    print(f"Success: {result['success']}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("PICOBOT SOLUTION TESTER")
    print("=" * 60)

    all_passed = True

    # Test 1: Empty room with initial solution
    # Using smaller room for faster testing
    room_small = create_empty_room(15, 15)
    passed = test_solution(
        "Empty Room (15x15) - Initial 7-rule Solution",
        room_small,
        EMPTY_ROOM_INITIAL,
        test_all_positions=True
    )
    all_passed = all_passed and passed

    # Test 2: Empty room with standard size
    room_standard = create_empty_room(25, 25)
    passed = test_solution(
        "Empty Room (25x25) - Initial 7-rule Solution",
        room_standard,
        EMPTY_ROOM_INITIAL,
        test_all_positions=False,  # Too many positions, sample instead
        sample_positions=10
    )
    all_passed = all_passed and passed

    # Test 3: Small maze
    maze_small = create_small_maze()
    passed = test_solution(
        "Small Maze (9x9) - Initial 16-rule Solution",
        maze_small,
        MAZE_INITIAL,
        test_all_positions=True
    )
    all_passed = all_passed and passed

    # Test 4: Standard maze
    maze_standard = create_standard_maze()
    passed = test_solution(
        "Standard Maze (25x25) - Initial 16-rule Solution",
        maze_standard,
        MAZE_INITIAL,
        test_all_positions=False,  # Sample positions
        sample_positions=10
    )
    all_passed = all_passed and passed

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if all_passed:
        print("âœ“ All tests PASSED!")
    else:
        print("âœ— Some tests FAILED")
    print()

    return all_passed


if __name__ == "__main__":
    main()
