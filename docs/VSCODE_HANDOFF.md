# Picobot Project Handoff for VS Code / GitHub

**Date:** January 28, 2026  
**For:** Matteo + Claude Sonnet 4.5 in VS Code  
**Primary Task:** Simulator Optimization (learning + pedagogy)

---

## 🎯 TASK 0: Organize Working Folder (First Thing)

The project files are currently flat. Before anything else, reorganize into proper structure:

**Current (flat):**
```
picobot-optimizer/
├── picobot_simulator.py
├── picobot_rooms.py
├── ... (all files flat)
```

**Target structure:**
```
picobot-optimizer/
├── .github/
│   └── copilot-instructions.md
├── picobot/
│   ├── __init__.py
│   ├── simulator.py
│   ├── rooms.py
│   ├── visualizer.py
│   └── solutions/
│       ├── __init__.py
│       ├── initial.py
│       └── optimized.py
├── tests/
│   ├── __init__.py
│   └── test_solutions.py
├── animations/
│   └── (GIFs)
├── docs/
│   ├── OPTIMIZATION_ACTIVITY.md
│   ├── PEDAGOGY_NOTES.md
│   └── PROJECT_STATUS.md
├── README.md
├── requirements.txt
└── LICENSE
```

**Steps:**
1. Create directories: `picobot/`, `picobot/solutions/`, `tests/`, `docs/`, `.github/`
2. Move and rename Python files per mapping below
3. Create `__init__.py` files
4. Create `requirements.txt`
5. Fix imports in all files
6. Test that imports work

---

## 🎯 TASK 1: GitHub Repository Setup

**Why first:** Post 1 needs a link to the repo. Get this done before publishing.

### Repository Structure

```
picobot-optimizer/
├── README.md                    # Polish for GitHub (see below)
├── LICENSE                      # MIT
├── requirements.txt
├── picobot/
│   ├── __init__.py
│   ├── simulator.py             # From picobot_simulator.py
│   ├── rooms.py                 # From picobot_rooms.py
│   ├── visualizer.py            # From picobot_visualizer.py
│   └── solutions/
│       ├── __init__.py
│       ├── initial.py           # From initial_solutions.py
│       └── optimized.py         # From optimized_solutions.py
├── tests/
│   ├── __init__.py
│   └── test_solutions.py
├── examples/
│   └── basic_usage.py
├── animations/
│   ├── empty_room_demo.gif
│   └── lab_maze_demo.gif
└── docs/
    └── optimization_journey.md   # Placeholder for later
```

### Steps

1. Create repo on GitHub (public, MIT license)
2. Refactor imports for package structure
3. Add `__init__.py` files
4. Copy and rename files per table below
5. Test that imports work
6. Push initial commit
7. **Give Matteo the repo URL for Post 1**

### File Mapping

| Current | Target |
|---------|--------|
| `picobot_simulator.py` | `picobot/simulator.py` |
| `picobot_rooms.py` | `picobot/rooms.py` |
| `picobot_visualizer.py` | `picobot/visualizer.py` |
| `initial_solutions.py` | `picobot/solutions/initial.py` |
| `optimized_solutions.py` | `picobot/solutions/optimized.py` |
| `test_solutions.py` | `tests/test_solutions.py` |

### Import Fixes

Change hardcoded paths like:
```python
from picobot_simulator import Picobot, Room
```

To package imports:
```python
from picobot.simulator import Picobot, Room
```

### README Polishing

The existing README is solid but needs GitHub polish:
- Add badges (Python version, license, tests passing)
- Add installation section (`pip install -e .` or similar)
- Add quick start code example
- Link to blog post (once published)
- Add "Contributing" section (optional)
- Verify all code examples still work after refactor

---

## 🎯 TASK 2: Optimization Work (After Repo)

### Why This Is Priority

The optimization work serves THREE purposes:
1. **Learning for Matteo** — NumPy, profiling, vectorization, performance thinking
2. **Pedagogy for others** — Teaching "Make it fast" as the third engineering stage
3. **Blog Post 3 material** — Document the journey as it happens

### The Engineering Progression

| Stage | Mantra | Picobot Project | Status |
|-------|--------|-----------------|--------|
| 1 | Make it work | Picobot rules | ✅ Done (2015) |
| 2 | Make it right | Python simulator | ✅ Done |
| 3 | **Make it fast** | **Optimization** | 🔄 **NOW** |

Most CS courses stop at stage 1. This project completes all three.

---

## Optimization Guide

**Full details:** `OPTIMIZATION_ACTIVITY_2026-01-27.md`

### Phase 1: Profile First (Don't Skip This!)

```python
import cProfile
import pstats

cProfile.run('test_rules_all_positions(room, rules)', 'profile_output')
stats = pstats.Stats('profile_output')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**Questions to answer:**
- Where does time actually go?
- Is it rule matching? String building? Coverage tracking?
- What percentage is Python overhead vs computation?

### Phase 2: Lookup Table (O(1) Rule Matching)

**Key insight:** Only 100 states × 16 surroundings = 1600 possible situations. Precompute everything.

```python
# Surroundings as integer (0-15)
def surroundings_to_index(n, e, w, s):
    return (n << 3) | (e << 2) | (w << 1) | s

# Build lookup table
table = np.full((100, 16, 2), -1, dtype=np.int8)  # [direction, new_state]
```

**Expected speedup:** ~8×

### Phase 3: Batch Simulation (Run All Positions Simultaneously)

Instead of:
```python
for pos in all_529_positions:
    bot = Picobot(room, rules, pos)
    bot.run()
```

Do:
```python
batch = BatchPicobot(room, rules, all_529_positions)
batch.run()  # All positions advance in parallel
```

**Expected speedup:** ~25× total (lookup + batch combined)

### Phase 4: Benchmark and Document

```python
print(f"Original:  {t_orig:.3f}s")
print(f"Optimized: {t_opt:.3f}s  ({t_orig/t_opt:.1f}x faster)")
```

**Document as you go:**
- What surprised you?
- What didn't work?
- What clicked?

This becomes Post 3 material.

---

## Deliverables

### Task 1: GitHub Repo
| Deliverable | Notes |
|-------------|-------|
| Public repo URL | For Post 1 link |
| Working package imports | `from picobot.simulator import ...` |
| README polished | For GitHub audience |
| MIT LICENSE | Standard open source |

### Task 2: Optimization
| File | Purpose | Priority |
|------|---------|----------|
| `benchmark_original.py` | Baseline measurements | Do first |
| `picobot/simulator_optimized.py` | Lookup table version | Core |
| `picobot/simulator_batch.py` | Parallel batch simulation | Core |
| `benchmarks/comparison.py` | Side-by-side results | After both work |
| `docs/OPTIMIZATION_JOURNAL.md` | Learning notes | Ongoing |

---

## Task 3 (Later): Pedagogy Exercises

**File:** `PEDAGOGY_NOTES_2026-01-27.md`

Three skills with progressive exercises:
1. Formal state machine representation
2. The X move (productive staying put)
3. Exhaustive case enumeration

Plus broken examples for debugging practice.

**Do after:** Optimization work complete (exercises can reference optimized code).

---

## Technical Reference

### Current Solutions (Verified)

**Empty Room (6 rules):**
```
0 x*** -> N 0
0 N*** -> X 1
1 *x** -> E 1
1 *E** -> W 2
2 **x* -> W 2
2 **W* -> S 1
```
⚠️ Requires State 0 start

**Maze (12 rules):**
```
0 *x** -> E 1    0 xE** -> N 0    0 NE** -> X 2
1 ***x -> S 3    1 *x*S -> E 1    1 *E*S -> X 0
2 x*** -> N 0    2 N*x* -> W 2    2 N*W* -> X 3
3 **x* -> W 2    3 **Wx -> S 3    3 **WS -> X 1
```

### Key Constants for Optimization

```python
# Direction encoding
DIRECTION_TO_INT = {'N': 0, 'E': 1, 'W': 2, 'S': 3, 'X': 4}

# Move vectors
MOVE_VECTORS = np.array([
    [-1, 0],  # N
    [0, 1],   # E
    [0, -1],  # W
    [1, 0],   # S
    [0, 0],   # X
], dtype=np.int8)

# Surroundings encoding: N=8, E=4, W=2, S=1
```

---

## Dependencies

### requirements.txt
```
numpy>=1.21.0
matplotlib>=3.5.0
Pillow>=9.0.0
```

### For benchmarking
```
pytest>=7.0.0
pytest-benchmark>=4.0.0  # Optional
```

---

## Questions to Ask Sonnet

1. "Let's profile the current simulator — what's actually slow?"
2. "Help me implement the surroundings-to-index encoding"
3. "Build and test the lookup table"
4. "Implement BatchPicobot step by step"
5. "Why isn't X giving the speedup I expected?" (when things don't work)

---

## Documentation Notes

### What to Document (for Post 3)

As you work, note:
- **Expectations vs reality** — "I thought X, but actually Y"
- **Dead ends** — What didn't work and why
- **Aha moments** — When something clicked
- **Transferable lessons** — What applies beyond Picobot

### Format

Keep an `OPTIMIZATION_JOURNAL.md` with dated entries:

```markdown
## 2026-01-28: Profiling Results

Ran cProfile on 25×25 room verification.

**Surprise:** Rule matching is only 15% of time. String building in
get_surroundings() is 40%!

**Implication:** Lookup table alone won't give 10×. Need to fix
surroundings encoding first.
```

---

## Context Files

| File | Purpose |
|------|---------|
| `PROJECT_STATUS_2026-01-28.md` | Overall project state |
| `SESSION_11_SUMMARY_2026-01-28.md` | Why optimization is priority |
| `OPTIMIZATION_ACTIVITY_2026-01-27.md` | Detailed optimization guide |
| `PEDAGOGY_NOTES_2026-01-27.md` | Educational design |
| `BLOG_HANDOFF_2026-01-28.md` | Blog series planning |

---

## Success Criteria

### Task 1: GitHub Repo ✓ when:
- [ ] Repo is public on GitHub
- [ ] Package imports work (`from picobot.simulator import Picobot`)
- [ ] Tests pass
- [ ] README is polished
- [ ] Matteo has URL for Post 1

### Task 2: Optimization ✓ when:
- [ ] Profiling results documented
- [ ] Lookup table implementation passes all tests
- [ ] Batch simulation passes all tests
- [ ] Benchmark numbers documented (speedup measured)
- [ ] Learning journal has entries for Post 3

---

*"Profile first. Measure always. Document the journey."*
