"""Test script to verify all routes are registered"""
from app.main import app

print("=" * 60)
print("REGISTERED ROUTES:")
print("=" * 60)

for route in app.routes:
    if hasattr(route, 'path'):
        if 'mobility' in route.path:
            print(f"+ {route.path}")

mobility_impact_routes = [r.path for r in app.routes if hasattr(r, 'path') and 'mobility-impact' in r.path]
print("\n" + "=" * 60)
print(f"Total mobility-impact routes: {len(mobility_impact_routes)}")
print("=" * 60)

if mobility_impact_routes:
    print("\nMobility Impact Routes Found:")
    for route in mobility_impact_routes:
        print(f"  - {route}")
else:
    print("\n[ERROR] No mobility-impact routes found!")
    print("\nAll available routes:")
    all_paths = [r.path for r in app.routes if hasattr(r, 'path')]
    for path in sorted(all_paths):
        print(f"  - {path}")
