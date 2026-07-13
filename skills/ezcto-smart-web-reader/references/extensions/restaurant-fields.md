# Restaurant Extension Fields (Enhanced)

When the site is detected as a restaurant or food service website, extract these additional fields into the `extensions.restaurant` object.

---

## Additional Extraction Rules

### 1. Cuisine Type
Identify the cuisine style(s):

**Common cuisines:**
- Italian, Chinese, Japanese, Korean, Thai, Vietnamese
- Mexican, Indian, Mediterranean, French, American
- Fusion, Contemporary, Traditional

**Sources:**
- Page title or description
- "Our cuisine" section
- Schema.org Restaurant type
- Menu categories

**Format:** Array (restaurants can serve multiple cuisines)
```json
"cuisine": ["Italian", "Mediterranean"]
```

### 2. Menu Items
Extract visible menu items with pricing:

**Fields per item:**
- `name`: Dish name
- `price`: Price (number as string)
- `currency`: Currency code (USD, EUR, etc.)
- `description`: Dish description
- `category`: Menu category (Appetizers, Entrees, Desserts, etc.)
- `dietary_info`: Dietary labels if present
  - `vegetarian`, `vegan`, `gluten_free`, `dairy_free`, `spicy`
- `image`: Dish image URL if available

**Where to look:**
- Menu page/section
- PDF menu (extract text if embedded)
- Schema.org Menu markup

**Limit:** Extract up to 20 menu items (avoid overwhelming output)

### 3. Business Hours
Extract operating hours for each day:

**Format:**
```json
"business_hours": {
  "monday": "11:00 AM - 10:00 PM",
  "tuesday": "11:00 AM - 10:00 PM",
  "wednesday": "11:00 AM - 10:00 PM",
  "thursday": "11:00 AM - 10:00 PM",
  "friday": "11:00 AM - 11:00 PM",
  "saturday": "10:00 AM - 11:00 PM",
  "sunday": "10:00 AM - 9:00 PM"
}
```

**Alternative compact format:**
```json
"business_hours": "Mon-Fri: 11AM-10PM, Sat-Sun: 10AM-11PM"
```

**Sources:**
- "Hours" section
- Footer
- Schema.org openingHours
- Google Business hours widget

### 4. Reservation System
Extract reservation/booking information:

**Fields:**
- `reservation_url`: Link to reservation page
- `reservation_platforms`: Platforms used
  - "opentable", "resy", "tock", "yelp", "proprietary"
- `phone_reservation`: Phone number for reservations
- `walk_ins_accepted`: true/false if mentioned

### 5. Delivery Platforms
Identify linked delivery services:

**Common platforms:**
- DoorDash, UberEats, GrubHub, Postmates
- Seamless, Caviar, ChowNow
- Proprietary delivery system

**Extract:**
- Platform names
- Links to restaurant page on each platform

### 6. Location Details
Extract physical location information:

**Fields:**
- `address`: Full street address
- `city`: City
- `state`: State/province
- `zip`: Postal code
- `country`: Country
- `map_url`: Google Maps or other map link
- `directions`: Directions text if provided
- `parking`: Parking information if mentioned

### 7. Special Features (NEW)
Extract unique restaurant features:

**Examples:**
- `outdoor_seating`: true/false
- `private_dining`: true/false
- `bar`: true/false
- `wifi`: true/false
- `accepts_reservations`: true/false
- `takeout`: true/false
- `delivery`: true/false
- `catering`: true/false
- `kid_friendly`: true/false
- `pet_friendly`: true/false

### 8. Chef Information (NEW)
If featured prominently:

**Fields:**
- `chef_name`: Head chef name
- `chef_bio`: Brief biography
- `awards`: Awards or recognitions

### 9. Reviews Summary (NEW)
If review data is displayed:

**Fields:**
- `rating`: Average rating (e.g., "4.5")
- `review_count`: Number of reviews
- `review_platforms`: ["Google", "Yelp", "TripAdvisor"]

---

## Output Format

```json
{
  "extensions": {
    "restaurant": {
      "cuisine": ["Italian", "Mediterranean"],

      "menu_items": [
        {
          "name": "Margherita Pizza",
          "price": "14.99",
          "currency": "USD",
          "description": "Classic pizza with tomato, mozzarella, and basil",
          "category": "Pizza",
          "dietary_info": ["vegetarian"],
          "image": "https://example.com/images/margherita.jpg"
        },
        {
          "name": "Spaghetti Carbonara",
          "price": "18.99",
          "currency": "USD",
          "description": "Traditional Roman pasta with guanciale and pecorino",
          "category": "Pasta"
        }
      ],

      "business_hours": {
        "monday": "11:00 AM - 10:00 PM",
        "tuesday": "11:00 AM - 10:00 PM",
        "wednesday": "11:00 AM - 10:00 PM",
        "thursday": "11:00 AM - 10:00 PM",
        "friday": "11:00 AM - 11:00 PM",
        "saturday": "10:00 AM - 11:00 PM",
        "sunday": "10:00 AM - 9:00 PM"
      },

      "reservation": {
        "url": "https://www.opentable.com/restaurant-example",
        "platforms": ["opentable", "resy"],
        "phone": "+1-555-123-4567",
        "walk_ins_accepted": true
      },

      "delivery_platforms": [
        {
          "name": "DoorDash",
          "url": "https://www.doordash.com/store/restaurant-example"
        },
        {
          "name": "UberEats",
          "url": "https://www.ubereats.com/store/restaurant-example"
        }
      ],

      "location": {
        "address": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102",
        "country": "USA",
        "map_url": "https://maps.google.com/?q=123+Main+St+SF",
        "parking": "Street parking and nearby garage"
      },

      "features": {
        "outdoor_seating": true,
        "private_dining": true,
        "bar": true,
        "wifi": true,
        "takeout": true,
        "delivery": true,
        "catering": true,
        "kid_friendly": true,
        "pet_friendly": false
      },

      "chef": {
        "name": "Chef Giovanni Rossi",
        "bio": "Award-winning Italian chef with 20 years of experience",
        "awards": ["Michelin Star 2023", "Best Italian Restaurant 2024"]
      },

      "reviews": {
        "rating": "4.7",
        "review_count": "1,523",
        "platforms": ["Google", "Yelp", "TripAdvisor"]
      }
    }
  }
}
```

---

## OpenClaw Agent Suggestions (Restaurant-Specific)

```json
{
  "agent_suggestions": {
    "primary_action": {
      "label": "Make Reservation",
      "url": "{{ extensions.restaurant.reservation.url }}",
      "purpose": "book_table",
      "priority": "high"
    },
    "next_actions": [
      {
        "action": "view_menu",
        "url": "/menu",
        "reason": "Browse full menu before visiting",
        "priority": 1
      },
      {
        "action": "order_delivery",
        "url": "{{ extensions.restaurant.delivery_platforms[0].url }}",
        "reason": "Order food for delivery",
        "priority": 2
      },
      {
        "action": "get_directions",
        "url": "{{ extensions.restaurant.location.map_url }}",
        "reason": "Get directions to restaurant",
        "priority": 3
      }
    ],
    "skills_to_chain": [
      {
        "skill": "calendar-add",
        "input": {
          "event": "Dinner at {{ entities.organization }}",
          "location": "{{ extensions.restaurant.location.address }}",
          "url": "{{ extensions.restaurant.reservation.url }}"
        },
        "reason": "Add reservation to calendar"
      },
      {
        "skill": "review-analyzer",
        "input": "{{ extensions.restaurant.reviews.platforms }}",
        "reason": "Analyze customer reviews across platforms"
      }
    ],
    "cache_freshness": {
      "should_refresh_after": "7 days",
      "refresh_priority": "low",
      "reason": "Menu and hours rarely change"
    }
  }
}
```

---

## Validation Rules

- **Prices:** Must be positive numbers (as strings)
- **Hours:** Use 12-hour format with AM/PM for consistency
- **Phone:** Preserve format exactly as displayed
- **Address:** Extract as complete as possible
- **Cuisine:** Use standard cuisine type names

---

## Error Handling

If menu not found but restaurant detected:

```json
{
  "extensions": {
    "restaurant": {
      "cuisine": ["Italian"],
      "menu_items": [],
      "extraction_confidence": "low",
      "warnings": [
        "Restaurant detected but menu not found",
        "Menu might be on a separate page or PDF"
      ],
      "menu_url": "https://example.com/menu.pdf"
    }
  }
}
```
