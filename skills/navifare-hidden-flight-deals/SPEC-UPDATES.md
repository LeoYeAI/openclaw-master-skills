# Navifare MCP Specification Updates

Based on the official documentation at https://www.navifare.com/mcp

## 🔥 BREAKING CHANGE - MCP Compliance Fix (Feb 12, 2026)

**The Navifare MCP server response format has been updated to comply with the official MCP specification.**

### What Changed

**Before (Non-compliant)**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "message": "...",
    "searchResult": {...},
    "status": "success"
  }
}
```

**After (MCP-compliant)**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"message\":\"...\",\"searchResult\":{...}}"
      }
    ],
    "isError": false
  }
}
```

### Why This Matters

The old format caused issues with all Claude clients:
- ❌ Claude Code: Tool results not displayed
- ❌ Claude.ai: Generic "Error occurred" messages
- ❌ Claude Desktop: Tools keep running after completion

The new format follows the [MCP Tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) and works correctly with all clients.

### Migration Guide

If you're using the Navifare MCP client directly (not through Claude), update your parsing:

**Old code**:
```javascript
const { message, searchResult } = response.result;
```

**New code**:
```javascript
const data = JSON.parse(response.result.content[0].text);
const { message, searchResult } = data;
```

---

## ✅ Corrections Made to Skill

### 1. **Round-Trip Format** (CRITICAL FIX)
**Before (WRONG)**:
```json
{
  "legs": [
    {
      "segments": [
        /* outbound AND return all in one leg */
      ]
    }
  ]
}
```

**After (CORRECT)**:
```json
{
  "legs": [
    {
      "segments": [/* outbound only */]
    },
    {
      "segments": [/* return only */]
    }
  ]
}
```

### 2. **Location Parameter**
- **Format**: 2-letter ISO country code (e.g., "IT", "US", "GB")
- **Default**: "ZZ" if unknown
- **Pattern**: `^[A-Z]{2}$`

### 3. **Travel Class Enum**
Exact values required:
- `ECONOMY`
- `PREMIUM_ECONOMY`
- `BUSINESS`
- `FIRST`

### 4. **Tool Names Confirmed**
- ✅ `flight_pricecheck` - Main search tool
- ✅ `format_flight_pricecheck_request` - Natural language formatter

## 📋 Complete Tool Specifications

### Tool 1: `flight_pricecheck`

**Purpose**: Search multiple booking sources to find better prices for a specific flight

**Input Parameters**:
```typescript
{
  trip: {
    legs: Array<{
      segments: Array<{
        airline: string;           // 2-letter IATA code
        flightNumber: string;      // Numeric part only
        departureAirport: string;  // 3-letter IATA code
        arrivalAirport: string;    // 3-letter IATA code
        departureDate: string;     // YYYY-MM-DD
        departureTime: string;     // HH:MM (24-hour)
        arrivalTime: string;       // HH:MM (24-hour)
        plusDays: number;          // 0, 1, 2, etc.
      }>;
    }>;
    travelClass: "ECONOMY" | "PREMIUM_ECONOMY" | "BUSINESS" | "FIRST";
    adults: number;      // min: 1
    children: number;    // min: 0
    infantsInSeat: number;  // min: 0
    infantsOnLap: number;   // min: 0
  };
  source: string;        // e.g., "Kayak", "ChatGPT"
  price: string;         // e.g., "84.00", "500"
  currency: string;      // 3-letter ISO code, pattern: ^[A-Z]{3}$
  location?: string;     // 2-letter ISO code, pattern: ^[A-Z]{2}$, default: "ZZ"
}
```

**Output** (MCP-compliant format):
```typescript
{
  content: [
    {
      type: "text",
      text: string  // JSON string containing { message, searchResult }
    }
  ],
  isError: boolean
}
```

**Parsed content structure**:
```typescript
{
  message: string;        // Summary message
  searchResult: {
    status: string;       // Overall status
    request_id: string;
    totalResults: number;
    results: Array<...>
  }
}
```

### Tool 2: `format_flight_pricecheck_request`

**Purpose**: Parse natural language into structured format

**Input**:
```typescript
{
  user_request: string;  // Natural language flight details
}
```

**Output**:
```typescript
{
  message: string;
  needsMoreInfo: boolean;
  missingFields?: string[];           // If needsMoreInfo is true
  flightData?: object;                // If needsMoreInfo is false
  readyForPriceCheck: boolean;
}
```

## 🎯 Your Milan → Sydney Flight (Corrected Format)

**Saved as**: `milan-sydney-example.json`

```json
{
  "trip": {
    "legs": [
      {
        "segments": [
          {
            "airline": "QR",
            "flightNumber": "124",
            "departureAirport": "MXP",
            "arrivalAirport": "DOH",
            "departureDate": "2026-02-19",
            "departureTime": "08:55",
            "arrivalTime": "16:40",
            "plusDays": 0
          },
          {
            "airline": "QR",
            "flightNumber": "908",
            "departureAirport": "DOH",
            "arrivalAirport": "SYD",
            "departureDate": "2026-02-19",
            "departureTime": "20:40",
            "arrivalTime": "18:50",
            "plusDays": 1
          }
        ]
      },
      {
        "segments": [
          {
            "airline": "QR",
            "flightNumber": "909",
            "departureAirport": "SYD",
            "arrivalAirport": "DOH",
            "departureDate": "2026-03-01",
            "departureTime": "21:40",
            "arrivalTime": "04:30",
            "plusDays": 1
          },
          {
            "airline": "QR",
            "flightNumber": "127",
            "departureAirport": "DOH",
            "arrivalAirport": "MXP",
            "departureDate": "2026-03-02",
            "departureTime": "08:50",
            "arrivalTime": "13:10",
            "plusDays": 0
          }
        ]
      }
    ],
    "travelClass": "ECONOMY",
    "adults": 1,
    "children": 0,
    "infantsInSeat": 0,
    "infantsOnLap": 0
  },
  "source": "Kayak",
  "price": "500",
  "currency": "USD",
  "location": "IT"
}
```

## 📊 Key Insights

### Round-Trip Structure
- **Leg 1**: Outbound journey (MXP → DOH → SYD)
  - 2 segments with connection in Doha
- **Leg 2**: Return journey (SYD → DOH → MXP)
  - 2 segments with connection in Doha

### Flight Timing
- **Outbound total**: ~26 hours (departs Feb 19 08:55, arrives Feb 20 18:50)
- **Return total**: ~17 hours (departs Mar 1 21:40, arrives Mar 2 13:10)
- **Trip duration**: 11 nights in Australia

### Price Analysis
- **$500 USD** for Milan → Sydney round-trip on Qatar Airways
- This is **exceptionally low** - typical prices: $800-1500+
- Could be:
  - Promotional fare
  - Error fare
  - Missing taxes/fees
  - Special corporate/student rate

## 🔧 MCP Configuration

**Add to `~/.claude/mcp.json`**:
```json
{
  "mcpServers": {
    "navifare-mcp": {
      "url": "https://mcp.navifare.com/mcp"
    }
  }
}
```

**Then restart Claude Code completely.**

## ✅ What's Updated

### Files Modified:
1. ✅ **SKILL.md** - Corrected round-trip format, updated tool names
2. ✅ **README.md** - Updated with HTTP endpoint configuration
3. ✅ **INSTALLATION.md** - Updated setup instructions
4. ✅ **milan-sydney-example.json** - Your flight in correct format
5. ✅ **SPEC-UPDATES.md** - This documentation

### Changes Applied:
- ✅ Round trips now use 2 legs (not 1)
- ✅ Location parameter uses 2-letter country codes
- ✅ Tool names match official spec
- ✅ Travel class enum matches exactly
- ✅ All examples updated to correct format

## 🚀 Next Steps

1. **Configure MCP** in `~/.claude/mcp.json`
2. **Restart Claude Code**
3. **Test with**: "Search that Milan to Sydney flight again"
4. **Get results** showing best prices across 10+ booking sites

## 📚 Official Documentation

- **MCP Endpoint**: https://mcp.navifare.com/mcp
- **Documentation**: https://www.navifare.com/mcp
- **Version**: 0.1.5
- **Status**: Always available (hosted service)

---

**Updated**: 2026-02-11
**Spec Version**: 0.1.5
**Skill Version**: 1.0.1
