from src.learning.history import ReviewHistoryStore

store = ReviewHistoryStore()

# Show all stored reviews
import sqlite3
conn = sqlite3.connect("history.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 5").fetchall()
print(f"Total stored reviews: {len(rows)}")
for r in rows:
    print(f"  [{r['severity']}] {r['file']} - {r['comment'][:60]}...")
conn.close()

# Show accepted examples (few-shot)
examples = store.get_few_shot_examples(3)
print(f"\nAccepted examples (used in prompts): {len(examples)}")