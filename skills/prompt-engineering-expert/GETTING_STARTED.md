# How to Use This Prompt Engineering Expert Skill

## 📦 What You Have

A complete Claude Skill for prompt engineering expertise, located at:
```
~/Documents/prompt-engineering-expert/
```

## 🚀 How to Upload & Use

### Option 1: Upload via Claude.com (Easiest)

1. **Go to Claude.com** and start a conversation
2. **Click the "+" button** next to the message input
3. **Select "Upload a Skill"**
4. **Choose the skill folder**: `~/Documents/prompt-engineering-expert/`
5. **Claude will load the skill** and you can start using it

### Option 2: Upload via Claude Code

1. **Open Claude Code** in Claude.com
2. **Create a new project**
3. **Upload the skill folder** to your project
4. **Reference the skill** in your prompts

### Option 3: Use with Agent SDK (Programmatic)

```python
from anthropic import Anthropic

client = Anthropic()

# Load the skill
skill_path = "~/Documents/prompt-engineering-expert"

# Use in your agent
response = client.messages.create(
    model="claude-opus-4-1",
    max_tokens=2048,
    system=f"You have access to the prompt engineering expert skill at {skill_path}",
    messages=[
        {
            "role": "user",
            "content": "Review this prompt and suggest improvements: [PROMPT]"
        }
    ]
)
```

## 💡 How to Use the Skill

### Basic Usage

Once uploaded, you can ask Claude:

```
"Review this prompt and suggest improvements:
[YOUR PROMPT]"
```

### Advanced Usage

```
"Using your prompt engineering expertise:
1. Analyze this prompt: [PROMPT]
2. Identify issues
3. Suggest specific improvements
4. Provide a refined version
5. Explain what changed and why"
```

### For Custom Instructions

```
"Design custom instructions for an agent that:
- Analyzes customer feedback
- Extracts key themes
- Generates recommendations
- Outputs structured JSON"
```

### For Troubleshooting

```
"This prompt isn't working:
[PROMPT]

Issues I'm seeing:
- [ISSUE 1]
- [ISSUE 2]

How can I fix it?"
```

## 📚 Skill Contents

### Core Files
- **SKILL.md** - Metadata and overview
- **CLAUDE.md** - Main instructions
- **README.md** - User guide

### Documentation
- **docs/BEST_PRACTICES.md** - Best practices guide
- **docs/TECHNIQUES.md** - Advanced techniques
- **docs/TROUBLESHOOTING.md** - Common issues

### Examples
- **examples/EXAMPLES.md** - Real-world examples

### Navigation
- **INDEX.md** - Complete index and navigation
- **SUMMARY.md** - What was created

## 🎯 Quick Start Examples

### Example 1: Analyze a Prompt
```
"Analyze this prompt for clarity and effectiveness:

'Summarize this article'

What could be improved?"
```

### Example 2: Generate a Prompt
```
"Create a prompt for analyzing customer support tickets.
The prompt should:
- Classify tickets by category
- Extract key issues
- Suggest responses
- Output as JSON"
```

### Example 3: Refine Instructions
```
"I'm creating a custom instruction for an AI agent.
Here's my draft:

[YOUR DRAFT]

Please improve it using prompt engineering best practices."
```

### Example 4: Troubleshoot
```
"My prompt keeps producing inconsistent results.
Here's the prompt:

[YOUR PROMPT]

What's wrong and how do I fix it?"
```

## 📖 Documentation Guide

### For Beginners
1. Start with **README.md**
2. Read **docs/BEST_PRACTICES.md** (Core Principles)
3. Review **examples/EXAMPLES.md** (Examples 1-3)

### For Intermediate Users
1. Read **docs/TECHNIQUES.md** (Sections 1-4)
2. Review **examples/EXAMPLES.md** (Examples 4-7)
3. Use **docs/TROUBLESHOOTING.md** as needed

### For Advanced Users
1. Study **docs/TECHNIQUES.md** (All sections)
2. Review **examples/EXAMPLES.md** (All examples)
3. Combine multiple techniques

## ✨ Key Features

### Expertise Areas
- Prompt writing best practices
- Advanced techniques (CoT, few-shot, XML, etc.)
- Custom instructions design
- Prompt optimization
- Anti-pattern recognition
- Evaluation frameworks
- Multimodal prompting

### Capabilities
- Analyze existing prompts
- Generate new prompts
- Refine and optimize
- Design custom instructions
- Teach best practices
- Identify issues
- Develop test cases
- Create documentation

## 🔧 Customization

### Add Domain-Specific Examples
Edit `examples/EXAMPLES.md` to add examples for your domain.

### Extend Best Practices
Add domain-specific best practices to `docs/BEST_PRACTICES.md`.

### Add Troubleshooting Cases
Add common issues to `docs/TROUBLESHOOTING.md`.

## 📊 File Structure

```
prompt-engineering-expert/
├── INDEX.md                    # Navigation guide
├── SUMMARY.md                  # What was created
├── README.md                   # User guide
├── SKILL.md                    # Metadata
├── CLAUDE.md                   # Main instructions
├── docs/
│   ├── BEST_PRACTICES.md       # Best practices
│   ├── TECHNIQUES.md           # Advanced techniques
│   └── TROUBLESHOOTING.md      # Troubleshooting
└── examples/
    └── EXAMPLES.md             # Examples
```

## 🎓 Learning Resources

### Within the Skill
- Comprehensive documentation
- Real-world examples
- Best practice checklists
- Troubleshooting guides
- Quick reference tables

### External Resources
- Claude Docs: https://docs.claude.com
- Anthropic Blog: https://www.anthropic.com/blog
- Claude Cookbooks: https://github.com/anthropics/claude-cookbooks

## ⚡ Pro Tips

1. **Start Simple** - Begin with basic prompts before advanced techniques
2. **Use Examples** - Provide examples to guide Claude's responses
3. **Be Specific** - The more specific your request, the better the results
4. **Test Thoroughly** - Always test refined prompts with real data
5. **Iterate** - Use feedback to continuously improve
6. **Document** - Keep notes on what works for your use case

## 🚀 Next Steps

1. **Upload the skill** using one of the methods above
2. **Try a simple example** to get familiar with it
3. **Review the documentation** for deeper learning
4. **Apply to your prompts** and iterate
5. **Share with your team** for collaborative improvement

## 📞 Support

### If You Need Help

1. **Check INDEX.md** for navigation
2. **Review TROUBLESHOOTING.md** for common issues
3. **Look at EXAMPLES.md** for similar cases
4. **Read BEST_PRACTICES.md** for guidance

### Common Questions

**Q: How do I upload the skill?**
A: See "Option 1: Upload via Claude.com" above

**Q: Can I customize the skill?**
A: Yes! Edit the markdown files to add domain-specific content

**Q: What if my prompt still doesn't work?**
A: Check TROUBLESHOOTING.md or ask Claude to debug it

**Q: Can I use this with the API?**
A: Yes! See "Option 3: Use with Agent SDK" above

## 🎉 You're Ready!

Your Prompt Engineering Expert Skill is ready to use. Start by uploading it and asking Claude to review one of your prompts!

---

**Questions?** Check the documentation files or ask Claude directly!
