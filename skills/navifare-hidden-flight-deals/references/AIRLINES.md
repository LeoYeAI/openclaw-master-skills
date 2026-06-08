# IATA Airline Codes Reference

Quick reference for common airline codes used in flight searches.

## Major Full-Service Airlines

### North America
- **AA** - American Airlines
- **DL** - Delta Air Lines
- **UA** - United Airlines
- **AC** - Air Canada
- **AS** - Alaska Airlines
- **WS** - WestJet

### Europe - Major Carriers
- **BA** - British Airways
- **AF** - Air France
- **LH** - Lufthansa
- **KL** - KLM Royal Dutch Airlines
- **AZ** - ITA Airways (formerly Alitalia)
- **LX** - Swiss International Air Lines
- **OS** - Austrian Airlines
- **LO** - LOT Polish Airlines
- **SN** - Brussels Airlines
- **IB** - Iberia
- **TP** - TAP Portugal
- **SK** - Scandinavian Airlines (SAS)
- **AY** - Finnair
- **EI** - Aer Lingus

### Middle East
- **EK** - Emirates
- **QR** - Qatar Airways
- **EY** - Etihad Airways
- **TK** - Turkish Airlines
- **MS** - EgyptAir
- **SV** - Saudia

### Asia-Pacific
- **SQ** - Singapore Airlines
- **CX** - Cathay Pacific
- **NH** - All Nippon Airways (ANA)
- **JL** - Japan Airlines (JAL)
- **KE** - Korean Air
- **OZ** - Asiana Airlines
- **TG** - Thai Airways
- **MH** - Malaysia Airlines
- **GA** - Garuda Indonesia
- **QF** - Qantas
- **NZ** - Air New Zealand
- **AI** - Air India
- **9W** - Jet Airways

### Latin America
- **LA** - LATAM Airlines
- **AM** - Aeroméxico
- **CM** - Copa Airlines
- **AV** - Avianca

### China
- **CA** - Air China
- **CZ** - China Southern Airlines
- **MU** - China Eastern Airlines
- **HU** - Hainan Airlines
- **3U** - Sichuan Airlines

## Low-Cost Carriers

### Europe
- **FR** - Ryanair
- **U2** - easyJet
- **W6** - Wizz Air
- **VY** - Vueling
- **PC** - Pegasus Airlines
- **LS** - Jet2.com
- **TO** - Transavia
- **DY** - Norwegian Air Shuttle
- **BT** - airBaltic

### North America
- **WN** - Southwest Airlines
- **B6** - JetBlue Airways
- **NK** - Spirit Airlines
- **F9** - Frontier Airlines
- **G4** - Allegiant Air

### Asia-Pacific
- **3K** - Jetstar Asia
- **FD** - Thai AirAsia
- **AK** - AirAsia
- **5J** - Cebu Pacific
- **TR** - Scoot
- **VJ** - VietJet Air
- **IX** - Air India Express
- **SG** - SpiceJet
- **6E** - IndiGo

### Middle East & Africa
- **FZ** - flydubai
- **XY** - flynas
- **G9** - Air Arabia
- **XQ** - SunExpress
- **WY** - Oman Air
- **FP** - Mango (South Africa)

## Alliance Members

### Star Alliance
Members include: UA, LH, AC, NH, SQ, TK, LO, SK, AY, OS, LX, SN, TP, AI, CA, OZ, TG, EY

### SkyTeam
Members include: AF, KL, DL, AZ, KE, CZ, MU, SV, AM, GA, VN

### oneworld
Members include: AA, BA, IB, AY, QR, JL, QF, CX, LA, AS, WY

## Regional European Airlines

### Germany
- **DE** - Condor
- **4U** - Germanwings (now Eurowings)
- **EW** - Eurowings

### UK & Ireland
- **BE** - Flybe (defunct)
- **LS** - Jet2.com
- **FR** - Ryanair
- **EI** - Aer Lingus

### Scandinavia
- **D8** - Norwegian Air International
- **DY** - Norwegian
- **BT** - airBaltic
- **AY** - Finnair
- **RC** - Atlantic Airways

### Eastern Europe
- **W6** - Wizz Air
- **FR** - Ryanair (operates throughout)
- **RO** - Tarom (Romania)
- **OK** - Czech Airlines

### Southern Europe
- **VY** - Vueling
- **UX** - Air Europa
- **NT** - Binter Canarias
- **AZ** - ITA Airways
- **AP** - AlbaStar
- **EN** - Air Dolomiti

## Flight Number Format Examples

Flight numbers consist of:
- **2-letter airline code** + **1-4 digit number**

Examples:
- BA553 → British Airways flight 553
- LH400 → Lufthansa flight 400
- FR1234 → Ryanair flight 1234
- U2 3811 → easyJet flight 3811 (note space)

### Extraction Rule
When extracting flight numbers for Navifare:
- **Extract ONLY the numeric part**
- BA553 → "553"
- LH400 → "400"
- U2 3811 → "3811"
- FR1234 → "1234"

The airline name/code is stored separately in the `airline` field.

## How to Identify Airlines

### From Flight Numbers
- **Two letters at start**: BA553, LH400, AF123
- **One letter + number**: U23811 (easyJet), W63456 (Wizz Air)
- **Single letter codes are rare**: Y (MyWay Airlines), I (IBC Airways)

### From Logos/Branding
- Look for airline logos on screenshots
- Check aircraft livery colors
- Look for "operated by" text (codeshares)

### From Context
If user mentions:
- "Lufthansa flight" → LH
- "British Airways" → BA
- "Ryanair" → FR
- "easyJet" → U2

## Codeshares & Partners

### What are codeshares?
One flight operated by airline A but sold with airline B's code.

Example:
- Flight operated by: LH (Lufthansa)
- Also sold as: UA8888 (United), AC9999 (Air Canada)

### How to handle
Always extract the **operating carrier** (actual airline flying the plane):
- Look for "operated by" text
- The operating carrier matters for Navifare searches
- Codeshare numbers may not work in searches

### Common Codeshare Patterns
- **Star Alliance**: UA, LH, AC flights often codeshare
- **SkyTeam**: AF, KL, DL flights often codeshare
- **oneworld**: AA, BA, IB flights often codeshare

## Regional Carriers & Subsidiaries

Many major airlines have regional subsidiaries:

### Lufthansa Group
- **LH** - Lufthansa
- **LX** - Swiss
- **OS** - Austrian
- **SN** - Brussels Airlines
- **EW** - Eurowings

### Air France-KLM
- **AF** - Air France
- **KL** - KLM
- **TO** - Transavia

### IAG (International Airlines Group)
- **BA** - British Airways
- **IB** - Iberia
- **VY** - Vueling
- **EI** - Aer Lingus

### Ryanair Holdings
- **FR** - Ryanair
- **MT** - Malta Air
- **RK** - Ryanair UK

## Handling Unknown Airlines

If you encounter an airline code not in this list:

1. **Ask the user**: "I don't recognize airline code XX. What airline is this?"
2. **Look for full name**: User might have mentioned "Delta" but code is DL
3. **Check for typos**: Common: BA vs BU, UA vs AA, LH vs LX
4. **Context from route**: Some airlines only fly certain routes

## Common User References

Users often use informal names:

### Informal → Official
- "British" → BA (British Airways)
- "Lufthansa" → LH (Lufthansa)
- "Air France" → AF (Air France)
- "KLM" → KL (KLM)
- "Ryanair" → FR (Ryanair)
- "easyJet" → U2 (easyJet)
- "Swiss" → LX (Swiss)
- "Austrian" → OS (Austrian)
- "ITA" or "Alitalia" → AZ (ITA Airways)
- "Emirates" → EK (Emirates)
- "Qatar" → QR (Qatar Airways)
- "Singapore" → SQ (Singapore Airlines)
- "ANA" → NH (All Nippon Airways)
- "JAL" → JL (Japan Airlines)

### Budget Carrier Nicknames
- "Ryanair" (never "Ryan Air") → FR
- "easyJet" (note capitalization) → U2
- "Wizz" or "Wizz Air" → W6

## Special Cases

### Multi-Airline Itineraries
Some flights have different airlines per segment:

Example:
- Segment 1: BA (British Airways) LHR→JFK
- Segment 2: AA (American) JFK→LAX

Extract each segment with its respective airline code.

### Cargo Airlines
Passenger searches should not include cargo-only airlines:
- FX (FedEx), 5X (UPS), QY (DHL), etc.

If user mentions cargo, clarify they want passenger flights.

### Defunct Airlines
Some codes refer to airlines no longer operating:
- **AZ** was Alitalia, now ITA Airways (still AZ code)
- **BE** was Flybe (defunct 2020)
- **9W** was Jet Airways (suspended 2019)

If searching historical flights, note airline may no longer exist.

---

**Note**: This list covers ~150 of the most commonly used airlines. The Navifare system recognizes 1000+ airline codes worldwide including regional carriers.
