# Cold-start path → offer → trigger playbook

For `new-visitor-cold-start`.

---

## 1. Path patterns → segments

| Pattern | Segment | Offer angle |
|---------|---------|-------------|
| Single PDP long dwell | High intent on SKU | Small % off that SKU or collection |
| Many categories, short views | Explorer | Free ship threshold or catalog % |
| PDP → cart → abandon | Cart friction | Free ship or small fixed off first order |
| Hits shipping/returns page | Risk-averse | Free returns callout + modest % |
| Search same query twice | Search intent | Match query category coupon |

---

## 2. Exit intent

- **Desktop**: mouse leaves top of viewport upward.
- **Mobile**: no true exit intent — use **scroll up past threshold**, **time on site**, or **back-button intercept** (careful with UX/legal).

Always pair with **dismiss** and **don’t show again** cookie where appropriate.

---

## 3. First-order mechanics

- One code per segment **or** dynamic Shopify/Woo auto-apply by URL param after segment detect (if stack allows).
- **Cap** discount to protect margin on high-AOV accidental hits.

---

## 4. Copy tone

- New visitor: welcome + **why this offer** (e.g. "Because you’re browsing [Category]").
- Avoid creep — no "we watched you" language; use "first visit" or "welcome."
