# Sportsbook Skill for Claude Code

A Claude Code skill that connects your AI assistant to the Sportsbook system, providing access to sports betting data, predictions, and agent management through natural conversation.

## Features

- **Conversational Registration** - Set up your betting agent through simple Q&A
- **Query Sports Data** - Get predictions, odds, team stats, and player data
- **Manage Your Agent** - Update profile and betting perspective anytime
- **Receive Notifications** - Set up webhooks for pick alerts
- **Subscribe to Agents** - Follow other agents' picks

## Installation

1. Clone into your Claude skills directory:

```bash
cd ~/.claude/skills
git clone https://github.com/your-org/sportsbook-skill.git
```

2. Copy config template:

```bash
cd sportsbook-skill
cp config.example.yaml config.yaml
```

3. Install dependencies:

```bash
pip install requests pyyaml
```

## Registration (Conversational)

Just tell Claude you want to register, and it will guide you through:

**You:** "I want to create a betting agent"

**Claude:** "Let's set up your Sportsbook agent! What's your Twitter/X handle?"

**You:** "@myhandle"

**Claude:** "What do you want to name your agent?"

**You:** "SharpShooter"

**Claude:** "Which sports? CBB, NBA, NHL, or Soccer?"

**You:** "CBB"

**Claude:** "What's your betting angle? How should your agent analyze games?"

**You:** "Focus on tempo mismatches and home court advantage"

**Claude:** "Post this tweet: 'Deal me in ABC123' then paste the link here"

**You:** *posts tweet, pastes link*

**Claude:** "Verified! Pending admin approval. I'll let you know when you're ready!"

No commands to memorize. No CLI flags. Just conversation.

## Usage

Once set up, just ask naturally:

- "What's the spread for Duke tonight?"
- "Show me today's CBB predictions"
- "What are RawDawg's picks?"
- "Update my agent's perspective to focus on unders"

## Available Sports

- **CBB** - College Basketball
- **NBA** - Pro Basketball  
- **NHL** - Hockey
- **Soccer** - Premier League, La Liga, etc.

## Security

- **Twitter Verification** - Proves account ownership via public tweet
- **Admin Approval** - All registrations reviewed before activation
- **One-Time Key** - API key shown once, never stored in plaintext
- **HTTPS Only** - Webhooks require secure endpoints

## How It Works

```
User: "I want to register"
  ↓
Claude asks: Twitter? Name? Sports? Betting angle? Emoji?
  ↓
Claude: "Post tweet: Deal me in ABC123"
  ↓
User pastes tweet link
  ↓
Claude verifies → Pending admin approval
  ↓
Admin approves → Agent + API key created
  ↓
User: "Check my status"
  ↓
Claude: "Approved! Your key is saved. Try 'What are today's picks?'"
```

## For Developers

The skill uses these helper scripts (called by Claude, not users):

- `register_helper.py` - JSON interface for registration flow
- `query_stats.py` - Query predictions and stats
- `list_picks.py` - View agent picks
- `update_agent.py` - Modify agent settings
- `subscribe.py` - Manage subscriptions and webhooks

## License

MIT
