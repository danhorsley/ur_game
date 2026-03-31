"""Game-agnostic hypergraph engine for Hyperstrate.

A HyperGraph is a set of nodes and hyperedges. Each node has an owner
(None, or a player identifier). Each hyperedge is a frozenset of node ids.
A player wins by owning every node in at least one hyperedge.
"""


class HyperGraph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}       # id -> {label, owner, x, y, ...}
        self.hyperedges: list[dict] = []        # [{nodes: frozenset, color, label, ...}]

    def add_node(self, node_id: str, **attrs):
        self.nodes[node_id] = {"owner": None, **attrs}

    def add_hyperedge(self, node_ids, **attrs):
        self.hyperedges.append({"nodes": frozenset(node_ids), **attrs})

    def claim_node(self, node_id: str, player: str):
        self.nodes[node_id]["owner"] = player

    def unclaim_node(self, node_id: str):
        self.nodes[node_id]["owner"] = None

    def available_nodes(self) -> list[str]:
        return [nid for nid, data in self.nodes.items() if data["owner"] is None]

    def check_winner(self):
        """Return the player who owns all nodes in any hyperedge, or None."""
        for edge in self.hyperedges:
            owners = {self.nodes[nid]["owner"] for nid in edge["nodes"]}
            if len(owners) == 1 and None not in owners:
                return owners.pop()
        return None

    def winning_edges(self, player: str) -> list[dict]:
        """Return all hyperedges fully owned by player."""
        result = []
        for edge in self.hyperedges:
            if all(self.nodes[nid]["owner"] == player for nid in edge["nodes"]):
                result.append(edge)
        return result

    def is_full(self) -> bool:
        return len(self.available_nodes()) == 0

    def copy(self):
        """Shallow copy suitable for search — copies node ownership, shares edge refs."""
        g = HyperGraph()
        g.nodes = {nid: dict(data) for nid, data in self.nodes.items()}
        g.hyperedges = self.hyperedges  # edges are immutable during play
        return g
