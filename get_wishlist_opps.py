import urllib.request
import json
from collections import Counter

response = urllib.request.urlopen('http://localhost:5000/api/opportunities')
data = json.loads(response.read().decode())

print("=== Wishlist Opportunity Areas ===\n")

# Group by wishlist intent
intent_groups = {}
for d in data:
    intent = d.get('wishlist_to_purchase_impact', 'Unknown')
    if intent not in intent_groups:
        intent_groups[intent] = []
    intent_groups[intent].append(d)

for intent, opps in intent_groups.items():
    print(f"## Intent: {intent.replace('_', ' ').title()} ({len(opps)} unique areas)")
    # Sort by mention count desc
    sorted_opps = sorted(opps, key=lambda x: x['mention_count'], reverse=True)
    for d in sorted_opps[:5]:
        print(f"- **{d['opportunity']}** ({d['mention_count']} mentions, {d['priority_level']} Priority)")
        print(f"  *Customer Problem:* {d['description']}")
    print()

