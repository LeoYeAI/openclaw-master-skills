# Navifare Flight Validator Skill - Installation & Validation

## ✅ Installation Complete!

The skill has been successfully created at:
```
~/.claude/skills/navifare-flight-validator/
```

## 📁 Directory Structure

```
navifare-flight-validator/
├── SKILL.md (573 lines)          # Main skill instructions
├── README.md                      # User guide
├── INSTALLATION.md                # This file
├── references/
│   ├── AIRPORTS.md (232 lines)   # IATA airport codes
│   ├── AIRLINES.md (299 lines)   # IATA airline codes
│   └── EXAMPLES.md (441 lines)   # Usage examples
└── scripts/                       # Reserved for future use
```

## 🔧 Configuration Required

### Step 1: Configure Navifare MCP HTTP Endpoint

The Navifare MCP server is available as a hosted service at `https://mcp.navifare.com/mcp`.

Add this to your MCP client configuration file (e.g., `mcp.json`):

```json
{
  "mcpServers": {
    "navifare-mcp": {
      "url": "https://mcp.navifare.com/mcp"
    }
  }
}
```

**Note**: This uses the HTTP transport to connect to the hosted Navifare MCP service. No local installation required!

### Step 2: Restart Your MCP Client

After adding/updating the MCP configuration:
1. Quit your MCP client completely
2. Relaunch the client
3. The Navifare MCP connection will be established automatically

### Step 3: Verify MCP Tools are Available

The following tools should be accessible in your MCP client:
- `mcp__navifare-mcp__flight_pricecheck` (main search tool)
- `mcp__navifare-mcp__format_flight_pricecheck_request` (formatting helper)

You can verify by checking the available MCP tools in your client.

## ✅ Validation Checklist

### Skill Structure Validation

- [x] **SKILL.md exists** with valid frontmatter
- [x] **Required fields present**: name, description
- [x] **Optional fields included**: license, compatibility, metadata, allowed-tools
- [x] **Name format correct**: lowercase, hyphens only, matches directory name
- [x] **Description under 1024 chars**: 262 characters ✓
- [x] **Body content present**: 573 lines of instructions
- [x] **Reference files created**: AIRPORTS.md, AIRLINES.md, EXAMPLES.md

### AgentSkills Compliance

According to [agentskills.io/specification](https://agentskills.io/specification):

✅ **Directory structure**: Correct
✅ **SKILL.md format**: Valid YAML frontmatter + Markdown body
✅ **Name constraints**: Meets all requirements (1-64 chars, lowercase, hyphens)
✅ **Description**: Clear, includes when to use, under 1024 chars
✅ **Progressive disclosure**:
  - Metadata: ~100 tokens
  - SKILL.md: ~4500 tokens
  - References: ~2500 tokens (loaded on-demand)
✅ **File references**: All relative paths, one level deep

### Content Validation

- [x] **Clear activation triggers**: 5 scenarios listed
- [x] **Step-by-step workflow**: 6 detailed steps
- [x] **Error handling**: 6 error scenarios covered
- [x] **Best practices**: 6 guidelines provided
- [x] **Data format examples**: 3 different flight types
- [x] **Reference documentation**: Complete IATA codes
- [x] **Real usage examples**: 8 realistic conversations

## 🧪 Testing the Skill

### Test 1: Simple Price Validation

**Input**:
> I found a flight from New York JFK to London Heathrow for $450. It's British Airways flight 178 departing June 15 at 8:00 PM. Is this a good price?

**Expected behavior**:
1. Skill activates automatically
2. Agent extracts flight details
3. Agent calls `mcp__navifare-mcp__format_flight_pricecheck_request` then `mcp__navifare-mcp__flight_pricecheck`
4. Agent presents comparison table with results

### Test 2: Screenshot Upload

**Input**:
> *[Upload a flight booking screenshot from Kayak/Skyscanner]*

**Expected behavior**:
1. Skill activates
2. Agent recognizes image contains flight info
3. Agent extracts flight details from the image using its vision capabilities
4. Agent calls the MCP tools to search and compare prices
5. Agent shows results table

### Test 3: Missing Information Handling

**Input**:
> I found a cheap flight to Paris. Should I book it?

**Expected behavior**:
1. Skill activates
2. Agent identifies missing information
3. Agent asks specific questions:
   - Departure city/airport?
   - Travel date?
   - Airline and flight number?
   - Departure time?
   - Reference price?

### Test 4: Unknown Airport Code

**Input**:
> Flight from LON to PAR for €200

**Expected behavior**:
1. Skill recognizes ambiguity
2. Agent asks which London airport (LHR/LGW/STN/LTN/LCY)
3. Agent asks which Paris airport (CDG/ORY)
4. Agent references AIRPORTS.md for clarification

## 🔍 Validation with skills-ref

To validate the skill structure using the official AgentSkills reference tool:

```bash
# Install skills-ref (if not already installed)
npm install -g @agentskills/skills-ref

# Validate the skill
skills-ref validate ~/.claude/skills/navifare-flight-validator

# Expected output:
# ✓ SKILL.md frontmatter is valid
# ✓ Name format is correct
# ✓ Description is valid
# ✓ All required fields present
# ✓ Directory structure is correct
```

**Note**: skills-ref may not be installed yet. If the command fails, the manual checks above are sufficient.

## 🐛 Troubleshooting

### Issue: Skill doesn't activate

**Check**:
1. SKILL.md is in correct location: `~/.claude/skills/navifare-flight-validator/SKILL.md`
2. Frontmatter is valid YAML (no syntax errors)
3. MCP client has restarted since skill was added

**Fix**: Restart your MCP client

### Issue: MCP tools not available

**Check**:
1. Your MCP configuration file exists and is valid JSON
2. The `navifare-mcp` entry has `"url": "https://mcp.navifare.com/mcp"`
3. Your MCP client has been restarted after config changes

**Fix**:
Verify your MCP configuration contains:
```json
{
  "mcpServers": {
    "navifare-mcp": {
      "url": "https://mcp.navifare.com/mcp"
    }
  }
}
```
Then restart your MCP client completely.

### Issue: Search returns no results

**Possible causes**:
1. Navifare API is down
2. Flight details are incorrect
3. The MCP endpoint is unreachable

**Fix**:
1. Check the MCP URL in your configuration
2. Verify flight details (airline codes, airport codes)
3. Check network connectivity

### Issue: Skill activates but search times out

**Expected behavior**: Navifare searches take up to 90 seconds

**What to do**:
- Wait for full 90 seconds
- Partial results may be shown
- Try again if timeout occurs

## 📊 Skill Metrics

- **Total lines**: 1,545 lines across all files
- **SKILL.md**: 573 lines (main instructions)
- **References**: 972 lines (IATA codes + examples)
- **Token estimate**:
  - Metadata: ~100 tokens (always loaded)
  - SKILL.md body: ~4,500 tokens (loaded when activated)
  - References: ~2,500 tokens (loaded on-demand)
- **Load time**: < 1 second (metadata), ~2 seconds (full skill)

## 🎯 Success Criteria

The skill is working correctly when:

✅ Agent recognizes flight price mentions and activates skill
✅ Agent extracts flight details from conversation
✅ Agent calls Navifare MCP flight_pricecheck tool
✅ Agent presents results in formatted table
✅ Agent provides clickable booking links
✅ Agent handles missing information gracefully
✅ Agent references AIRPORTS.md and AIRLINES.md as needed
✅ Agent follows examples from EXAMPLES.md

## 🚀 Next Steps

1. **Test with real queries**: Try the examples from Test 1-4 above
2. **Refine triggers**: If skill activates too often/rarely, adjust description
3. **Add more examples**: Update EXAMPLES.md with real usage patterns
4. **Enhance references**: Add more airports/airlines as needed
5. **Monitor performance**: Track search times and success rates

## 📚 Related Documentation

- **AgentSkills Specification**: https://agentskills.io/specification
- **Navifare API Docs**: (see main Navifare repo)

## ✉️ Support

- **Skill issues**: Check README.md and this file
- **MCP configuration**: See main Navifare MCP docs

---

**Installation Date**: 2025-02-11
**Skill Version**: 1.2.0
**Last Updated**: 2026-02-23
