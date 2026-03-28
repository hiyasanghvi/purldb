from packagedb.models import Package, PackageRelation
from minecode.ranker import run_ranking

def run_popularity_pipeline():
    # Pull edges from DB
    edges = [(r.from_package.name, r.to_package.name) for r in PackageRelation.objects.all()]
    
    # Freshness (days since last release)
    freshness = {
        'numpy': 5, 'pandas': 30, 'scipy': 60,
        'matplotlib': 10, 'requests': 3,
        'django': 7, 'pillow': 20, 'urllib3': 14, 'certifi': 45,
    }
    
    # Run ranking
    ranked = run_ranking(edges, freshness)
    
    # Save to DB
    for pkg_name, score in ranked:
        Package.objects.filter(name=pkg_name).update(popularity_score=score)
        print(f"Saved {pkg_name}: {score:.4f}")