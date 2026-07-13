#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json

with open('suppliers_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('='*60)
print('Database Verification Report')
print('='*60)
print(f'Total suppliers: {len(db["suppliers"])}')
print()

# Count by status
status_count = {}
for s in db['suppliers']:
    status = s['status']
    status_count[status] = status_count.get(status, 0) + 1

print('Status distribution:')
for status, count in status_count.items():
    print(f'  {status}: {count}')
print()

# Show suppliers with history
print('Suppliers with chat history:')
print()
count = 0
for s in db['suppliers']:
    if s['history']:
        count += 1
        print(f'[{s["id"]}] {s["name"]}')
        print(f'  Status: {s["status"]}')
        for h in s['history']:
            direction = 'SENT' if h['direction'] == 'out' else 'RECEIVED'
            msg = h['message'][:50] if len(h['message']) > 50 else h['message']
            print(f'  [{direction}] {msg}')
        print()

print(f'Total with history: {count}')
print('='*60)
