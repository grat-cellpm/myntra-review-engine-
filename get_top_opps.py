import urllib.request
import json

response = urllib.request.urlopen('http://localhost:5000/api/opportunities')
data = json.loads(response.read().decode())

print("Top 10 Opportunity Areas:\n")
for d in data[:10]:
    print(f"- **{d['opportunity']}** ({d['mention_count']} mentions, {d['priority_level']} Priority)")
    print(f"  *Customer Problem:* {d['description']}")
    print(f"  *Wishlist to Purchase Impact:* {d['wishlist_to_purchase_impact'].replace('_', ' ').title()}")
    print()
