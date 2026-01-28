# Picobot Project - Session Handoff Document

**Last Updated:** January 28, 2026  
**Session:** 11

---

## Project Overview

**Goal:** Revisit Matteo's 10-year-old Picobot solutions, verify them, optimize them, document the journey, and create educational materials.

**The Arc (Expanded):**
1. ✅ Transcribe notes and verify solutions
2. ✅ Build Python simulator
3. ✅ Write Blog Post 1 (technical journey)
4. 🔄 **Optimize simulator (learning + pedagogy)**
5. ⏳ Write Blog Posts 2 & 3
6. ⏳ Publish GitHub repository with educational materials

---

## Current Status

### ✅ BLOG POST 1: READY FOR PUBLICATION

**Title:** "Picobot Revisited: Optimizing a Tiny Robot's Rules, Ten Years Later"

Final draft complete with:
- HMC "six rules" challenge context
- Corrected narrative flow
- Personal touches ("hooked me", "loved it")
- All GIFs and images in place
- AI/HI transparency statement

**Action:** Publish now.

---

### 🔄 NEXT: VS Code Work (Two Tasks)

**Task 1: GitHub Repository (Do First)**
- Needed for Post 1 link
- Refactor to package structure
- Polish README
- Push and get URL

**Task 2: Optimization (Then This)**
- Learning opportunity for Matteo
- Pedagogical content for others
- Material for Blog Post 3

**The Three Stages of Engineering:**

| Stage | Goal | Picobot Project | Status |
|-------|------|-----------------|--------|
| Make it work | Logic | Picobot rules (2015) | ✅ Done |
| Make it right | Quality | Python simulator | ✅ Done |
| Make it fast | Performance | Optimization | 🔄 **Next** |

**Optimization Techniques to Explore:**

| Technique | Learning Goal | Expected Speedup |
|-----------|---------------|------------------|
| Profiling (cProfile) | Don't guess, measure | — |
| Lookup table | O(1) vs O(n) complexity | ~8× |
| Bit operations | Efficient state encoding | Included |
| Batch simulation | Amortized Python overhead | ~25× total |
| NumPy broadcasting | When vectorization helps | — |

**Deliverables:**
1. `simulator_optimized.py` — Lookup table implementation
2. `simulator_batch.py` — Parallel batch simulation
3. Benchmark results and analysis
4. Documentation of learning journey (feeds Post 3)

**Guide:** `OPTIMIZATION_ACTIVITY_2026-01-27.md`

---

### ⏳ BLOG SERIES

| Post | Title | Status | Dependency |
|------|-------|--------|------------|
| 1 | Picobot Revisited: Optimizing Rules | ✅ Ready | None — publish now |
| 2 | Human + AI Collaboration | Planned | Post 1 published |
| 3 | Making It Fast: Profiling & Optimization | Planned | Optimization work done |

**Key principle:** Document the LEARNING journey, not just results. Show wrong turns, surprises, what clicked.

---

## Verified Solutions

| Problem | Rules | Positions | Status |
|---------|-------|-----------|--------|
| Empty Room | 6 | 529/529 | ✅ Verified |
| Maze | 12 | 287/287 | ✅ Verified |

**Hidden Assumptions Made Explicit:**
- Empty room: Must start in State 0
- Maze: Rules evaluated top-to-bottom ("Key is G")

---

## Files Summary

### Core Code
| File | Purpose | Status |
|------|---------|--------|
| `picobot_simulator.py` | Original simulator | ✅ Complete |
| `picobot_rooms.py` | Room utilities | ✅ Complete |
| `picobot_visualizer.py` | GIF generator | ✅ Complete |
| `optimized_solutions.py` | Verified solutions | ✅ Complete |
| `simulator_optimized.py` | Lookup table version | ⏳ To build |
| `simulator_batch.py` | Batch simulation | ⏳ To build |

### Documentation
| File | Purpose | Audience |
|------|---------|----------|
| `PROJECT_STATUS_2026-01-28.md` | This file | All contexts |
| `SESSION_11_SUMMARY_2026-01-28.md` | Detailed session notes | Continuity |
| `VSCODE_HANDOFF_2026-01-28.md` | VS Code tasks | Sonnet |
| `BLOG_HANDOFF_2026-01-28.md` | Blog planning | Opus |
| `OPTIMIZATION_ACTIVITY_2026-01-27.md` | Optimization guide | Matteo + Sonnet |
| `PEDAGOGY_NOTES_2026-01-27.md` | Educational design | All |

### Blog Assets
| File | Status |
|------|--------|
| `featured_image_picobot_maze.png` | ✅ Ready |
| `boustrophedon_pattern.gif` | ✅ Ready |
| `picobot_north_start_noloop.gif` | ✅ Ready |
| `lab_maze_12rule_noloop.gif` | ✅ Ready |

---

## Workflow by Context

### VS Code + Sonnet
1. Read `VSCODE_HANDOFF_2026-01-28.md`
2. Primary task: Optimization (follow `OPTIMIZATION_ACTIVITY`)
3. Secondary: GitHub repo setup, pedagogy exercises

### Opus (Blog)
1. Read `BLOG_HANDOFF_2026-01-28.md`
2. Post 2 after Post 1 published
3. Post 3 after optimization work complete

### Any New Context
1. Start with `PROJECT_STATUS_2026-01-28.md` (this file)
2. Check `SESSION_11_SUMMARY_2026-01-28.md` for detailed rationale

---

## Key Quotes

> "The optimization journey IS pedagogy."

> "Make it work → Make it right → Make it fast. Most CS courses stop at step 1."

> "Document the LEARNING process — show wrong turns, not just results."

---

## Next Actions

1. **VS Code + Sonnet:** Create GitHub repo (needed for Post 1)
2. **Matteo:** Publish Blog Post 1 (with repo link)
3. **VS Code + Sonnet:** Optimization work
4. **Document:** Learning journey as it happens
5. **Then:** Write Posts 2 & 3

---

*"The folder finally gets its due — and teaches others along the way."*
