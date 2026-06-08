# Navifare Flight Price Validator Skill

An AgentSkills-compliant skill that enables AI agents to validate and compare flight prices across multiple booking sites using the Navifare MCP. Compatible with any MCP-enabled client (Claude Code, OpenClawd, etc.).

## What This Skill Does

When users mention flight prices from any booking website (Skyscanner, Kayak, Google Flights, etc.), this skill automatically:
1. ✈️ Extracts flight details from text or screenshots
2. 🔍 Searches Navifare's network of booking sites
3. 💰 Compares prices to find the best deals
4. 🔗 Provides direct booking links to providers

## Installation

### Prerequisites

**Required**: Navifare MCP Server must be configured in your MCP client.

The Navifare MCP is available as a hosted service. Add the following to your MCP client configuration (e.g., `mcp.json`):

```json
{
  "mcpServers": {
    "navifare-mcp": {
      "url": "https://mcp.navifare.com/mcp"
    }
  }
}
```

**No local installation required!** The MCP server is hosted and always available.

### Install the Skill

Install the skill in your agent's skills directory. For example:
```
~/.claude/skills/navifare-flight-validator/
```

Directory structure:
```
navifare-flight-validator/
├── SKILL.md              # Main skill definition
├── README.md             # This file
├── references/
│   ├── AIRPORTS.md       # IATA airport codes reference
│   ├── AIRLINES.md       # IATA airline codes reference
│   └── EXAMPLES.md       # Real usage examples
└── scripts/              # (Reserved for future enhancements)
```

### Verify Installation

1. **Check MCP is running**:
   The following Navifare MCP tools should be available in your client:
   - `mcp__navifare-mcp__flight_pricecheck`
   - `mcp__navifare-mcp__format_flight_pricecheck_request`

2. **Verify skill is detected**:
   Your MCP client should automatically discover skills in the configured skills directory.

## Usage

### Example 1: Validate a Price from Skyscanner

**You**: I found a flight from New York to London on Skyscanner for $450. It's BA553 departing June 15 at 6 PM.

**Agent** (automatically activates skill):
- Extracts flight details
- Searches Navifare for better prices
- Presents comparison table with booking links

### Example 2: Upload a Screenshot

**You**: *[Upload screenshot from Kayak]*

**Agent**:
- Extracts visible flight details from the screenshot
- Validates prices across booking sites
- Shows savings opportunities

### Example 3: Before Booking

**You**: I'm about to book this flight. Should I?

**Agent**:
- Asks for flight details
- Runs price comparison
- Recommends best option

## When The Skill Activates

The skill automatically triggers when you:
- 💬 Mention finding a flight price: "I found this flight for $X"
- 📸 Upload a flight booking screenshot
- ❓ Ask "Is this a good price?"
- 🤔 Say "Should I book this?"
- 🔍 Ask "Can you find cheaper?"

## What Information is Needed

For accurate price comparison, the skill needs:

**Required**:
- ✈️ **Route**: Departure and arrival airports (e.g., "JFK to LHR")
- 📅 **Date**: Travel date (e.g., "June 15, 2025")
- 🛫 **Flight**: Airline and flight number (e.g., "BA553")
- ⏰ **Times**: Departure and arrival times (e.g., "6:00 PM - 6:30 AM")

**Optional but helpful**:
- 💺 **Class**: Economy, Business, First (defaults to Economy)
- 👥 **Passengers**: Number of adults/children (defaults to 1 adult)
- 💵 **Reference price**: What you saw on other sites
- 💱 **Currency**: USD, EUR, GBP, etc. (auto-detected from price)

If any information is missing, the agent will ask you for it!

## Features

### ✅ What This Skill Does
- Compares prices across 10+ booking sites
- Handles direct and connecting flights
- Supports round-trip searches (one-way NOT supported)
- Extracts flight info from screenshots (via the agent's vision capabilities)
- Validates IATA codes for airports and airlines
- Converts currencies
- Shows price trends and savings
- Provides direct booking links

### ❌ What This Skill Does NOT Do
- Book flights automatically (returns links only)
- Store your payment information
- Make purchasing decisions for you
- Guarantee prices won't change

## Reference Documentation

### AIRPORTS.md
Complete IATA airport codes including:
- 200+ major international airports
- Regional airports by continent
- Multi-airport cities (London, New York, Paris, etc.)
- Low-cost carrier hubs
- How to handle ambiguous airport references

### AIRLINES.md
Complete IATA airline codes including:
- 150+ major airlines worldwide
- Low-cost carriers
- Alliance memberships (Star Alliance, SkyTeam, oneworld)
- Regional carriers and subsidiaries
- Codeshare handling
- Flight number extraction rules

### EXAMPLES.md
Real conversation examples showing:
- Handling one-way requests (round-trip only limitation)
- Screenshot extraction workflows
- Multi-segment connection flights
- Round-trip validations
- Error handling scenarios
- Missing information recovery
- Edge cases (no results, price increases, etc.)

## Troubleshooting

### "Navifare MCP not available"

**Solution**: Verify your MCP client configuration:
1. Check that `navifare-mcp` is configured with `"url": "https://mcp.navifare.com/mcp"`
2. Restart your MCP client after changing configuration
3. Verify the Navifare MCP tools are available

### "No results found"

**Possible causes**:
1. Flight details are incorrect (wrong airline code, flight number)
2. The flight doesn't operate on the specified date
3. Airport codes are invalid

**Solution**: Double-check flight details and use reference docs to verify codes.

### "Search timeout"

**What happened**: Navifare searches take up to 90 seconds. Sometimes it times out.

**Solution**: The skill will show partial results if available. You can:
- Try searching again
- Use the partial results returned
- Verify flight details are correct

### "Invalid airport code"

**Solution**: Check `references/AIRPORTS.md` for the correct IATA code.

Common mistakes:
- LON vs LHR/LGW/STN (London has 6 airports!)
- NYC vs JFK/EWR/LGA (New York has 3 major)
- PAR vs CDG/ORY (Paris has 2 major)

## Advanced Usage

### For Multiple Passengers

**You**: Family of 4 traveling to Paris. Found €1,200 total on Kayak.

**Agent**: Extracts passenger count (4) and searches accordingly.

### For Business Class

**You**: Business class JFK to Tokyo, found $3,500 on United.

**Agent**: Searches business class fares specifically.

### For Complex Itineraries

**You**: LAX → Tokyo → Sydney, multi-city trip.

**Agent**: Handles multiple segments and connections.

## Performance

- **Typical search time**: 30-60 seconds
- **Maximum search time**: 90 seconds
- **Booking sites searched**: 10+ providers
- **Results returned**: Up to 20 options (shows top 5 by default)

## Privacy & Security

This skill processes **pre-booking itineraries only** — flight routes, dates, times, and prices that the user found on booking sites and wants to compare. It does **not** process booking confirmations, passenger names, passport details, payment information, or any other personally identifiable information (PII).

**What is sent to the Navifare MCP server:**
- Flight numbers, airlines, airports, dates, and times
- Travel class and passenger count (e.g., "2 adults")
- A reference price and currency for comparison

**What is NOT sent:**
- Passenger names or personal details
- Booking references or confirmation numbers
- Payment or credit card information
- Passport or identity documents

**Data handling:**
- Searches are not linked to user accounts or identities
- Booking happens directly on provider sites via their own links
- No tracking or affiliate redirects

For full details, see [navifare.com](https://navifare.com) and our [Terms of Service](https://navifare.com/terms).

## Contributing

To improve this skill:

1. **Add more airports**: Edit `references/AIRPORTS.md`
2. **Add more airlines**: Edit `references/AIRLINES.md`
3. **Add examples**: Edit `references/EXAMPLES.md`
4. **Enhance instructions**: Edit `SKILL.md`

## Support

For issues with:
- **The skill itself**: Check this README and reference docs
- **Navifare MCP**: See main Navifare repository
- **Your MCP client**: Refer to your client's documentation

## License

MIT License - See main Navifare project for details.

## Version History

- **v1.2.0** (2026-02-23): Privacy clarity and PII protection
  - Detailed privacy section explaining exactly what data is and is not sent
  - Screenshot instructions now explicitly exclude personal information
  - Added links to navifare.com and Terms of Service
- **v1.1.1** (2026-02-23): Consistency fixes
  - Fixed tool name inconsistencies across all docs (now consistently `flight_pricecheck` and `format_flight_pricecheck_request`)
  - Clarified round-trip only limitation across all files
  - Removed references to undeclared tools (extractFlightDetails, Gemini AI)
  - Made documentation client-agnostic (not tied to Claude Code)
  - Removed stale local installation references
- **v1.0.0** (2025-02-11): Initial release
  - Price comparison across booking sites
  - Screenshot extraction support
  - Complete IATA reference data
  - Comprehensive usage examples

---

**Happy travels! Save money with Navifare price comparison.**
