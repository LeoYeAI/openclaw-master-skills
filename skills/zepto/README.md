# Zepto Grocery Automation

**Order groceries in 30 seconds. From chat to checkout.**

Just tell your AI what you need. It shops, generates a payment link, sends it to WhatsApp. You pay on your phone. Groceries arrive in 10 minutes.

## How It Works

**You:** "Order milk and bread from Zepto"

**AI does:**
1. ✅ Confirms your delivery address
2. 🛒 Finds items, adds to cart
3. 💳 Generates payment link
4. 📱 Sends link to your WhatsApp

**You:** Click link, pay, done. Groceries on the way.

---

## Examples

**Quick orders:**
- "Add 2 liters of milk and a loaf of bread"
- "Order vegetables - tomatoes, onions, potatoes"
- "Get me Amul butter and cheese"

**Smart recommendations:**
- Remembers what you usually order
- "Add my usual milk" → automatically picks the brand you always get

**Full shopping list:**
- "Add milk, bread, eggs, coriander, ginger, and tea bags"
- AI adds everything, shows total, sends payment link

---

## Features

- 🏠 **Address confirmation** - Always checks before ordering
- 🧠 **Remembers your usuals** - Tracks what you order frequently
- 🛒 **Smart cart** - Adds all items, then shows summary
- 💳 **Payment links** - Pay securely via WhatsApp on your phone
- ✅ **Order verification** - Confirms when your order is on the way
- 🧹 **Auto cleanup** - Clears cart after each order

## Quick Start

**Just say:**
- "Order groceries from Zepto"
- "Add milk and bread to my Zepto cart"
- "Get me vegetables - onions, tomatoes, potatoes"

**The AI will:**
1. Confirm your address
2. Add items to cart
3. Send payment link to WhatsApp
4. Verify order after you pay

**That's it!** Groceries arrive in ~10 minutes.

## Version History

### v1.0.5 (2026-02-09)
- **Improved**: Much better description and examples - clear, concise, user-friendly
- **Improved**: README now shows actual usage examples
- **Improved**: Highlights speed and simplicity (30 seconds from chat to checkout)

### v1.0.4 (2026-02-09)
- **Security**: Completely removed all cron job functionality
- **Improved**: Payment message now explicitly asks user to message "DONE" 
- **Improved**: Order verification only on explicit user confirmation
- **Fixed**: Discrepancy in documentation about cron removal

### v1.0.3 (2026-02-09)
- **Improved**: Address confirmation now mandatory before every order
- **Improved**: Smart cart clearing - auto-clear after payment, ask during normal flow
- **Improved**: Payment link message includes order confirmation instructions
- **Improved**: Post-payment flow verifies order status and clears cart automatically
- **Fixed**: Cart persistence issue after payment (items remained in cart)
- **Fixed**: Multi-item ordering now adds all items first, then shows cart summary
- **Improved**: Item selection logic - ask when unclear about variants
- **Documented**: Complete workflow mapping with button references

### v1.0.2 (2026-02-09)
- Internal version (deleted, security improvements)

### v1.0.1 (2026-02-09)
- Changed display name from "Zepto India Grocery Automation" to "zepto"

### v1.0.0 (2026-02-08)
- Initial release with full Zepto automation

## Requirements

- **OpenClaw** with browser control enabled
- **WhatsApp** channel configured (for payment links)
- **Zepto account** (skill handles login via Phone + OTP)
- **India location** (Zepto delivers in major Indian cities)

## First Time Setup

The skill walks you through:
1. Phone number + OTP login to Zepto
2. Address confirmation
3. First order

After that, you're logged in and can order anytime.

## Author

Created by Gaurav

## License

MIT
