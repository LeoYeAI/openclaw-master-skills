# Nova Act Cookbook

Best practices for using Amazon Nova Act effectively in usability testing.

## Core Principles

### 0. Nova Act is a Browser Automation Tool, NOT a Reasoning Engine

**CRITICAL:** Nova Act executes browser actions. It should NOT:
- Reason about user personas
- Judge if a task is "easy" or "hard"
- Evaluate usability or user experience
- Decide what's "important" for a user type

**The Claude agent does the reasoning.** Nova Act just clicks, types, and reports what it sees.

❌ **WRONG:** Asking Nova Act to reason
```python
# Don't ask Nova Act to think about personas or UX
nova.act("As a beginner user, can you easily find the documentation?")
nova.act("Would a business professional find the pricing clear?")
nova.act("Is this task accomplishable for someone with low technical skills?")
```

✅ **RIGHT:** Give Nova Act direct browser tasks
```python
# Simple, direct browser commands
nova.act("Click the Documentation link in the navigation")
nova.act("Find and click a link containing 'Pricing'")
nova.act_get("What text is displayed in the main heading?")
nova.act_get("List the navigation menu items visible on this page")
```

**The workflow:**
1. **Agent** decides what to test based on persona (e.g., "Can Dorothy find how to watch golf?")
2. **Agent** generates simple prompts for Nova Act ("Click 'Watch & Listen' in the navigation")
3. **Nova Act** executes the browser task and returns raw results
4. **Agent** interprets results in context of persona ("Dorothy would struggle here because...")

### 1. Nova Act Matching Behavior

**CRITICAL:** Nova Act has two matching modes:

**Exact Matching (with quotes):**
- `"Documentation"` → Only matches the exact word "Documentation"
- `"API Documentation"` → Only matches that exact phrase
- Use for precise element identification

**Loose Matching (without quotes):**
- `Documentation` → Can match "Documentation", "Docs", "API Documentation", etc.
- More flexible, fuzzy matching
- Use for broader searches

❌ **WRONG:** Using quotes when you want flexible matching
```python
# This is too strict - will miss "API Docs", "Developer Docs", etc.
nova.act_get('Is there a link labeled "Documentation"?')
```

✅ **RIGHT:** Use quotes strategically
```python
# Loose matching - finds variations
nova.act_get('Is there a link with Documentation in it?')

# Exact matching - when you know the precise text
nova.act_get('Click the link that says "Sign Up"')
```

**Best Practice:** When searching for elements:
1. Start broad (no quotes): "What links do you see in the navigation?"
2. Use loose matching first: "Is there a link with Documentation?"
3. If you need precision: Use quotes for exact text matching
4. Try variations if first attempt fails

### 1. Break Tasks into Small Steps

Nova Act works most reliably when tasks can be accomplished in **fewer than 30 steps**.

❌ DON'T: Single large act() call
```python
nova.act("book me a hotel that costs less than $100 with highest rating then find car rental and book lunch")
```

✅ DO: Multiple small act() calls
```python
hotel = nova.act_get("book a hotel for $100 or less, return the address")
nova.act(f"book restaurant near {hotel.response} at 12:30pm")
nova.act(f"rent a car near {hotel.response}")
```

### 2. Be Direct and Specific

Make prompts clear about exactly what should happen.

❌ DON'T: Vague instructions
```python
nova.act("Let's see what routes are available")
```

✅ DO: Direct instructions  
```python
nova.act("Navigate to the routes tab")
```

### 3. Extract Information with Schemas

Use `act_get()` with Pydantic schemas for structured data extraction.

```python
from pydantic import BaseModel

class PricingInfo(BaseModel):
    price: float
    currency: str
    features: list[str]

result = nova.act_get(
    "Find the pricing information on this page",
    schema=PricingInfo.model_json_schema()
)

pricing = PricingInfo.model_validate(result.parsed_response)
```

### 4. Observe and Analyze Each Step

After each `act()` call, analyze the result before deciding the next action.

```python
# Navigate to page
nova.act("Go to the pricing page")

# Check if successful
is_found = nova.act_get(
    "Is there a pricing table visible on this page?",
    schema=BOOL_SCHEMA
)

if is_found.parsed_response:
    # Extract pricing
    pricing = nova.act_get("Extract all pricing tiers", schema=PricingSchema)
else:
    # Try alternative path
    nova.act("Look for a 'Plans' or 'Subscribe' link")
```

### 5. Use Playwright for Fine Control

For sensitive data or precise actions, use Playwright APIs directly:

```python
# Focus on field with act(), then type with Playwright
nova.act("click on the password field")
nova.page.keyboard.type(password)  # Doesn't send over network
nova.act("click sign in")
```

## Common Patterns

### Navigation Testing
```python
# Check if navigation is clear
nova.act("Navigate to the main menu")
is_clear = nova.act_get(
    "Are the menu items clearly labeled and easy to understand?",
    schema=BOOL_SCHEMA
)
```

### Form Filling
```python
# Fill forms step by step
nova.act("Click on the signup form")
nova.act("Enter email address test@example.com")
nova.act("Enter name 'John Doe'")
result = nova.act_get("Is there a clear submit button visible?")
```

### Search Testing
```python
# Test search functionality
nova.act("search for 'pricing'. press enter to initiate search")
results = nova.act_get(
    "Are search results relevant to 'pricing'?",
    schema=BOOL_SCHEMA
)
```

### Information Architecture
```python
# Test if information is findable
time_to_find = measure_time()
nova.act("Find the contact information")
duration = time_to_find()

# Note: If it took >30 steps or multiple attempts, that's a UX issue
```

## Persona Adaptation

Adjust act() prompts based on persona tech proficiency:

**Low proficiency (elderly user):**
```python
# More explicit, step-by-step
nova.act("Look for a button that says 'Contact' or 'Contact Us'")
nova.act("Click on the Contact button")
```

**High proficiency (power user):**
```python
# Test efficiency paths
nova.act("Find keyboard shortcut for search")
nova.act("Use keyboard shortcut to open search")
```

## Error Handling

```python
try:
    result = nova.act("Complete checkout")
except ActAgentError as e:
    # Agent couldn't complete - this is a UX issue!
    note_friction_point(
        "Checkout flow failed - agent couldn't figure it out",
        error=str(e)
    )
```

## Iterative Exploration Pattern

For usability testing, use an **explore-adapt-verify** approach:

**Step 1: Broad Discovery**
```python
# Don't assume - ask what's there
nav_items = nova.act_get("What navigation links do you see at the top?", schema=StringArraySchema)
```

**Step 2: Adapt Based on Findings**
```python
# If you found "API Documentation", now search for it specifically
if "API" in nav_items:
    nova.act("Click on the link containing 'API'")
```

**Step 3: Verify Hypothesis Multiple Ways**
```python
# Hypothesis: "Users can't find pricing"
# Approach 1: Check nav
has_nav_pricing = nova.act_get("Is 'Pricing' in the navigation?", schema=BOOL_SCHEMA)

# Approach 2: Check page body
if not has_nav_pricing:
    nova.act("Scroll down")
    has_body_pricing = nova.act_get("Do you see pricing or cost information?", schema=BOOL_SCHEMA)

# Approach 3: Check variations
if not has_body_pricing:
    has_plans = nova.act_get("Do you see 'Plans' or 'Subscribe'?", schema=BOOL_SCHEMA)
```

## Nova Act Trace Files

**Nova Act automatically generates detailed HTML trace files** for every session!

These trace files contain:
- Screenshots at each step
- AI reasoning and decisions
- Actions taken and their results
- Full timeline of the session

**Where to find them:**
- Set `logs_directory` when creating NovaAct instance
- Files are named: `act_<uuid>_output.html`
- Each test captures these files
- **Linked automatically in the HTML report**

```python
with NovaAct(
    starting_page=url,
    logs_directory="/path/to/logs"  # Set custom directory
) as nova:
    nova.act("Navigate somewhere")
    # Trace file automatically created
```

## Workflow Testing (Not Just Information Finding)

**Modern usability testing goes beyond "can users find the docs?"** — it tests whether users can **complete real tasks end-to-end**.

### Real User Journeys to Test

**Flight Booking Sites:**
- Search for flights (origin, destination, dates)
- Filter results (price, time, airline)
- Select a flight
- Fill passenger information
- **STOP before payment**

**E-Commerce Sites:**
- Search for product
- Add to cart
- Modify quantity
- Proceed to checkout
- Fill shipping info
- **STOP before payment/order placement**

**Social Media Platforms:**
- Create new post
- Add text content
- Attach media (if applicable)
- Preview post
- **STOP before publishing**

**SaaS/Software Sites:**
- Sign up flow (fill registration form)
- **STOP before final submission** (unless explicitly testing signup)
- Demo/trial access workflow
- Feature exploration
- Settings configuration

**Newsletter/Form Submissions:**
- Fill out form fields
- Verify validation works
- **STOP before final submit button** (unless explicitly testing)

### Safety Guardrails - STOP Before Material Impact ⚠️

**ALWAYS stop testing before actions that cause:**
- 💳 **Monetary impact**: Charges, purchases, subscriptions, donations
- 📧 **External communication**: Sending emails, posting publicly, messaging real users
- 🔐 **Account creation**: Creating real accounts (use "test" flows if available)
- 🗑️ **Data modification**: Deleting, editing, or corrupting existing data
- 📝 **Legal commitment**: Agreeing to terms, signing contracts, submitting official forms
- 📬 **Spam/annoyance**: Newsletter signups, notification opt-ins

**How to Test Safely:**

1. **Navigate TO the final step** (checkout page, publish screen, submit button)
2. **Verify the final action is accessible** (button exists, is enabled, is clear)
3. **Use `act_get()` to observe without acting**:
   ```python
   # Good: Observe the checkout button
   checkout_ready = nova.act_get(
       "Is there a 'Complete Purchase' or 'Pay Now' button visible and enabled?",
       schema=BOOL_SCHEMA
   )
   ```
4. **Document readiness but DO NOT CLICK**
5. **In observations, explicitly note the safety stop**:
   ```python
   observations.append({
       "step": "verify_checkout_accessible",
       "action": "Confirmed payment button is reachable",
       "success": checkout_ready.parsed_response,
       "notes": "✅ Workflow complete up to payment. STOPPED per safety guidelines - no actual purchase made."
   })
   ```

**Example: Safe Flight Booking Test**

```python
def test_flight_booking_workflow(nova, persona):
    """Test flight booking WITHOUT actually booking."""
    
    observations = []
    
    # Step 1: Search
    nova.act("Find the flight search form")
    nova.act("Enter departure city: New York")
    nova.act("Enter destination city: Los Angeles")
    nova.act("Select departure date 2 weeks from today")
    nova.act("Select return date 3 weeks from today")
    nova.act("Click the search button")
    
    search_success = nova.act_get(
        "Are flight results displayed with prices and times?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "search_flights",
        "action": "Searched for NYC to LAX flights",
        "success": search_success.parsed_response,
        "notes": "Flight search returned results" if search_success.parsed_response else "Search failed or no results"
    })
    
    if not search_success.parsed_response:
        return observations  # Can't continue if search failed
    
    # Step 2: Select flight
    nova.act("Click on the first available flight option")
    
    flight_selected = nova.act_get(
        "Is the selected flight now highlighted or showing details?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "select_flight",
        "action": "Selected first available flight",
        "success": flight_selected.parsed_response,
        "notes": "Flight selection worked" if flight_selected.parsed_response else "Could not select flight"
    })
    
    # Step 3: Fill passenger info
    nova.act("Click continue or proceed to passenger information")
    nova.act("Enter passenger name: John Doe")
    nova.act("Enter email: test@example.com")
    nova.act("Enter phone: 555-0123")
    
    form_filled = nova.act_get(
        "Are all passenger information fields filled out?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "fill_passenger_info",
        "action": "Filled passenger details",
        "success": form_filled.parsed_response,
        "notes": "Form filled successfully" if form_filled.parsed_response else "Form filling incomplete"
    })
    
    # Step 4: Verify checkout is reachable (BUT DON'T CLICK)
    checkout_accessible = nova.act_get(
        "Is there a 'Continue to Payment', 'Proceed to Checkout', or 'Complete Booking' button visible?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "verify_payment_reachable",
        "action": "Verified checkout button exists",
        "success": checkout_accessible.parsed_response,
        "notes": "⚠️ SAFETY STOP: Checkout accessible but NOT clicked. Booking workflow verified up to payment step. No actual booking made."
    })
    
    # Overall success: Could we reach checkout?
    workflow_success = checkout_accessible.parsed_response
    
    return observations, workflow_success
```

**Example: Safe E-Commerce Test**

```python
def test_ecommerce_purchase(nova, persona):
    """Test product purchase workflow WITHOUT completing transaction."""
    
    # Search for product
    nova.act("Search for 'laptop'")
    nova.act("Click on the first product in search results")
    
    # Add to cart
    nova.act("Click the 'Add to Cart' button")
    
    cart_success = nova.act_get(
        "Is there confirmation the item was added to cart?",
        schema=BOOL_SCHEMA
    )
    
    # Proceed to checkout
    nova.act("Click on the cart icon or 'View Cart' button")
    nova.act("Click 'Proceed to Checkout' or 'Checkout'")
    
    # Fill shipping (use fake data)
    nova.act("Fill shipping name: Test User")
    nova.act("Fill address: 123 Test St")
    nova.act("Fill city: Test City")
    nova.act("Fill zip: 12345")
    
    # Verify we reached payment step
    payment_page = nova.act_get(
        "Is there a payment method section or credit card form visible?",
        schema=BOOL_SCHEMA
    )
    
    # STOP HERE - do not enter payment info or submit
    return {
        "success": payment_page.parsed_response,
        "notes": "⚠️ SAFETY STOP: Reached payment page. Cart and checkout flow functional. NO PURCHASE MADE."
    }
```

### Detecting Material Impact Actions

When generating test strategies, identify if the test case involves:

```python
MATERIAL_IMPACT_KEYWORDS = [
    # Monetary
    "buy", "purchase", "checkout", "pay", "subscribe", "donate",
    # Communication
    "post", "publish", "share", "send", "email", "message",
    # Account creation
    "sign up", "register", "create account",
    # Submissions
    "submit", "apply", "enroll",
    # Newsletter/notifications
    "subscribe", "sign up for newsletter", "get updates"
]

def requires_safety_stop(test_case: str) -> bool:
    """Check if test case involves material impact."""
    test_lower = test_case.lower()
    return any(keyword in test_lower for keyword in MATERIAL_IMPACT_KEYWORDS)
```

If detected, **modify the test strategy** to:
1. Include all steps UP TO the final action
2. Replace final action with verification
3. Document the safety stop in observations

## Usability Observations

Document friction points as you observe them:

- **Task failed after multiple approaches** = Major UX issue
- **Found after 2+ attempts** = Moderate UX issue (discoverability)
- **Found but unclear label** = Minor UX issue
- **Small text, poor contrast** = Accessibility issue
- **>20 steps for simple task** = Efficiency issue
- **Workflow reachable but confusing** = Navigation/flow issue
- **Form validation unclear or missing** = Usability issue
- **Mobile responsiveness problems** = Accessibility issue
