"""Hyperstrate v0.2 — Chromatic: Color-Mixing Hypergraph Strategy Game.

Players alternate claiming colored nodes (R/G/B). Completing a recipe
(hyperedge of 3 nodes) scores points. Recipes are shown as filled triangles
so you can SEE the shapes you're building.
"""

import pygame
import sys
import math
import time
from graph import HyperGraph
from ai import best_move

# ── constants ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1100, 750
BG = (20, 20, 30)
NODE_RADIUS = 28
BOARD_OFFSET_X = 40
BOARD_OFFSET_Y = 20

# Node type colors
RED_NODE = (220, 60, 60)
GREEN_NODE = (60, 200, 80)
BLUE_NODE = (60, 100, 220)
NODE_COLORS = {"R": RED_NODE, "G": GREEN_NODE, "B": BLUE_NODE}

# Recipe result colors
PURPLE = (170, 70, 200)
YELLOW = (220, 200, 40)
CYAN = (40, 200, 220)
WHITE_MIX = (210, 210, 230)

RECIPE_COLORS = {
    "purple": PURPLE, "yellow": YELLOW, "cyan": CYAN, "white": WHITE_MIX,
}

# Point values
RECIPE_POINTS = {"purple": 1, "yellow": 1, "cyan": 1, "white": 3}

# Owner indication
P1_BORDER = (255, 255, 255)
P2_BORDER = (50, 50, 50)
UNCLAIMED_BORDER = (100, 100, 110)

# Player colors for HUD
X_COLOR = (180, 200, 255)
O_COLOR = (255, 150, 150)

DIFFICULTIES = ["easy", "medium", "hard"]

# RPS: purple beats yellow, yellow beats cyan, cyan beats purple
RPS_CANCELS = {"purple": "yellow", "yellow": "cyan", "cyan": "purple"}


# ── build the chromatic hypergraph ──────────────────────────────────────────
def make_chromatic() -> HyperGraph:
    """Create 18-node, 24-hyperedge color-mixing game board."""
    g = HyperGraph()

    spacing_x = 110
    spacing_y = 110
    row_offset = 55
    base_x = 160 + BOARD_OFFSET_X
    base_y = 100 + BOARD_OFFSET_Y

    node_defs = [
        # Row 0: 5 nodes
        ("R0", "R", base_x, base_y),
        ("G0", "G", base_x + spacing_x, base_y),
        ("B0", "B", base_x + spacing_x * 2, base_y),
        ("R1", "R", base_x + spacing_x * 3, base_y),
        ("G1", "G", base_x + spacing_x * 4, base_y),
        # Row 1: 4 nodes (offset)
        ("B1", "B", base_x + row_offset, base_y + spacing_y),
        ("G2", "G", base_x + row_offset + spacing_x, base_y + spacing_y),
        ("R2", "R", base_x + row_offset + spacing_x * 2, base_y + spacing_y),
        ("B2", "B", base_x + row_offset + spacing_x * 3, base_y + spacing_y),
        # Row 2: 5 nodes
        ("G3", "G", base_x, base_y + spacing_y * 2),
        ("R3", "R", base_x + spacing_x, base_y + spacing_y * 2),
        ("B3", "B", base_x + spacing_x * 2, base_y + spacing_y * 2),
        ("G4", "G", base_x + spacing_x * 3, base_y + spacing_y * 2),
        ("R4", "R", base_x + spacing_x * 4, base_y + spacing_y * 2),
        # Row 3: 4 nodes (offset)
        ("B4", "B", base_x + row_offset, base_y + spacing_y * 3),
        ("R5", "R", base_x + row_offset + spacing_x, base_y + spacing_y * 3),
        ("G5", "G", base_x + row_offset + spacing_x * 2, base_y + spacing_y * 3),
        ("B5", "B", base_x + row_offset + spacing_x * 3, base_y + spacing_y * 3),
    ]

    for nid, color_type, x, y in node_defs:
        g.add_node(nid, x=x, y=y, color_type=color_type, label=nid)

    # ── Recipes: ALL 3-node ──
    # White (R+G+B) — 3 points, never cancelled
    g.add_hyperedge(["R0", "G0", "B0"], recipe="white", label="R0+G0+B0", color=WHITE_MIX)
    g.add_hyperedge(["R1", "G1", "B0"], recipe="white", label="R1+G1+B0", color=WHITE_MIX)
    g.add_hyperedge(["R3", "G2", "B3"], recipe="white", label="R3+G2+B3", color=WHITE_MIX)
    g.add_hyperedge(["R2", "G4", "B2"], recipe="white", label="R2+G4+B2", color=WHITE_MIX)
    g.add_hyperedge(["R5", "G3", "B4"], recipe="white", label="R5+G3+B4", color=WHITE_MIX)
    g.add_hyperedge(["R5", "G5", "B5"], recipe="white", label="R5+G5+B5", color=WHITE_MIX)

    # Purple (R+B mix) — 1 point each
    g.add_hyperedge(["R0", "B1", "R3"], recipe="purple", label="R0+B1+R3", color=PURPLE)
    g.add_hyperedge(["R1", "B2", "R4"], recipe="purple", label="R1+B2+R4", color=PURPLE)
    g.add_hyperedge(["R2", "B0", "R1"], recipe="purple", label="R2+B0+R1", color=PURPLE)
    g.add_hyperedge(["R5", "B3", "B4"], recipe="purple", label="R5+B3+B4", color=PURPLE)
    g.add_hyperedge(["R4", "B5", "B2"], recipe="purple", label="R4+B5+B2", color=PURPLE)
    g.add_hyperedge(["R3", "B3", "R2"], recipe="purple", label="R3+B3+R2", color=PURPLE)

    # Yellow (R+G mix) — 1 point each
    g.add_hyperedge(["R0", "G0", "R1"], recipe="yellow", label="R0+G0+R1", color=YELLOW)
    g.add_hyperedge(["G2", "R3", "G3"], recipe="yellow", label="G2+R3+G3", color=YELLOW)
    g.add_hyperedge(["R2", "G1", "G4"], recipe="yellow", label="R2+G1+G4", color=YELLOW)
    g.add_hyperedge(["R5", "G3", "G5"], recipe="yellow", label="R5+G3+G5", color=YELLOW)
    g.add_hyperedge(["R4", "G4", "G5"], recipe="yellow", label="R4+G4+G5", color=YELLOW)
    g.add_hyperedge(["R3", "G2", "R2"], recipe="yellow", label="R3+G2+R2", color=YELLOW)

    # Cyan (B+G mix) — 1 point each
    g.add_hyperedge(["B0", "G0", "G1"], recipe="cyan", label="B0+G0+G1", color=CYAN)
    g.add_hyperedge(["B1", "G3", "G2"], recipe="cyan", label="B1+G3+G2", color=CYAN)
    g.add_hyperedge(["B2", "G4", "G1"], recipe="cyan", label="B2+G4+G1", color=CYAN)
    g.add_hyperedge(["B4", "G3", "B3"], recipe="cyan", label="B4+G3+B3", color=CYAN)
    g.add_hyperedge(["B5", "G5", "G4"], recipe="cyan", label="B5+G5+G4", color=CYAN)
    g.add_hyperedge(["B1", "G2", "B0"], recipe="cyan", label="B1+G2+B0", color=CYAN)

    return g


# ── scoring ────────────────────────────────────────────────────────────────
def count_recipes(graph, player):
    """Count completed recipes by type for a player."""
    counts = {"purple": 0, "yellow": 0, "cyan": 0, "white": 0}
    for edge in graph.winning_edges(player):
        recipe = edge.get("recipe", "")
        if recipe in counts:
            counts[recipe] += 1
    return counts


def compute_score(graph, player):
    """Compute score for player with RPS cancellation."""
    opp = "O" if player == "X" else "X"
    my = count_recipes(graph, player)
    their = count_recipes(graph, opp)

    # RPS cancellation
    eff_purple = max(0, my["purple"] - their["cyan"])
    eff_yellow = max(0, my["yellow"] - their["purple"])
    eff_cyan = max(0, my["cyan"] - their["yellow"])

    return eff_purple + eff_yellow + eff_cyan + my["white"] * 3


def evaluate_chromatic(graph, player):
    """AI evaluation function."""
    opp = "O" if player == "X" else "X"
    my_score = compute_score(graph, player)
    opp_score = compute_score(graph, opp)
    max_possible = 30.0
    return max((min((my_score - opp_score) / max_possible, 1.0)), -1.0)


# ── edge status helpers ────────────────────────────────────────────────────
def edge_status(graph, edge, player):
    """Return (owned_by_player, owned_by_opp, unclaimed) counts."""
    opp = "O" if player == "X" else "X"
    p_count = o_count = free = 0
    for nid in edge["nodes"]:
        owner = graph.nodes[nid]["owner"]
        if owner == player:
            p_count += 1
        elif owner == opp:
            o_count += 1
        else:
            free += 1
    return p_count, o_count, free


def is_cancelled(graph, edge, player):
    """Check if a completed edge is RPS-cancelled by opponent."""
    recipe = edge.get("recipe", "")
    if recipe == "white" or recipe not in RPS_CANCELS:
        return False
    cancelled_by = {"purple": "cyan", "yellow": "purple", "cyan": "yellow"}
    canceller = cancelled_by.get(recipe, "")
    if not canceller:
        return False
    opp = "O" if player == "X" else "X"
    my_count = sum(1 for e in graph.winning_edges(player) if e.get("recipe") == recipe)
    opp_canceller_count = sum(1 for e in graph.winning_edges(opp) if e.get("recipe") == canceller)
    cancelled_count = min(my_count, opp_canceller_count)
    return cancelled_count > 0 and cancelled_count >= my_count


# ── drawing helpers ─────────────────────────────────────────────────────────
def get_triangle_points(graph, edge):
    """Get the 3 vertex positions for a triangle edge."""
    node_ids = sorted(edge["nodes"])
    return [(int(graph.nodes[n]["x"]), int(graph.nodes[n]["y"])) for n in node_ids]


def draw_triangle(surface, graph, edge, alpha=30, outline_width=0,
                  pulse=False, cancelled=False, owner=None):
    """Draw a filled triangle for a 3-node hyperedge."""
    color = edge.get("color", (150, 150, 150))
    pts = get_triangle_points(graph, edge)

    if pulse:
        t = (math.sin(time.time() * 4) + 1) / 2
        fill_alpha = int(40 + 60 * t)
        outline_alpha = int(150 + 105 * t)
        outline_w = int(3 + 3 * t)
    else:
        fill_alpha = alpha
        outline_alpha = min(255, alpha + 60)
        outline_w = outline_width

    if cancelled:
        fill_alpha = max(8, fill_alpha // 4)
        outline_alpha = max(20, outline_alpha // 4)
        outline_w = max(1, outline_w - 1)

    # Filled triangle
    tri_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fill_color = (*color, fill_alpha)
    pygame.draw.polygon(tri_surface, fill_color, pts)

    # Outline
    if outline_w > 0:
        outline_color = (*color, outline_alpha)
        pygame.draw.polygon(tri_surface, outline_color, pts, outline_w)

    # Owner indicator: small icon at centroid
    if owner and not cancelled:
        cx = sum(p[0] for p in pts) // 3
        cy = sum(p[1] for p in pts) // 3
        if owner == "X":
            indicator_color = (*P1_BORDER, min(255, outline_alpha))
        else:
            indicator_color = (*O_COLOR, min(255, outline_alpha))
        pygame.draw.circle(tri_surface, indicator_color, (cx, cy), 6)

    surface.blit(tri_surface, (0, 0))


def draw_node(surface, node_id, data, font, is_last_move=False):
    x, y = int(data["x"]), int(data["y"])
    owner = data["owner"]
    color_type = data.get("color_type", "R")

    fill = NODE_COLORS.get(color_type, (150, 150, 150))

    if owner is None:
        fill = tuple(max(30, c - 40) for c in fill)
        border = UNCLAIMED_BORDER
        border_width = 2
    elif owner == "X":
        border = P1_BORDER
        border_width = 4
    else:
        border = P2_BORDER
        border_width = 4

    # Last move highlight — pulsing ring
    if is_last_move:
        t = (math.sin(time.time() * 6) + 1) / 2
        ring_alpha = int(100 + 155 * t)
        ring_color = X_COLOR if owner == "X" else O_COLOR
        ring_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*ring_color, ring_alpha), (x, y), NODE_RADIUS + 8, 3)
        surface.blit(ring_surf, (0, 0))

    pygame.draw.circle(surface, fill, (x, y), NODE_RADIUS)
    pygame.draw.circle(surface, border, (x, y), NODE_RADIUS, border_width)

    if owner:
        txt = font.render(owner, True, (255, 255, 255) if owner == "X" else (20, 20, 20))
        surface.blit(txt, (x - txt.get_width() // 2, y - txt.get_height() // 2))
    else:
        txt = font.render(color_type, True, (255, 255, 255, 120))
        surface.blit(txt, (x - txt.get_width() // 2, y - txt.get_height() // 2))


def node_at_pos(graph, mx, my):
    for nid, data in graph.nodes.items():
        dx = data["x"] - mx
        dy = data["y"] - my
        if dx * dx + dy * dy <= NODE_RADIUS * NODE_RADIUS:
            return nid
    return None


def format_score(score):
    if score == int(score):
        return str(int(score))
    return f"{score:.1f}"


# ── event log ──────────────────────────────────────────────────────────────
class EventLog:
    """Tracks recent game events for display."""
    def __init__(self, max_events=6):
        self.events = []
        self.max_events = max_events

    def add(self, text, color, timestamp=None):
        self.events.append({
            "text": text,
            "color": color,
            "time": timestamp or time.time(),
        })
        if len(self.events) > self.max_events:
            self.events.pop(0)

    def clear(self):
        self.events = []

    def draw(self, surface, font, x, y):
        now = time.time()
        for i, event in enumerate(reversed(self.events)):
            age = now - event["time"]
            # Fade out after 8 seconds
            if age > 10:
                continue
            alpha = 255 if age < 6 else int(255 * (1 - (age - 6) / 4))
            alpha = max(0, min(255, alpha))
            color = event["color"]
            txt = font.render(event["text"], True, color)
            txt.set_alpha(alpha)
            surface.blit(txt, (x, y + i * 16))


# ── main ────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hyperstrate — Chromatic")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("monospace", 20, bold=True)
    small_font = pygame.font.SysFont("monospace", 14)
    title_font = pygame.font.SysFont("monospace", 20, bold=True)
    score_font = pygame.font.SysFont("monospace", 24, bold=True)
    tooltip_font = pygame.font.SysFont("monospace", 13)
    event_font = pygame.font.SysFont("monospace", 13)

    graph = make_chromatic()
    current_player = "X"
    game_over = False
    difficulty_idx = 2
    hover_node = None
    message = "Your turn (X)"
    last_move = None  # track last placed node
    event_log = EventLog()

    # HUD layout
    panel_x = 780
    new_game_rect = pygame.Rect(panel_x, 200, 170, 36)
    diff_rect = pygame.Rect(panel_x, 244, 170, 36)

    def check_new_recipes(player, before_counts):
        """Check what recipes were completed by the last move."""
        after_counts = count_recipes(graph, player)
        new_recipes = []
        for rtype in after_counts:
            diff = after_counts[rtype] - before_counts.get(rtype, 0)
            if diff > 0:
                pts = RECIPE_POINTS.get(rtype, 1)
                for _ in range(diff):
                    new_recipes.append((rtype, pts))
        return new_recipes

    def reset():
        nonlocal graph, current_player, game_over, message, last_move
        graph = make_chromatic()
        current_player = "X"
        game_over = False
        message = "Your turn (X)"
        last_move = None
        event_log.clear()

    while True:
        mx, my = pygame.mouse.get_pos()
        hover_node = node_at_pos(graph, mx, my) if not game_over else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_game_rect.collidepoint(mx, my):
                    reset()
                    continue
                if diff_rect.collidepoint(mx, my):
                    difficulty_idx = (difficulty_idx + 1) % len(DIFFICULTIES)
                    continue

                if not game_over and current_player == "X":
                    clicked = node_at_pos(graph, mx, my)
                    if clicked and graph.nodes[clicked]["owner"] is None:
                        before = count_recipes(graph, "X")
                        graph.claim_node(clicked, "X")
                        last_move = clicked

                        # Log new recipes
                        new = check_new_recipes("X", before)
                        for rtype, pts in new:
                            color = RECIPE_COLORS.get(rtype, (200, 200, 200))
                            event_log.add(f"You completed {rtype}! +{pts}pt", color)

                        if graph.is_full():
                            x_score = compute_score(graph, "X")
                            o_score = compute_score(graph, "O")
                            if x_score > o_score:
                                message = f"You win! {format_score(x_score)}-{format_score(o_score)}"
                            elif o_score > x_score:
                                message = f"AI wins! {format_score(o_score)}-{format_score(x_score)}"
                            else:
                                message = f"Draw! {format_score(x_score)}-{format_score(o_score)}"
                            game_over = True
                        else:
                            current_player = "O"
                            message = "AI thinking..."

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset()

        # AI turn
        if not game_over and current_player == "O":
            diff = DIFFICULTIES[difficulty_idx]
            before = count_recipes(graph, "O")
            move = best_move(graph, "O", difficulty=diff, evaluate=evaluate_chromatic)
            if move:
                graph.claim_node(move, "O")
                last_move = move

                # Log AI's new recipes
                new = check_new_recipes("O", before)
                for rtype, pts in new:
                    color = RECIPE_COLORS.get(rtype, (200, 200, 200))
                    event_log.add(f"AI completed {rtype}! +{pts}pt", color)

                if graph.is_full():
                    x_score = compute_score(graph, "X")
                    o_score = compute_score(graph, "O")
                    if x_score > o_score:
                        message = f"You win! {format_score(x_score)}-{format_score(o_score)}"
                    elif o_score > x_score:
                        message = f"AI wins! {format_score(o_score)}-{format_score(x_score)}"
                    else:
                        message = f"Draw! {format_score(x_score)}-{format_score(o_score)}"
                    game_over = True
                else:
                    current_player = "X"
                    message = "Your turn (X)"

        # ── draw ────────────────────────────────────────────────────────
        screen.fill(BG)

        # ── Draw recipe triangles ──
        # Layer 1: inactive recipes (very faint, only outline)
        for edge in graph.hyperedges:
            p_count, o_count, free = edge_status(graph, edge, "X")
            total = len(edge["nodes"])
            if p_count == 0 and o_count == 0:
                # Completely unclaimed — very subtle outline only
                draw_triangle(screen, graph, edge, alpha=8, outline_width=1)

        # Layer 2: partially claimed (one player has progress)
        for edge in graph.hyperedges:
            p_count, o_count, free = edge_status(graph, edge, "X")
            total = len(edge["nodes"])
            mixed = (p_count > 0 and o_count > 0)  # contested
            if mixed:
                # Contested — dim, no fill
                draw_triangle(screen, graph, edge, alpha=5, outline_width=1)
            elif p_count == 1 and o_count == 0:
                # Player has started building — light fill
                draw_triangle(screen, graph, edge, alpha=15, outline_width=2)
            elif o_count == 1 and p_count == 0:
                draw_triangle(screen, graph, edge, alpha=12, outline_width=1)

        # Layer 3: one-away recipes (prominent)
        for edge in graph.hyperedges:
            p_count, o_count, free = edge_status(graph, edge, "X")
            total = len(edge["nodes"])
            if p_count == total - 1 and free == 1:
                # Player one away — bright!
                draw_triangle(screen, graph, edge, alpha=40, outline_width=3)
            elif o_count == total - 1 and free == 1:
                # AI one away — warning
                draw_triangle(screen, graph, edge, alpha=30, outline_width=2)

        # Layer 4: completed recipes (pulsing)
        for edge in graph.hyperedges:
            p_count, o_count, free = edge_status(graph, edge, "X")
            total = len(edge["nodes"])
            if p_count == total:
                cancelled = is_cancelled(graph, edge, "X")
                draw_triangle(screen, graph, edge, pulse=True,
                              cancelled=cancelled, owner="X")
            elif o_count == total:
                cancelled = is_cancelled(graph, edge, "O")
                draw_triangle(screen, graph, edge, pulse=True,
                              cancelled=cancelled, owner="O")

        # Layer 5: hover highlight — show all recipes containing hovered node
        if hover_node and graph.nodes[hover_node]["owner"] is None:
            for edge in graph.hyperedges:
                if hover_node in edge["nodes"]:
                    p_count, o_count, free = edge_status(graph, edge, "X")
                    # Highlight viable recipes (not fully blocked)
                    if o_count < len(edge["nodes"]):
                        draw_triangle(screen, graph, edge, alpha=50, outline_width=3)

        # Draw nodes
        for nid, data in graph.nodes.items():
            draw_node(screen, nid, data, font, is_last_move=(nid == last_move))

        # Hover glow
        if hover_node and graph.nodes[hover_node]["owner"] is None:
            hx = int(graph.nodes[hover_node]["x"])
            hy = int(graph.nodes[hover_node]["y"])
            hover_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(hover_surf, (255, 255, 255, 50), (hx, hy), NODE_RADIUS + 6)
            screen.blit(hover_surf, (0, 0))

        # ── HUD ─────────────────────────────────────────────────────────
        # Title
        title = title_font.render("HYPERSTRATE", True, (200, 200, 200))
        screen.blit(title, (panel_x, 30))
        sub = small_font.render("Chromatic v0.2", True, (140, 140, 140))
        screen.blit(sub, (panel_x, 55))

        # Scores
        x_score = compute_score(graph, "X")
        o_score = compute_score(graph, "O")

        score_y = 85
        you_txt = score_font.render(f"You: {format_score(x_score)}", True, X_COLOR)
        screen.blit(you_txt, (panel_x, score_y))
        ai_txt = score_font.render(f" AI: {format_score(o_score)}", True, O_COLOR)
        screen.blit(ai_txt, (panel_x, score_y + 30))

        # Score breakdown
        breakdown_y = score_y + 66
        for player, label, color in [("X", "You", X_COLOR), ("O", "AI", O_COLOR)]:
            counts = count_recipes(graph, player)
            parts = []
            for rtype, rcolor_name in [("purple", "P"), ("yellow", "Y"), ("cyan", "C"), ("white", "W")]:
                c = counts[rtype]
                if c > 0:
                    parts.append(f"{rcolor_name}:{c}")
            if parts:
                detail = small_font.render(f"  {label}: {' '.join(parts)}", True, (120, 120, 130))
                screen.blit(detail, (panel_x, breakdown_y))
                breakdown_y += 18

        # Status message
        if "win" in message.lower():
            msg_color = (100, 255, 100) if "You" in message else (255, 100, 100)
        elif "Draw" in message:
            msg_color = (255, 255, 100)
        else:
            msg_color = (200, 200, 200)
        msg_surf = font.render(message, True, msg_color)
        screen.blit(msg_surf, (panel_x, 165))

        # Buttons
        new_game_rect.y = 200
        diff_rect.y = 242
        btn_color = (60, 70, 90) if not new_game_rect.collidepoint(mx, my) else (80, 90, 120)
        pygame.draw.rect(screen, btn_color, new_game_rect, border_radius=6)
        pygame.draw.rect(screen, (140, 140, 140), new_game_rect, 2, border_radius=6)
        btn_txt = small_font.render("New Game (R)", True, (220, 220, 220))
        screen.blit(btn_txt, (new_game_rect.x + 28, new_game_rect.y + 10))

        btn_color2 = (60, 70, 90) if not diff_rect.collidepoint(mx, my) else (80, 90, 120)
        pygame.draw.rect(screen, btn_color2, diff_rect, border_radius=6)
        pygame.draw.rect(screen, (140, 140, 140), diff_rect, 2, border_radius=6)
        diff_label = DIFFICULTIES[difficulty_idx].capitalize()
        diff_txt = small_font.render(f"AI: {diff_label}", True, (220, 220, 220))
        screen.blit(diff_txt, (diff_rect.x + 44, diff_rect.y + 10))

        # Recipe legend
        legend_y = 295
        legend_title = small_font.render("Recipes (3-node triangles):", True, (160, 160, 160))
        screen.blit(legend_title, (panel_x, legend_y))
        recipes_legend = [
            (WHITE_MIX, "White (R+G+B)", "3pt"),
            (PURPLE, "Purple (R+B mix)", "1pt"),
            (YELLOW, "Yellow (R+G mix)", "1pt"),
            (CYAN,   "Cyan   (B+G mix)", "1pt"),
        ]
        for i, (color, name, pts) in enumerate(recipes_legend):
            ly = legend_y + 20 + i * 20
            # Small triangle icon
            pygame.draw.polygon(screen, color,
                                [(panel_x + 6, ly + 14), (panel_x, ly + 2), (panel_x + 12, ly + 2)])
            txt = small_font.render(f" {name} {pts}", True, (140, 140, 140))
            screen.blit(txt, (panel_x + 16, ly))

        # RPS cycle
        rps_y = legend_y + 20 + len(recipes_legend) * 20 + 8
        rps_title = small_font.render("Cancels (RPS):", True, (160, 160, 160))
        screen.blit(rps_title, (panel_x, rps_y))
        rps_items = [
            (PURPLE, "P", YELLOW, "Y"),
            (YELLOW, "Y", CYAN, "C"),
            (CYAN, "C", PURPLE, "P"),
        ]
        for i, (c1, n1, c2, n2) in enumerate(rps_items):
            ry = rps_y + 18 + i * 16
            pygame.draw.rect(screen, c1, (panel_x + 4, ry + 2, 10, 10))
            txt = small_font.render(f" {n1} beats {n2} ", True, (130, 130, 130))
            screen.blit(txt, (panel_x + 16, ry))
            pygame.draw.rect(screen, c2, (panel_x + 16 + txt.get_width(), ry + 2, 10, 10))

        # Visual guide
        guide_y = rps_y + 18 + len(rps_items) * 16 + 12
        guide_title = small_font.render("Visual guide:", True, (120, 120, 130))
        screen.blit(guide_title, (panel_x, guide_y))
        guides = [
            ((255, 255, 255), "Pulsing △ = completed"),
            ((180, 180, 180), "Bright △ = 1 away"),
            ((120, 120, 120), "Faint △ = in progress"),
            ((100, 180, 100), "Hover = your options"),
        ]
        for i, (c, desc) in enumerate(guides):
            gy = guide_y + 18 + i * 16
            txt = small_font.render(f"• {desc}", True, c)
            screen.blit(txt, (panel_x, gy))

        # Event log
        log_y = guide_y + 18 + len(guides) * 16 + 16
        log_title = small_font.render("Recent:", True, (100, 100, 110))
        screen.blit(log_title, (panel_x, log_y))
        event_log.draw(screen, event_font, panel_x, log_y + 18)

        # Stats
        claimed = sum(1 for n in graph.nodes.values() if n["owner"] is not None)
        total_nodes = len(graph.nodes)
        stats_txt = small_font.render(f"Turn {claimed}/{total_nodes}", True, (70, 70, 80))
        screen.blit(stats_txt, (panel_x, HEIGHT - 28))

        # Footer
        footer = small_font.render("Click nodes · R restart · Hover to preview", True, (60, 60, 70))
        screen.blit(footer, (20, HEIGHT - 24))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
