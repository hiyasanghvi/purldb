import networkx as nx
import math
import re

def collapse_version(name):
    return re.split(r'[=><!\[]', name)[0].strip()

def build_collapsed_graph(edges):
    G = nx.DiGraph()
    for src, dst in edges:
        G.add_edge(collapse_version(src), collapse_version(dst))
    return G
# ================================
# 🔹 STEP 1: Normalize (Version Collapse)
# ================================
def normalize(name):
    return name.split("==")[0].lower()


# ================================
# 🔹 STEP 2: Sample Dependency Data (with versions)
# ================================
edges = [
    ("pandas==2.0", "numpy==1.24"),
    ("scipy==1.10", "numpy==1.24"),
    ("matplotlib==3.7", "numpy==1.25"),
    ("seaborn==0.12", "matplotlib==3.7"),  # extra depth
]

# Apply normalization
edges = [(normalize(a), normalize(b)) for a, b in edges]


# ================================
# 🔹 STEP 3: Build Graph
# ================================
G = nx.DiGraph()
G.add_edges_from(edges)


# ================================
# 🔹 STEP 4: PageRank (Base Popularity)
# ================================
scores = nx.pagerank(G)

print("\n Base PageRank:\n")
for pkg, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{pkg}: {round(score, 4)}")


# ================================
# 🔹 STEP 5: Temporal Decay (Freshness)
# ================================
# Fake freshness data (days since last release)
freshness = {
    "numpy": 5,
    "pandas": 30,
    "scipy": 60,
    "matplotlib": 10,
    "seaborn": 20,
}

def decay(days, lambda_=0.05):
    return math.exp(-lambda_ * days)

# Apply decay
decayed_scores = {
    pkg: scores[pkg] * decay(freshness.get(pkg, 30))
    for pkg in scores
}

print("\n After Temporal Decay:\n")
for pkg, score in sorted(decayed_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{pkg}: {round(score, 4)}")


# ================================
# 🔹 STEP 6: Strongly Connected Components (SCC)
# ================================
scc = list(nx.strongly_connected_components(G))

print("\n Strongly Connected Components:\n")
for component in scc:
    print(component)


# ================================
# 🔹 STEP 7: Final Ranking
# ================================
print("\n Final Popularity Ranking:\n")

ranked = sorted(decayed_scores.items(), key=lambda x: x[1], reverse=True)

for i, (pkg, score) in enumerate(ranked, start=1):
    print(f"{i}. {pkg} → {round(score, 4)}")