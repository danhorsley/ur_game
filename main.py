import pygame
import sys
import random
import math
from collections import defaultdict

pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game #0 – Arithmetic Hypergraph Prototype")
font = pygame.font.SysFont("monospace", 24)
small_font = pygame.font.SysFont("monospace", 16)

class Node:
    def __init__(self, x, y, value, is_operator=False):
        self.x = x
        self.y = y
        self.value = value          # number or operator string e.g. "+", "×"
        self.is_operator = is_operator
        self.radius = 30
        self.color = (255, 100, 100) if is_operator else (100, 200, 255)
        self.connections = []       # list of (other_node, is_hyperedge)

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius, 3)
        txt = small_font.render(str(self.value), True, (255,255,255))
        screen.blit(txt, (self.x - txt.get_width()//2, self.y - txt.get_height()//2))

    def distance(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

class Hypergraph:
    def __init__(self):
        self.nodes = []
        self.target = random.randint(50, 200)

    def add_node(self, node):
        self.nodes.append(node)

    def evaluate(self):
        # Very simple recursive evaluator for demo (assumes tree-like with one root)
        # Real version will use topological sort + hyperedge support
        if not self.nodes:
            return 0
        # For prototype we treat the last-added operator as root and connect greedily
        # (full graph parser comes in v0.2)
        try:
            # Dummy evaluation: sum all numbers then apply operators in order added
            nums = [n.value for n in self.nodes if not n.is_operator]
            ops = [n.value for n in self.nodes if n.is_operator]
            if not nums:
                return 0
            result = nums[0]
            for i, op in enumerate(ops):
                if i + 1 >= len(nums):
                    break
                if op == "+":
                    result += nums[i+1]
                elif op == "×":
                    result *= nums[i+1]
                elif op == "-":
                    result -= nums[i+1]
            return result
        except:
            return 0

    def draw(self):
        for node in self.nodes:
            node.draw()
        # Draw connections
        for i, node in enumerate(self.nodes):
            for j, other in enumerate(self.nodes):
                if i < j and node.distance(other) < 200:  # simple proximity hyperedge
                    pygame.draw.line(screen, (150,150,150), (node.x, node.y), (other.x, other.y), 4)

# --------------------- Simple AI (re-uses evaluation) ---------------------
def ai_best_move(graph, offered_numbers, offered_ops, depth=2):
    best_score = float('inf')
    best_choice = None
    for num in offered_numbers:
        for op in offered_ops:
            # Simulate adding
            test_graph = Hypergraph()
            test_graph.nodes = [n for n in graph.nodes]  # shallow copy
            n_node = Node(400, 300, num)
            op_node = Node(500, 300, op, True)
            test_graph.add_node(n_node)
            test_graph.add_node(op_node)
            score = abs(test_graph.evaluate() - graph.target)
            if score < best_score:
                best_score = score
                best_choice = (num, op)
    return best_choice

# --------------------- Main Game Loop ---------------------
def main():
    clock = pygame.time.Clock()
    graph = Hypergraph()
    # Seed
    graph.add_node(Node(200, 300, 5))

    offered_numbers = [random.randint(1, 20) for _ in range(3)]
    offered_ops = ["+", "×", "-"]
    selected = None
    dragging = None
    mode = "player"  # "player" or "ai"

    while True:
        screen.fill((20, 20, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for node in graph.nodes:
                    if math.hypot(node.x - mx, node.y - my) < node.radius:
                        dragging = node
                        break
                # Click offered items
                for i, num in enumerate(offered_numbers):
                    if 800 < mx < 950 and 100 + i*60 < my < 140 + i*60:
                        selected = ("num", num)
                for i, op in enumerate(offered_ops):
                    if 1000 < mx < 1150 and 100 + i*60 < my < 140 + i*60:
                        selected = ("op", op)

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    dragging = None
                if selected and event.button == 1:
                    mx, my = event.pos
                    if selected[0] == "num":
                        new_node = Node(mx, my, selected[1])
                    else:
                        new_node = Node(mx, my, selected[1], True)
                    graph.add_node(new_node)
                    selected = None
                    # AI turn demo
                    if random.random() < 0.3:  # occasional AI move
                        num, op = ai_best_move(graph, offered_numbers, offered_ops, depth=2)
                        ai_node = Node(600 + random.randint(-50,50), 400 + random.randint(-50,50), num)
                        op_node = Node(700 + random.randint(-50,50), 400 + random.randint(-50,50), op, True)
                        graph.add_node(ai_node)
                        graph.add_node(op_node)

        # Draw graph
        graph.draw()

        # Live evaluation
        val = graph.evaluate()
        dist = abs(val - graph.target)
        txt = font.render(f"Current: {val}   Target: {graph.target}   Dist: {dist}", True, (255,255,100))
        screen.blit(txt, (20, 20))

        # Offered palette
        for i, num in enumerate(offered_numbers):
            pygame.draw.rect(screen, (100,200,255), (800, 100 + i*60, 150, 40))
            txt = small_font.render(str(num), True, (0,0,0))
            screen.blit(txt, (820, 110 + i*60))
        for i, op in enumerate(offered_ops):
            pygame.draw.rect(screen, (255,100,100), (1000, 100 + i*60, 150, 40))
            txt = small_font.render(op, True, (0,0,0))
            screen.blit(txt, (1050, 110 + i*60))

        # Instructions
        help_txt = small_font.render("Drag nodes • Click palette to add • Rearrange freely • Combos = strategy!", True, (180,180,180))
        screen.blit(help_txt, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()