# SQL JOIN-Referenz

## JOIN-Typen

### INNER JOIN
Nur Datensätze die in BEIDEN Tabellen eine Übereinstimmung haben.
```sql
SELECT k.name, b.produkt, b.betrag
FROM kunden k
INNER JOIN bestellungen b ON k.id = b.kunden_id;
```

### LEFT JOIN
ALLE Datensätze aus der linken Tabelle + passende aus der rechten (NULL wenn keine).
```sql
-- Alle Kunden, auch ohne Bestellungen
SELECT k.name, b.produkt, b.betrag
FROM kunden k
LEFT JOIN bestellungen b ON k.id = b.kunden_id;
```

### RIGHT JOIN
ALLE Datensätze aus der rechten Tabelle + passende aus der linken.
```sql
SELECT k.name, b.produkt
FROM kunden k
RIGHT JOIN bestellungen b ON k.id = b.kunden_id;
```

## Häufige Patterns

### Aggregation mit GROUP BY + HAVING
```sql
-- Gesamtumsatz pro Kunde, nur > 500 EUR
SELECT k.name, SUM(b.betrag) AS gesamt
FROM kunden k
LEFT JOIN bestellungen b ON k.id = b.kunden_id
GROUP BY k.name
HAVING SUM(b.betrag) > 500
ORDER BY gesamt DESC;
```

### Normalisierungsformen (Kurzreferenz)
- **1NF**: Atomare Werte, keine Wiederholungsgruppen
- **2NF**: 1NF + keine partiellen Abhängigkeiten
- **3NF**: 2NF + keine transitiven Abhängigkeiten
