from src.auth.audit import AuditLogger

logger = AuditLogger()
rows = logger.recent(10)
print(f"Total audit entries: {len(rows)}")
print()
for entry in rows:
    print(f"[{entry['timestamp'][:19]}] {entry['action']} -> {entry['result']} ({entry['resource']})")
    if entry.get('details'):
        print(f"    details: {entry['details'][:100]}")