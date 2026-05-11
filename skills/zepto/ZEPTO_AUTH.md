---
name: zepto-auth
description: Zepto authentication flow - handle phone number entry, OTP verification, and address confirmation
metadata: {"openclaw":{"emoji":"🔐"}}
---

# Zepto Authentication Skill

Complete authentication and setup flow for Zepto orders.

## Flow Overview
1. **Phone Number Entry** - User provides phone number
2. **OTP Verification** - I ask user for OTP received on phone
3. **Address Confirmation** - Verify delivery address with user
4. **Ready to Order** - User can now place orders

---

## Step 1: Phone Number Entry

**Ask user for phone number:**
```
"What's your phone number for Zepto? (10 digits)"
```

**Enter phone number in browser:**
```bash
browser act profile=openclaw request='{"kind":"type","ref":"e1","text":"{phone}"}'
browser act profile=openclaw request='{"kind":"click","ref":"e2"}'  # Continue button
```

---

## Step 2: OTP Verification

**After phone number submitted, Zepto sends OTP to user's phone.**

**Ask user for OTP:**
```
"I've sent the OTP to {phone}. What's the OTP you received?"
```

**Wait for user to provide OTP (via WhatsApp message)**

**Enter OTP in browser:**
```bash
browser snapshot --interactive profile=openclaw  # Get OTP input field refs
browser act profile=openclaw request='{"kind":"type","ref":"{otp_input_ref}","text":"{otp}"}'
browser act profile=openclaw request='{"kind":"click","ref":"{verify_button_ref}"}'
```

---

## Step 3: Address Confirmation

**After OTP verification, check if location is set:**

```bash
browser navigate url=https://www.zepto.com profile=openclaw
browser snapshot --interactive profile=openclaw
```

**Look for location button (usually shows current address or "Select Location")**

**If location not set or needs confirmation:**

**Ask user:**
```
"Where should I deliver your Zepto order? 
Current saved addresses: {list_addresses}

Reply with:
1. Number to select saved address
2. New address (I'll help you add it)"
```

**To add new address:**
1. Click "Select Location" button
2. User can either:
   - Type address
   - Enable location (if on phone)
   - Select from saved addresses

**Confirm with user:**
```
"Delivery address set to: {address}
Zepto ETA: {eta_minutes} mins
Is this correct? (yes/no)"
```

---

## Step 4: Serviceability Check

**After address is set, check if location is serviceable:**

```bash
browser navigate url=https://www.zepto.com profile=openclaw
# Look for "Store closed" or "Not serviceable" messages
```

**If serviceable:**
```
✅ You're all set! I can now order groceries for you.
Delivery ETA: {eta} mins
Store: {store_name}

What would you like to add to cart?
```

**If NOT serviceable:**
```
⚠️ Your location ({address}) is currently not serviceable by Zepto.

This could be because:
- Store temporarily closed (back in {eta} mins)
- Location outside delivery zone

Want to try a different address?
```

---

## Complete Authentication Script

```python
#!/usr/bin/env python3
"""
Zepto Authentication Handler
"""

def authenticate_zepto(phone_number):
    """
    Complete Zepto authentication flow
    Returns: (success, user_data)
    """
    
    # Step 1: Enter phone number
    print(f"Entering phone number: {phone_number}")
    # browser commands...
    
    # Step 2: Ask for OTP
    otp = input("Enter OTP received on phone: ")
    # browser commands to enter OTP...
    
    # Step 3: Check/confirm address
    # browser commands to get current address...
    
    # Step 4: Verify serviceability
    # Check if location is serviceable...
    
    return {
        "authenticated": True,
        "phone": phone_number,
        "address": address,
        "serviceable": True,
        "eta_minutes": 15,
        "store_name": "Store Name"
    }
```

---

## Error Handling

**Invalid Phone Number:**
```
"Phone number should be 10 digits. Please try again."
```

**Invalid OTP:**
```
"OTP verification failed. Let me resend the OTP.
Check your phone for the new code."
```

**Location Not Serviceable:**
```
"Your location is not serviceable right now.
Want to try a different address?"
```

---

## Session Persistence

**After successful auth:**
- Browser session stays logged in (cookies saved)
- No need to re-authenticate for future orders
- Can directly proceed to adding items to cart

**To check if already authenticated:**
```bash
browser navigate url=https://www.zepto.com profile=openclaw
browser snapshot --interactive profile=openclaw
# Look for "login" button vs user profile icon
```

**If logged in:** Skip auth, proceed to ordering
**If logged out:** Run full auth flow

---

## Security

- **Never store OTP** - ask user each time
- **Never automate OTP entry without user confirmation**
- **Always confirm address before ordering**
- **User must approve each order**

---

## Integration with Main Zepto Skill

Before any order, check authentication status:
1. Is user logged in? → Proceed
2. Not logged in? → Run auth flow first
3. Address confirmed? → Proceed
4. Location serviceable? → Proceed

Only after all checks pass, proceed with adding items to cart.
