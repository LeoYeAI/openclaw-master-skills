---
name: food402
description: Order food from TGO Yemek (Trendyol GO), Turkey's leading food delivery service. Use when user wants to order food delivery in Turkey, browse restaurants, search for foods, manage delivery addresses, check order history, or checkout with 3D Secure payment.
metadata: {"openclaw": {"emoji": "🍕", "requires": {"bins": ["curl", "jq", "openssl"], "env": ["TGO_EMAIL", "TGO_PASSWORD", "GOOGLE_PLACES_API_KEY"]}, "primaryEnv": "TGO_EMAIL"}}
---

# Food402 - TGO Yemek Food Delivery

Order food from Trendyol GO (TGO Yemek), Turkey's leading food delivery service. This skill enables complete food ordering: browse restaurants, view menus, customize items, manage cart, and checkout with 3D Secure payment.

## Setup

### OpenClaw

Add the following to your `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "food402": {
        "enabled": true,
        "env": {
          "TGO_EMAIL": "your-tgo-email@example.com",
          "TGO_PASSWORD": "your-tgo-password",
          "GOOGLE_PLACES_API_KEY": "your-google-api-key"
        }
      }
    }
  }
}
```

### Claude Code / Cursor / Codex / Gemini CLI

Set environment variables in your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export TGO_EMAIL="your-tgo-email@example.com"
export TGO_PASSWORD="your-tgo-password"
export GOOGLE_PLACES_API_KEY="your-google-api-key"  # Optional: for Google Reviews
```

Then reload your shell or run `source ~/.zshrc` (or equivalent).

## Authentication

The skill automatically handles authentication. When making API calls:

1. Run `{baseDir}/scripts/auth.sh get-token` to get a valid JWT
2. The script caches tokens in `/tmp/food402-token` with automatic refresh (60s buffer before expiry)
3. If any API call returns 401, clear the token with `{baseDir}/scripts/auth.sh clear-token` and retry

**Manual authentication check:**
```bash
{baseDir}/scripts/auth.sh check-token
```

## Required Workflow

**IMPORTANT:** You MUST follow this order:

1. **select_address** - REQUIRED first step (sets delivery location for cart)
2. **get_restaurants** or **search_restaurants** - Browse/search restaurants
3. **get_restaurant_menu** - View a restaurant's menu
4. **get_product_details** - Check customization options (if needed)
5. **add_to_basket** - Add items to cart
6. **checkout_ready** - Verify cart is ready for payment
7. **place_order** - Complete the order with 3D Secure

If `add_to_basket` fails, try `clear_basket` first then retry.

---

## Address Management Operations

### get_addresses

Get user's saved delivery addresses. Call this first to show available addresses.

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-user-apimemberaddress-santral/addresses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response fields:** `id`, `addressName`, `addressLine`, `neighborhoodName`, `districtName`, `cityName`, `latitude`, `longitude`

### select_address

**MUST be called before browsing restaurants or adding to basket.** Sets the shipping address for the cart.

**Parameters:**
- `addressId` (required): Address ID from get_addresses

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X POST "https://api.tgoapis.com/web-checkout-apicheckout-santral/shipping" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{"shippingAddressId": {addressId}, "invoiceAddressId": {addressId}}'
```

### add_address

Add a new delivery address. Use get_cities → get_districts → get_neighborhoods to find location IDs first.

**Parameters:**
- `name` (required): First name
- `surname` (required): Last name
- `phone` (required): Phone without country code (e.g., "5356437070")
- `addressName` (required): Label (e.g., "Home", "Work")
- `addressLine` (required): Street address
- `cityId` (required): From get_cities
- `districtId` (required): From get_districts
- `neighborhoodId` (required): From get_neighborhoods
- `latitude` (required): Coordinate string
- `longitude` (required): Coordinate string
- `apartmentNumber`, `floor`, `doorNumber`, `addressDescription` (optional)
- `elevatorAvailable` (optional): boolean

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X POST "https://api.tgoapis.com/web-user-apimemberaddress-santral/addresses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{
    "name": "{name}",
    "surname": "{surname}",
    "phone": "{phone}",
    "addressName": "{addressName}",
    "addressLine": "{addressLine}",
    "cityId": {cityId},
    "districtId": {districtId},
    "neighborhoodId": {neighborhoodId},
    "latitude": "{latitude}",
    "longitude": "{longitude}",
    "countryCode": "TR",
    "elevatorAvailable": false
  }' | jq
```

**Note:** If response is 429, OTP verification is required. Direct user to add the address at tgoyemek.com instead.

### get_cities

Get list of all cities for address selection.

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-user-apimemberaddress-santral/cities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq '.cities[] | {id, name}'
```

### get_districts

Get districts for a city.

**Parameters:**
- `cityId` (required): City ID from get_cities

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-user-apimemberaddress-santral/cities/{cityId}/districts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq '.districts[] | {id, name}'
```

### get_neighborhoods

Get neighborhoods for a district.

**Parameters:**
- `districtId` (required): District ID from get_districts

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-user-apimemberaddress-santral/districts/{districtId}/neighborhoods" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq '.neighborhoods[] | {id, name}'
```

---

## Restaurant Discovery Operations

### get_restaurants

List restaurants near the selected address. **Requires select_address first.**

**Parameters:**
- `latitude` (required): From selected address
- `longitude` (required): From selected address
- `page` (optional): Page number, default 1
- `sortBy` (optional): `RECOMMENDED` (default), `RESTAURANT_SCORE`, or `RESTAURANT_DISTANCE`
- `minBasketPrice` (optional): Pass 400 to filter min order >= 400 TL

**Sorting keywords (Turkish & English):**
- "önerilen" / "recommended" / "popüler" → `RECOMMENDED`
- "en yakın" / "closest" / "yakınımdaki" → `RESTAURANT_DISTANCE`
- "en iyi" / "best rated" / "en yüksek puanlı" → `RESTAURANT_SCORE`
- "en ucuz" / "cheapest" → Use **search_restaurants** instead (returns product prices)

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-discovery-apidiscovery-santral/restaurants/filters?openRestaurants=true&latitude={latitude}&longitude={longitude}&pageSize=50&page={page}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

Add `&sortType=RESTAURANT_SCORE` or `&sortType=RESTAURANT_DISTANCE` for sorting (omit for RECOMMENDED).

**Response fields:** `id`, `name`, `kitchen`, `rating`, `ratingText`, `minBasketPrice`, `averageDeliveryInterval`, `distance`, `neighborhoodName`, `isClosed`, `campaignText`

### search_restaurants

Search restaurants and products by keyword. Results include product prices (useful for "cheapest" queries).

**IMPORTANT:** Always check `isClosed` field. Never suggest closed restaurants.

**Parameters:**
- `searchQuery` (required): Search keyword (e.g., "pizza", "burger", "dürüm")
- `latitude` (required): From selected address
- `longitude` (required): From selected address
- `page` (optional): Page number, default 1

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-restaurant-apirestaurant-santral/restaurants/in/search?searchQuery={searchQuery}&latitude={latitude}&longitude={longitude}&pageSize=50&page={page}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response includes:** Restaurant info plus `products[]` array with `id`, `name`, `description`, `price`

---

## Menu & Product Operations

### get_restaurant_menu

Get a restaurant's full menu with categories and items.

**Parameters:**
- `restaurantId` (required): Restaurant ID
- `latitude` (required): Coordinate
- `longitude` (required): Coordinate

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-restaurant-apirestaurant-santral/restaurants/{restaurantId}?latitude={latitude}&longitude={longitude}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response structure:**
- `info`: Restaurant details (id, name, rating, workingHours, deliveryTime, minOrderPrice)
- `categories[]`: Menu sections with `items[]` (id, name, description, price, likePercentage)

### get_product_details

Get product customization options (ingredients to exclude, modifier groups for extras/sizes).

**Parameters:**
- `restaurantId` (required): Restaurant ID
- `productId` (required): Product ID from menu
- `latitude` (required): Coordinate
- `longitude` (required): Coordinate

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X POST "https://api.tgoapis.com/web-restaurant-apirestaurant-santral/restaurants/{restaurantId}/products/{productId}?latitude={latitude}&longitude={longitude}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{}' | jq
```

**Response includes `components[]`:**
- `type`: `INGREDIENTS` (items to exclude) or `MODIFIER_GROUP` (extras/sizes to select)
- `modifierGroupId`: Use this ID when adding modifiers to basket
- `options[]`: Available choices with `id`, `name`, `price`, `isPopular`
- `isSingleChoice`, `minSelections`, `maxSelections`: Selection rules

### get_product_recommendations

Get "goes well with" suggestions for products.

**Parameters:**
- `restaurantId` (required): Restaurant ID
- `productIds` (required): Array of product IDs

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X POST "https://api.tgoapis.com/web-discovery-apidiscovery-santral/recommendation/product" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{
    "restaurantId": "{restaurantId}",
    "productIds": ["{productId1}", "{productId2}"],
    "page": "PDP"
  }' | jq
```

---

## Cart Management Operations

### add_to_basket

Add items to the shopping cart. **Requires select_address first.**

**Parameters:**
- `storeId` (required): Restaurant ID (NUMBER)
- `latitude` (required): Coordinate (NUMBER, not string)
- `longitude` (required): Coordinate (NUMBER, not string)
- `items[]` (required): Array of items to add

**Item structure:**
```json
{
  "productId": 12345,
  "quantity": 1,
  "modifierProducts": [
    {
      "productId": 111,
      "modifierGroupId": 222,
      "modifierProducts": [],
      "ingredientOptions": {"excludes": [], "includes": []}
    }
  ],
  "ingredientOptions": {
    "excludes": [{"id": 333}],
    "includes": []
  }
}
```

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X POST "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{
    "storeId": {storeId},
    "items": [{items}],
    "latitude": {latitude},
    "longitude": {longitude},
    "isFlashSale": false,
    "storePickup": false
  }' | jq
```

**If this fails,** try `clear_basket` first then retry.

### get_basket

Get current cart contents.

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response includes:** `storeGroups[]` with store info and products, `summary[]`, `totalPrice`, `deliveryPrice`, `isEmpty`

### remove_from_basket

Remove an item from the cart.

**Parameters:**
- `itemId` (required): Item UUID from get_basket response (the `itemId` field, NOT `productId`)

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X DELETE "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts/items/{itemId}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

### clear_basket

Clear the entire cart.

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X DELETE "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)"
```

---

## Checkout & Payment Operations

### get_saved_cards

Get user's saved payment cards (masked). If no cards, user must add one at tgoyemek.com.

**Uses Payment API with different headers:**

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://payment.tgoapps.com/v2/cards/" \
  -H "Authorization: bearer $TOKEN" \
  -H "app-name: TrendyolGo" \
  -H "x-applicationid: 1" \
  -H "x-channelid: 4" \
  -H "x-storefrontid: 1" | jq
```

**Response:** `cards[]` with `cardId`, `maskedCardNumber`, `bankName`, `cardNetwork`, `isDebitCard`

### checkout_ready

Verify cart is ready for checkout. Call this before place_order.

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts?cartContext=payment&limitPromoMbs=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Check response:**
- If `totalProductCount` is 0, cart is empty
- Check `warnings[]` for issues (e.g., below minimum order)
- Returns full cart details and `totalPrice`

### set_order_note

Set order note and service preferences. Call before place_order.

**Parameters:**
- `note` (optional): Note for courier/restaurant
- `noServiceWare` (optional): Don't include plastic/cutlery (default: false)
- `contactlessDelivery` (optional): Leave at door (default: false)
- `dontRingBell` (optional): Don't ring doorbell (default: false)

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s -X PUT "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts/customerNote" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" \
  -d '{
    "customerNote": "{note}",
    "noServiceWare": false,
    "contactlessDelivery": false,
    "dontRingBell": false
  }'
```

### place_order

Place the order with 3D Secure payment. This is a 3-step process.

**Parameters:**
- `cardId` (required): Card ID from get_saved_cards

**Step 1: Get cart with payment context**
```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-checkout-apicheckout-santral/carts?cartContext=payment&limitPromoMbs=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)"
```

**Step 2: Select payment method (Payment API)**
```bash
# Get bin code from card's maskedCardNumber (first 6 digits + **)
BINCODE="${maskedCardNumber:0:6}**"

curl -s -X POST "https://payment.tgoapps.com/v3/payment/options" \
  -H "Authorization: bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "app-name: TrendyolGo" \
  -H "x-applicationid: 1" \
  -H "x-channelid: 4" \
  -H "x-storefrontid: 1" \
  -d '{
    "paymentType": "payWithCard",
    "data": {
      "savedCardId": {cardId},
      "binCode": "{binCode}",
      "installmentId": 0,
      "reward": null,
      "installmentPostponingSelected": false
    }
  }'
```

**Step 3: Submit payment (Payment API)**
```bash
curl -s -X POST "https://payment.tgoapps.com/v2/payment/pay" \
  -H "Authorization: bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "app-name: TrendyolGo" \
  -H "x-applicationid: 1" \
  -H "x-channelid: 4" \
  -H "x-storefrontid: 1" \
  -d '{
    "customerSelectedThreeD": false,
    "paymentOptions": [{"name": "payWithCard", "cardNo": "", "customerSelectedThreeD": false}],
    "callbackUrl": "https://tgoyemek.com/odeme"
  }'
```

**3D Secure handling:** If response contains `json.content` (HTML) or `redirectUrl`:
1. Save HTML to temp file
2. Open in browser: `{baseDir}/scripts/3dsecure.sh "$HTML_CONTENT"`
3. Inform user to complete verification in browser

---

## Order History Operations

### get_orders

Get user's order history with status.

**Parameters:**
- `page` (optional): Page number, default 1

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-checkout-apicheckout-santral/orders?page={page}&pageSize=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response:** `orders[]` with `id`, `orderDate`, `store`, `status`, `price`, `products[]`

### get_order_detail

Get detailed information about a specific order including delivery status.

**Parameters:**
- `orderId` (required): Order ID from get_orders

```bash
TOKEN=$({baseDir}/scripts/auth.sh get-token)
curl -s "https://api.tgoapis.com/web-checkout-apicheckout-santral/orders/detail?orderId={orderId}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-correlationid: $(uuidgen)" \
  -H "pid: $(uuidgen)" \
  -H "sid: $(uuidgen)" | jq
```

**Response includes:** Order details, delivery status steps, ETA, products with prices, delivery address

---

## Google Reviews (Optional)

### get_google_reviews

Fetch Google Maps rating and reviews for a restaurant. **Requires GOOGLE_PLACES_API_KEY env var.**

**Parameters:**
- `restaurantId`, `restaurantName`, `neighborhoodName`, `tgoDistance`, `tgoRating`, `latitude`, `longitude`

This operation uses Google Places API to find the restaurant and compare ratings. Only use if GOOGLE_PLACES_API_KEY is configured.

---

## Error Handling

| Status | Action |
|--------|--------|
| **401 Unauthorized** | Token expired. Run `{baseDir}/scripts/auth.sh clear-token` then retry the operation. |
| **400 Bad Request** | Check parameters. Parse and show the error message from response body. |
| **429 Rate Limited** | OTP verification required. Direct user to complete the action at tgoyemek.com instead. |
| **5xx Server Error** | TGO service temporarily unavailable. Wait a moment and retry once. |
| **3D Secure** | Save HTML content, open browser with `{baseDir}/scripts/3dsecure.sh`, inform user to complete verification. |

Always parse error responses and present the error message clearly to the user.

---

## Guidelines

- **Always authenticate** before making API calls. Use the auth.sh helper.
- **Never expose** raw credentials, JWTs, or tokens to the user.
- **Confirm destructive operations** (clear_basket, place_order) with the user before executing.
- **Check `isClosed`** before suggesting restaurants from search results.
- **Present results** in a clean, readable format rather than raw JSON dumps.
- **Follow the required workflow**: select_address → browse → menu → add to basket → checkout.
- **Handle coordinates correctly**: get_restaurants uses STRING coordinates, add_to_basket uses NUMBER coordinates.
- **If add_to_basket fails**, try clear_basket first then retry.
- **For payment**, always use the Payment API headers (lowercase "bearer", app-name, x-applicationid, etc.).
