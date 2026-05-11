#!/usr/bin/env python3
import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
import sqlite3

CSV_PATH = Path('/home/openclaw/.openclaw/workspace/skills/paradiz/references/prices.csv')
DB_PATH = Path('/home/openclaw/.openclaw/workspace/skills/paradiz/data/db/testDB.sqlite')

# Маппинг названий из прайса в фактические категории новой БД
ROOM_DB_MAP = {
    'Домик Эконом': 'Домик',
    'Стандарт': 'Стандарт',
    'Двухкомнатный номер': 'Двухкомнатный Номер',
    'Номер с кухней': 'Номер с кухней Стандарт',
    'Номер Большой с кухней': 'Номер с кухней №33',
}


def mk_hash(*parts: str) -> str:
    return hashlib.md5('|'.join(parts).encode('utf-8')).hexdigest()


def load_csv(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def date_jd(cur, s: str):
    return cur.execute('SELECT julianday(?)', (s,)).fetchone()[0]


def ensure_category(cur, name: str, maxlivers: int):
    row = cur.execute('SELECT id FROM hotel_room_categories WHERE name=?', (name,)).fetchone()
    if row:
        return row[0]
    cid = mk_hash('paradiz-cat', name)
    now_jd = cur.execute('SELECT julianday("now")').fetchone()[0]
    h = mk_hash(cid, name)
    cur.execute(
        '''INSERT INTO hotel_room_categories
           (id,name,ename,color,maxlivers,channelCode,additionalChannelCode,additional,description,status,lastupdate,hash)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
        (cid, name, name, 0, maxlivers, '', '', '', 'imported from prices.csv', 0, now_jd, h)
    )
    return cid


def upsert_cost(cur, category_id: str, room_name: str, guests_num: int, cost: float, dfrom: str, dto: str):
    rid = mk_hash('paradiz-cost', room_name, dfrom, dto, str(guests_num))
    exists = cur.execute('SELECT 1 FROM hotel_room_categories_cost WHERE id=?', (rid,)).fetchone()
    df = date_jd(cur, dfrom)
    dt = date_jd(cur, dto)
    if exists:
        cur.execute('''UPDATE hotel_room_categories_cost
                       SET category=?, number=?, cost=?, date_from=?, date_to=?, subtype='', days=127
                       WHERE id=?''',
                    (category_id, guests_num, cost, df, dt, rid))
    else:
        cur.execute('''INSERT INTO hotel_room_categories_cost
                       (id, category, number, cost, date_from, date_to, subtype, days)
                       VALUES (?,?,?,?,?,?,?,?)''',
                    (rid, category_id, guests_num, cost, df, dt, '', 127))


def main():
    if not CSV_PATH.exists() or not DB_PATH.exists():
        raise SystemExit('prices.csv or testDB.sqlite not found')

    # backup db
    backup_dir = DB_PATH.parent / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = backup_dir / f'testDB-{stamp}.sqlite'
    shutil.copy2(DB_PATH, backup_path)

    rows = load_csv(CSV_PATH)

    # extra-person price by period
    extra_by_period = {}
    for r in rows:
        if (r.get('room') or '').strip().lower() == 'доп. человек':
            extra_by_period[(r['date_from'], r['date_to'])] = float(r['price_per_night'])

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    room_max = {
        'Домик Эконом': 4,
        'Стандарт': 4,
        'Двухкомнатный номер': 6,
        'Номер с кухней': 4,
        'Номер Большой с кухней': 6,
    }

    synced = 0
    used_categories = set()
    for r in rows:
        room = (r.get('room') or '').strip()
        if not room or room == 'Доп. человек':
            continue

        dfrom = r['date_from']
        dto = r['date_to']
        gmin = int(r['guests_min'])
        gmax = int(r['guests_max'])
        base = float(r['price_per_night'])
        extra = float(extra_by_period.get((dfrom, dto), 800.0))

        base_included = 4 if room in ('Двухкомнатный номер', 'Номер Большой с кухней') else 2
        maxl = room_max.get(room, gmax)

        db_room = ROOM_DB_MAP.get(room, room)
        cat_id = ensure_category(cur, db_room, maxl)
        used_categories.add(db_room)

        # очищаем старые/дублирующиеся тарифы в том же диапазоне дат и вместимости
        df = date_jd(cur, dfrom)
        dt = date_jd(cur, dto)
        cur.execute('''DELETE FROM hotel_room_categories_cost
                       WHERE category=? AND date_from=? AND date_to=? AND number BETWEEN ? AND ?''',
                    (cat_id, df, dt, gmin, gmax))

        for n in range(gmin, gmax + 1):
            extra_guests = max(0, n - base_included)
            cost = base + extra_guests * extra
            upsert_cost(cur, cat_id, db_room, n, cost, dfrom, dto)
            synced += 1

    conn.commit()
    conn.close()

    print(f'backup: {backup_path}')
    print(f'synced cost rows: {synced}')
    print('mapped categories:', ', '.join(sorted(used_categories)))


if __name__ == '__main__':
    main()
