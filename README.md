# Game #0 – Hyperstrate (working title: NodeForge)

**"Strategy is hypergraph construction under alternating selection pressure."**

a single Pygame application where players (or modders) can create, visualize, analyze, and play *any* two-player perfect-information strategy game by defining nodes, hyperedges, and targets.

## Initial Goals (v0.1 – Arithmetic Prototype – "Make the Number")
- Single-player arithmetic hypergraph builder (easiest on-ramp).
- Draggable nodes: numbers (leaves) + operators (hyperedges).
- Free rearrangement of the expression graph each turn.
- Live evaluation to a random or chosen target number.
- Combo-friendly strategy (add-then-multiply, grouping, order-of-operations tricks).
- Built-in AI opponent using the *exact same* math we use for rule-set analysis.
- Minimal but extensible code structure so we can iterate fast.

Run it with `python main.py` (requires pygame). First version ships with the arithmetic game; editor tabs and classic templates come in v0.2.

## Roadmap → End State

**v0.1** (now)  
Arithmetic prototype + basic metrics dashboard + depth-based AI.

**v0.2**  
Full editor (Nodes | Rules | Target | Play | Metrics).  
Load built-in templates (Color Alchemy, Tic-Tac-Toe++, Go-Lite, Chess).  
Hypergraph visualizer (convex-hull edges, live pulsing, hover inspection).

**v0.3**  
Two-player hotseat + online AI.  
Dynamic node-menu generation (so the game can emulate board games).  
Export/import rule sets as JSON.

**v0.4+**  
Community vault, MCTS for complex rules, game-history scrubber with hypergraph evolution, visual clarity scoring.

**End State (the dream)**  
A single executable where *anyone* can:  
1. Load a classic game as a hypergraph.  
2. Tweak one rule and instantly see balance/depth metrics.  
3. Play against an AI whose strength scales perfectly with the rule set.  
4. Discover brand-new games that feel as deep as Go or as tactical as chess — because the engine *is* the universal substrate.

## Maths We Use for Strategic Depth & Computer Opponent

We reuse **one unified simulation engine** for both offline analysis *and* live AI. No separate code paths.

### Core Metrics (Jaffe / Lantz style – already formalized in game-design literature)
- **Depth-d score**: Run self-play with restricted lookahead (depth-1 = greedy vs full minimax). Large gap = deep strategy.
- **First-player win % & draw rate** (target 45–55% balance).
- **Strategy diversity**: Cluster final hypergraphs by graph-edit distance.
- **Emergence**: Shannon entropy of rule firings across 1000 simulated games.

### Computer Opponent (online mode)
The AI is literally the Simulator class running in “live” mode:
- **State representation**: Current hypergraph + available moves.
- **Evaluation**: Same distance-to-target function used in live preview + bonuses (hyperedge density, combo potential).
- **Search**:
  - Easy = depth-1 greedy (immediate best move).
  - Medium = depth-3–5 alpha-beta / minimax.
  - Hard = full (or time-capped) minimax with the same heuristics extracted during offline analysis.
- For arithmetic graphs the state space is tiny → lightning fast.  
- For future board-game templates we drop in Monte-Carlo Tree Search (MCTS) using the same rollout logic we already run for metrics.

Result: the AI strength automatically matches the “goodness” of any rule set you create. No hand-tuning required.

