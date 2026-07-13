#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os

files = [f for f in os.listdir('.') if f.endswith('.json')]
for f in files:
    print(f'=== {f} ===')
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for i, item in enumerate(data[:3], 1):
                name = item.get('name', 'Unknown')[:40]
                price = item.get('price', 'Unknown')
                print(f'  {i}. {name}... ({price})')
    except Exception as e:
        print(f'  Error: {e}')
    print()
