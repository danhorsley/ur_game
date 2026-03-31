"""Game-agnostic minimax solver for any HyperGraph game.

Works by enumerating available nodes, simulating claims, and recursing.
Alpha-beta pruning with move ordering included. Supports custom evaluation
functions for score-based games (not just binary win/loss).
"""

import random
import time
from graph import HyperGraph

PLAYERS = ("X", "O")


def _opponent(player: str) -> str:
    return "O" if player == "X" else "X"


def _default_evaluate(graph: HyperGraph, player: str) -> float:
    """Binary win/loss evaluation (original tic-tac-toe style)."""
    winner = graph.check_winner()
    if winner == player:
        return 1.0
    if winner == _opponent(player):
        return -1.0
    return 0.0


def _order_moves(graph, available, player, evaluate):
    """Order moves by quick evaluation — best-looking moves first.

    This dramatically improves alpha-beta pruning by letting it cut
    branches early.
    """
    scored = []
    for nid in available:
        g = graph.copy()
        g.claim_node(nid, player)
        score = evaluate(g, player)
        scored.append((score, nid))
    scored.sort(reverse=True)
    return [nid for _, nid in scored]


def _minimax(graph: HyperGraph, player: str, maximizing: bool,
             depth: int, alpha: float, beta: float,
             evaluate, deadline: float) -> float:
    # Time limit check
    if time.time() > deadline:
        return evaluate(graph, player)

    # Terminal: board full or depth exhausted
    if graph.is_full() or depth == 0:
        return evaluate(graph, player)

    current = player if maximizing else _opponent(player)
    available = graph.available_nodes()

    # Move ordering: sort by evaluation for better pruning
    if depth >= 2 and len(available) > 4:
        available = _order_moves(graph, available, current, evaluate)

    if maximizing:
        best = -2.0
        for nid in available:
            g = graph.copy()
            g.claim_node(nid, current)
            val = _minimax(g, player, False, depth - 1, alpha, beta, evaluate, deadline)
            best = max(best, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best
    else:
        best = 2.0
        for nid in available:
            g = graph.copy()
            g.claim_node(nid, current)
            val = _minimax(g, player, True, depth - 1, alpha, beta, evaluate, deadline)
            best = min(best, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best


def best_move(graph, player, difficulty="hard", evaluate=None):
    """Return the best node_id for player to claim.

    difficulty: 'easy' (random), 'medium' (depth-2), 'hard' (depth-4 with time limit)
    evaluate: callable(graph, player) -> float in [-1, 1]. Defaults to binary win/loss.
    """
    if evaluate is None:
        evaluate = _default_evaluate

    available = graph.available_nodes()
    if not available:
        return None

    if difficulty == "easy":
        # Mostly random but occasionally picks a good move
        if random.random() < 0.3:
            max_depth = 1
        else:
            return random.choice(available)
    elif difficulty == "medium":
        max_depth = 2
    else:
        max_depth = 4

    # Time limit: 1.5 seconds max for hard, 0.5 for medium
    time_limit = 1.5 if difficulty == "hard" else 0.5
    deadline = time.time() + time_limit

    # Use move ordering at top level too
    ordered = _order_moves(graph, available, player, evaluate)

    best_score = -2.0
    best_moves = []
    for nid in ordered:
        if time.time() > deadline:
            # If we haven't evaluated any moves yet, use the first ordered move
            if not best_moves:
                best_moves = [ordered[0]]
            break

        g = graph.copy()
        g.claim_node(nid, player)
        score = _minimax(g, player, False, max_depth - 1, -2.0, 2.0, evaluate, deadline)
        if score > best_score:
            best_score = score
            best_moves = [nid]
        elif score == best_score:
            best_moves.append(nid)

    return random.choice(best_moves)
