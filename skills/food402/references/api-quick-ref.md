# TGO Yemek API Quick Reference

## Base URLs
- **Main API:** `https://api.tgoapis.com`
- **Payment API:** `https://payment.tgoapps.com`

## Authentication
- Login: `POST https://tgoyemek.com/api/auth/login`
- CSRF first: `GET https://tgoyemek.com/api/auth/csrf`
- Token cookie: `tgo-token`

## Main API Headers
```
Authorization: Bearer {token}
x-correlationid: {uuid}
pid: {uuid}
sid: {uuid}
```

## Payment API Headers
```
Authorization: bearer {token}  # lowercase 'bearer'
app-name: TrendyolGo
x-applicationid: 1
x-channelid: 4
x-storefrontid: 1
```

## Endpoints Reference

### Address Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/web-user-apimemberaddress-santral/addresses` | GET | List addresses |
| `/web-user-apimemberaddress-santral/addresses` | POST | Add address |
| `/web-user-apimemberaddress-santral/cities` | GET | List cities |
| `/web-user-apimemberaddress-santral/cities/{id}/districts` | GET | List districts |
| `/web-user-apimemberaddress-santral/districts/{id}/neighborhoods` | GET | List neighborhoods |

### Cart
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/web-checkout-apicheckout-santral/shipping` | POST | Set address |
| `/web-checkout-apicheckout-santral/carts` | GET | Get cart |
| `/web-checkout-apicheckout-santral/carts` | DELETE | Clear cart |
| `/web-checkout-apicheckout-santral/carts/items` | POST | Add items |
| `/web-checkout-apicheckout-santral/carts/items/{id}` | DELETE | Remove item |
| `/web-checkout-apicheckout-santral/carts/customerNote` | PUT | Set note |
| `/web-checkout-apicheckout-santral/carts?cartContext=payment` | GET | Checkout ready |

### Restaurants
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/web-discovery-apidiscovery-santral/restaurants/filters` | GET | List restaurants |
| `/web-restaurant-apirestaurant-santral/restaurants/in/search` | GET | Search |
| `/web-restaurant-apirestaurant-santral/restaurants/{id}` | GET | Get menu |
| `/web-restaurant-apirestaurant-santral/restaurants/{id}/products/{pid}` | POST | Product details |
| `/web-discovery-apidiscovery-santral/recommendation/product` | POST | Recommendations |

### Orders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/web-checkout-apicheckout-santral/orders` | GET | Order history |
| `/web-checkout-apicheckout-santral/orders/detail` | GET | Order detail |

### Payment (payment.tgoapps.com)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v2/cards/` | GET | Saved cards |
| `/v3/payment/options` | POST | Select payment |
| `/v2/payment/pay` | POST | Place order |

## Common Query Parameters

### get_restaurants
- `openRestaurants=true`
- `latitude`, `longitude` (required)
- `pageSize=50`, `page=1`
- `sortType`: RESTAURANT_SCORE, RESTAURANT_DISTANCE (omit for RECOMMENDED)
- `minBasketPrice=400` (optional filter)

### search_restaurants
- `searchQuery` (required)
- `latitude`, `longitude` (required)
- `pageSize=50`, `page=1`

## add_to_basket Body Structure
```json
{
  "storeId": 12345,
  "items": [{
    "productId": 67890,
    "quantity": 1,
    "modifierProducts": [{
      "productId": 111,
      "modifierGroupId": 222,
      "modifierProducts": [],
      "ingredientOptions": {"excludes": [], "includes": []}
    }],
    "ingredientOptions": {
      "excludes": [{"id": 333}],
      "includes": []
    }
  }],
  "latitude": 41.0082,
  "longitude": 28.9784,
  "isFlashSale": false,
  "storePickup": false
}
```
**Note:** latitude/longitude are NUMBERS here, not strings.

## place_order Flow
1. GET `/carts?cartContext=payment` (Main API)
2. POST `/v3/payment/options` (Payment API)
3. POST `/v2/payment/pay` (Payment API)

If response has `json.content` or `htmlContent` → 3D Secure required → open in browser.
