# minecode/ranker.py
import math
import re
import networkx as nx


def collapse_version(name):
    """Remove version pins. 'requests==2.28.0' → 'requests'"""
    return re.split(r'[=><!\[]', name)[0].strip().lower()


def build_graph(edges):
    """Build version-collapsed directed graph from (from, to) edge list."""
    G = nx.DiGraph()
    for src, dst in edges:
        G.add_edge(collapse_version(src), collapse_version(dst))
    return G


def compute_pagerank(G):
    """Base popularity via PageRank on dependency graph."""
    return nx.pagerank(G, alpha=0.85)


def apply_decay(scores, freshness_days, lambda_=0.05):
    """
    Temporal decay: packages not updated recently score lower.
    Formula: score × e^(−λ × days_since_release)
    """
    decayed = {}
    for pkg, score in scores.items():
        days = freshness_days.get(pkg, 365)  # default: assume stale
        decayed[pkg] = score * math.exp(-lambda_ * days)
    return decayed


def apply_transitive_discount(G, scores, discount=0.85):
    """
    Packages that are direct dependencies rank higher than
    packages 2-3 hops away. Penalise by hop count.
    """
    adjusted = {}
    for node in G.nodes():
        total = 0
        for target in G.nodes():
            try:
                hops = nx.shortest_path_length(G, node, target)
                total += scores.get(target, 0) * (discount ** hops)
            except nx.NetworkXNoPath:
                continue
        adjusted[node] = total
    return adjusted


def filter_bot_downloads(downloads):
    """
    Filter CI/mirror bot traffic before computing download velocity.
    downloads: list of (package_name, count, source_type)
    source_type: 'human' | 'fixed_interval' | 'mirror'
    """
    return [
        (pkg, count)
        for pkg, count, source in downloads
        if source == 'human'
    ]


def detect_cycles(G):
    """Find strongly connected components (circular deps)."""
    sccs = list(nx.strongly_connected_components(G))
    cycles = [s for s in sccs if len(s) > 1]
    return cycles


def run_ranking(edges, freshness_days=None, downloads=None):
    """
    Full pipeline. Returns ranked list of (package, score).
    
    edges: list of (from_package, to_package) strings
    freshness_days: dict of {package_name: days_since_last_release}
    downloads: list of (package, count, source_type)
    """
    if freshness_days is None:
        freshness_days = {}

    G = build_graph(edges)
    scores = compute_pagerank(G)
    scores = apply_decay(scores, freshness_days)
    scores = apply_transitive_discount(G, scores)

    cycles = detect_cycles(G)
    if cycles:
        print(f"[ranker] Warning: {len(cycles)} circular dependency clusters found")

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked