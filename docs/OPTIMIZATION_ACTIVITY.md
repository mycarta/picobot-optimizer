# Picobot Simulator Optimization Activity

**For:** Matteo + Sonnet in VS Code  
**Type:** Optional, self-contained tinkering project  
**Goal:** Learn NumPy optimization techniques by speeding up Picobot simulation  
**Prerequisite:** Working simulator from main project

---

## Why This Is Interesting

The Picobot simulator runs fine for single simulations. But verification requires testing from ALL starting positions (529 for empty room, 287 for maze). Currently this is a loop:

```python
for start_pos in all_positions:
    bot = Picobot(room, rules, start_pos)
    bot.run()
    results.append(bot.coverage)
```

**Question:** Can we vectorize this? Run all 529 simulations *simultaneously*?

**Spoiler:** Yes, with caveats. This is a great exercise in understanding where vectorization helps and where it doesn't.

---

## The Scope: What Can Actually Be Optimized

| Area | Current Approach | Vectorizable? | Potential Win |
|------|------------------|---------------|---------------|
| **Batch testing** | Loop 529 positions | YES — parallel sims | **Big** |
| **Rule lookup** | Linear search | YES — lookup table | **Big** |
| **Rule matching** | String comparison | YES — bit operations | Medium |
| **Surroundings** | Build string | Marginal | Small |
| **Core step loop** | Sequential | NO — step N needs step N-1 | None |

**Key insight:** The core simulation is sequential (can't vectorize), but we can run MANY simulations in parallel.

---

## Phase 1: Profile First (Don't Optimize Blind)

**Rule:** Never optimize without measuring. Find the actual bottleneck.

### Task 1.1: Add Timing

```python
import time

def benchmark_verification(room, rules, n_runs=3):
    """Time the full verification across all starting positions."""
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        result = test_rules_all_positions(room, rules, verbose=False)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    print(f"Mean: {np.mean(times):.3f}s, Std: {np.std(times):.3f}s")
    return times
```

### Task 1.2: Profile with cProfile

```python
import cProfile
import pstats

cProfile.run('test_rules_all_positions(room, rules)', 'profile_output')

stats = pstats.Stats('profile_output')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions by time
```

**Questions to answer:**
1. What percentage of time is in rule matching vs. position updates vs. coverage tracking?
2. Is the bottleneck in the inner loop (per step) or outer loop (per simulation)?
3. How much is Python overhead vs. actual computation?

---

## Phase 2: Lookup Table Optimization (O(1) Rule Matching)

**The Big Insight:** There are only:
- 100 possible states (0-99)
- 16 possible surroundings (2⁴ combinations)

So the entire rule logic fits in a `(100, 16)` lookup table. At runtime: one array index, no pattern matching.

### Task 2.1: Surroundings as Integer

Instead of building a string like `"xEWx"`, compute an integer 0-15:

```python
def surroundings_to_index(n_wall: bool, e_wall: bool, w_wall: bool, s_wall: bool) -> int:
    """
    Convert wall booleans to a surroundings index (0-15).
    
    Encoding: N=8, E=4, W=2, S=1 (bit positions)
    
    Examples:
        xxxx (no walls) → 0
        Nxxx (north wall only) → 8
        NEWS (all walls) → 15
        xEWx → 4 + 2 = 6
    """
    return (n_wall << 3) | (e_wall << 2) | (w_wall << 1) | s_wall
```

**Exercise:** Write the inverse function `index_to_surroundings(idx: int) -> str`.

### Task 2.2: Expand Patterns to Indices

A rule pattern like `x***` matches multiple surroundings:

```python
def pattern_to_indices(pattern: str) -> list[int]:
    """
    Expand a surroundings pattern to all matching indices.
    
    Examples:
        "xxxx" → [0]  
        "x***" → [0, 1, 2, 3, 4, 5, 6, 7]  # North empty (bit 3 = 0)
        "****" → list(range(16))
    """
    indices = []
    for idx in range(16):
        n_wall, e_wall, w_wall, s_wall = (
            bool(idx & 8), bool(idx & 4), bool(idx & 2), bool(idx & 1)
        )
        walls = [n_wall, e_wall, w_wall, s_wall]
        chars = ['N', 'E', 'W', 'S']
        
        match = True
        for i, (p_char, is_wall) in enumerate(zip(pattern, walls)):
            if p_char == '*':
                continue
            elif p_char == 'x' and is_wall:
                match = False
                break
            elif p_char == chars[i] and not is_wall:
                match = False
                break
        
        if match:
            indices.append(idx)
    
    return indices
```

### Task 2.3: Build the Lookup Table

```python
import numpy as np

DIRECTION_TO_INT = {'N': 0, 'E': 1, 'W': 2, 'S': 3, 'X': 4}

MOVE_VECTORS_NP = np.array([
    [-1, 0],  # N
    [0, 1],   # E
    [0, -1],  # W
    [1, 0],   # S
    [0, 0],   # X
], dtype=np.int8)

def build_lookup_table(rules: list) -> np.ndarray:
    """
    Build O(1) lookup table from rules.
    
    Returns: shape (100, 16, 2) — [direction_int, new_state]
             -1 means no matching rule
    """
    table = np.full((100, 16, 2), -1, dtype=np.int8)
    
    for rule in rules:
        direction_int = DIRECTION_TO_INT[rule.direction]
        
        for idx in pattern_to_indices(rule.surroundings_pattern):
            # First matching rule wins
            if table[rule.state, idx, 0] == -1:
                table[rule.state, idx, 0] = direction_int
                table[rule.state, idx, 1] = rule.new_state
    
    return table
```

### Task 2.4: Optimized Step

```python
class PicobotOptimized:
    def __init__(self, room_np, lookup_table, start_pos):
        self.room = room_np  # NumPy array
        self.table = lookup_table
        self.row, self.col = start_pos
        self.state = 0
        self.visited = {start_pos}
    
    def step(self) -> bool:
        # Get surroundings index — bit operations, no string building
        surr_idx = self._get_surroundings_index()
        
        # Lookup — O(1) array access, no loop
        action = self.table[self.state, surr_idx]
        
        if action[0] == -1:
            return False  # No rule
        
        direction_int, new_state = action
        
        # Move
        dr, dc = MOVE_VECTORS_NP[direction_int]
        self.row += dr
        self.col += dc
        self.state = new_state
        self.visited.add((self.row, self.col))
        
        return True
    
    def _get_surroundings_index(self) -> int:
        r, c = self.row, self.col
        n = r == 0 or self.room[r-1, c] == 1
        e = c == self.room.shape[1]-1 or self.room[r, c+1] == 1
        w = c == 0 or self.room[r, c-1] == 1
        s = r == self.room.shape[0]-1 or self.room[r+1, c] == 1
        return (n << 3) | (e << 2) | (w << 1) | s
```

---

## Phase 3: Batch Simulation (The Real Win)

Run ALL starting positions simultaneously.

### Task 3.1: Parallel State Representation

```python
class BatchPicobot:
    """Run N simulations in parallel using NumPy arrays."""
    
    def __init__(self, room_np, lookup_table, start_positions):
        self.room = room_np
        self.table = lookup_table
        self.n_bots = len(start_positions)
        
        # Parallel state: (n_bots,) arrays
        self.rows = np.array([p[0] for p in start_positions], dtype=np.int16)
        self.cols = np.array([p[1] for p in start_positions], dtype=np.int16)
        self.states = np.zeros(self.n_bots, dtype=np.int8)
        
        # Visited: (n_bots, height, width) — memory intensive!
        self.visited = np.zeros((self.n_bots, *room_np.shape), dtype=bool)
        for i, (r, c) in enumerate(start_positions):
            self.visited[i, r, c] = True
        
        # Active mask: which bots are still running
        self.active = np.ones(self.n_bots, dtype=bool)
        self.total_empty = (room_np == 0).sum()
```

### Task 3.2: Vectorized Step

```python
def step_all(self):
    """Advance all active bots by one step."""
    if not self.active.any():
        return False
    
    # Get surroundings indices for all active bots (vectorized)
    active_idx = np.where(self.active)[0]
    surr_indices = self._get_surroundings_batch(active_idx)
    
    # Lookup actions for all active bots (fancy indexing)
    active_states = self.states[active_idx]
    actions = self.table[active_states, surr_indices]  # Shape: (n_active, 2)
    
    # Check for stuck bots (no matching rule)
    stuck = actions[:, 0] == -1
    if stuck.any():
        self.active[active_idx[stuck]] = False
        active_idx = active_idx[~stuck]
        actions = actions[~stuck]
    
    if len(active_idx) == 0:
        return False
    
    # Apply moves (vectorized)
    directions = actions[:, 0]
    new_states = actions[:, 1]
    
    moves = MOVE_VECTORS_NP[directions]  # Shape: (n_active, 2)
    self.rows[active_idx] += moves[:, 0]
    self.cols[active_idx] += moves[:, 1]
    self.states[active_idx] = new_states
    
    # Mark visited (loop — hard to vectorize)
    for i, bot_idx in enumerate(active_idx):
        r, c = self.rows[bot_idx], self.cols[bot_idx]
        self.visited[bot_idx, r, c] = True
    
    # Check for completion
    coverage = self.visited.reshape(self.n_bots, -1).sum(axis=1)
    complete = coverage >= self.total_empty
    self.active[complete] = False
    
    return self.active.any()

def _get_surroundings_batch(self, indices):
    """Get surroundings indices for multiple bots."""
    r = self.rows[indices]
    c = self.cols[indices]
    
    n = (r == 0) | (self.room[np.clip(r-1, 0, None), c] == 1)
    e = (c == self.room.shape[1]-1) | (self.room[r, np.clip(c+1, None, self.room.shape[1]-1)] == 1)
    w = (c == 0) | (self.room[r, np.clip(c-1, 0, None)] == 1)
    s = (r == self.room.shape[0]-1) | (self.room[np.clip(r+1, None, self.room.shape[0]-1), c] == 1)
    
    return (n.astype(np.int8) << 3) | (e.astype(np.int8) << 2) | (w.astype(np.int8) << 1) | s.astype(np.int8)
```

---

## Phase 4: Benchmark and Compare

```python
def compare_implementations(size=25, n_trials=3):
    """Compare original vs optimized vs batch."""
    from picobot.simulator import Room, test_rules_all_positions, parse_rules
    from picobot.solutions.optimized import EMPTY_ROOM_6_RULES
    
    # Setup
    room_orig = Room.empty_room(size, size)
    room_np = np.array([[1 if c.value == 1 else 0 for c in row] for row in room_orig.grid], dtype=np.int8)
    rules = parse_rules(EMPTY_ROOM_6_RULES)
    lookup_table = build_lookup_table(rules)
    empty_positions = [(r, c) for r in range(size) for c in range(size) if room_np[r, c] == 0]
    
    # Original
    times_orig = []
    for _ in range(n_trials):
        start = time.perf_counter()
        test_rules_all_positions(room_orig, EMPTY_ROOM_6_RULES, verbose=False)
        times_orig.append(time.perf_counter() - start)
    
    # Optimized (single, with lookup table)
    times_opt = []
    for _ in range(n_trials):
        start = time.perf_counter()
        for pos in empty_positions:
            bot = PicobotOptimized(room_np, lookup_table, pos)
            while bot.step() and len(bot.visited) < len(empty_positions):
                pass
        times_opt.append(time.perf_counter() - start)
    
    # Batch
    times_batch = []
    for _ in range(n_trials):
        start = time.perf_counter()
        batch = BatchPicobot(room_np, lookup_table, empty_positions)
        while batch.step_all():
            pass
        times_batch.append(time.perf_counter() - start)
    
    print(f"Original:  {np.mean(times_orig):.3f}s")
    print(f"Optimized: {np.mean(times_opt):.3f}s  ({np.mean(times_orig)/np.mean(times_opt):.1f}x)")
    print(f"Batch:     {np.mean(times_batch):.3f}s  ({np.mean(times_orig)/np.mean(times_batch):.1f}x)")
```

---

## Expected Results

| Approach | Time (25×25) | Speedup | Why |
|----------|--------------|---------|-----|
| Original | ~2.5s | 1× | String ops, linear rule search |
| Lookup table | ~0.3s | ~8× | O(1) rule matching |
| Batch | ~0.1s | ~25× | Amortized Python overhead |

---

## Phase 5: Memory vs Speed Tradeoffs

The batch approach uses a 3D visited array:

```
529 bots × 25 × 25 × 1 byte = 330 KB  ← Fine
529 bots × 100 × 100 × 1 byte = 5.3 MB  ← Still OK
529 bots × 500 × 500 × 1 byte = 132 MB  ← Getting heavy
```

**Challenge:** For large rooms, implement batched batching — run 100 bots at a time.

---

## Bonus Challenges

1. **Numba JIT** — Use `@numba.jit(nopython=True)` for the inner loop
2. **Sparse visited tracking** — Use sets instead of 3D array for large rooms
3. **GPU with CuPy** — For truly massive parallelism
4. **Visualization optimization** — The GIF generation is also slow; profile it!

---

## Deliverables

1. **Profiling results** — What's actually slow?
2. **`simulator_optimized.py`** — Lookup table + optimized single bot
3. **`simulator_batch.py`** — Parallel batch simulation
4. **Benchmark comparison** — Table of times and speedups
5. **Brief writeup** — What did you learn? What surprised you?

---

## For Sonnet in VS Code

When starting:
1. "Let's profile the current simulator"
2. "Implement the surroundings-to-index conversion"
3. "Build and test the lookup table"
4. "Implement BatchPicobot step by step"
5. "Run benchmarks and interpret"

**Remember:** This is exploratory. If something doesn't give the expected speedup, that's data!

---

*"The fastest code is code that doesn't run. The second fastest is code that does minimum work. A lookup table does both."*
