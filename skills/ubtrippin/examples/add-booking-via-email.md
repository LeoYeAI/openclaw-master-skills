# Adding a Booking via Email Forwarding

UBTRIPPIN processes booking confirmation emails automatically. As an agent, you can add bookings on behalf of your user by forwarding their confirmation email.

## Steps

1. User receives a booking confirmation (flight, hotel, train, etc.)
2. You (the agent) forward the email from the user's registered address to: **trips@ubtrippin.xyz**
3. UBTRIPPIN's AI parser extracts the details (~30 seconds)
4. The item appears in the matching trip (or a new trip is created)

## Important

- **Must forward from the user's registered sender address** — emails from unknown senders are rejected.
- The registered sender is the email address the user verified in UBTRIPPIN settings.
- PDF attachments (e.g. eTickets, rail PDFs) are included — don't strip attachments when forwarding.

## Supported Booking Types

- ✈️ Flights (any airline, any booking platform)
- 🏨 Hotels (Booking.com, Expedia, direct, etc.)
- 🚂 Trains (Eurostar, SNCF, Trainline, Thalys, Renfe, etc.)
- 🚗 Car rentals (Hertz, Avis, Europcar, etc.)
- ⛴️ Ferries
- 🎭 Activities and tours

## If the Email Contains a PDF

Forward it with the PDF attachment included. UBTRIPPIN can read PDF eTickets and boarding passes.

## Checking the Result

After forwarding, wait ~30 seconds and then call:
```
GET /api/v1/trips
```
The new item should appear in the most recently updated trip.
