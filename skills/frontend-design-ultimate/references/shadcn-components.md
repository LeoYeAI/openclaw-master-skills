# shadcn/ui Component Reference

Quick reference for the 40+ pre-installed shadcn/ui components.

Documentation: https://ui.shadcn.com/docs/components

## Most Used for Landing Pages

| Component | Use Case | Example |
|-----------|----------|---------|
| `Button` | CTAs, actions | Hero buttons, form submits |
| `Badge` | Labels, status | "New", "Popular", "Beta" |
| `Card` | Content containers | Feature cards, pricing tiers |
| `Accordion` | Collapsible content | FAQ sections |
| `Dialog` | Modals | Video players, signup forms |
| `NavigationMenu` | Header navigation | Main nav with dropdowns |
| `Tabs` | Tabbed content | Feature showcases |
| `Carousel` | Sliding content | Testimonials, galleries |

## Full Component List

### Layout & Navigation
- `Accordion` — Collapsible sections
- `Breadcrumb` — Navigation trail
- `Carousel` — Sliding content
- `Collapsible` — Expand/collapse
- `NavigationMenu` — Header nav with dropdowns
- `Pagination` — Page navigation
- `Resizable` — Resizable panels
- `Scroll-Area` — Custom scrollbars
- `Separator` — Visual divider
- `Sheet` — Slide-out panels
- `Sidebar` — App sidebars
- `Tabs` — Tabbed content

### Data Display
- `Avatar` — User images
- `Badge` — Labels and status
- `Card` — Content container
- `HoverCard` — Hover popups
- `Table` — Data tables

### Forms
- `Button` — Actions
- `Checkbox` — Multi-select
- `Combobox` — Searchable select
- `DatePicker` — Date selection
- `Form` — Form wrapper with validation
- `Input` — Text input
- `InputOTP` — One-time password
- `Label` — Form labels
- `RadioGroup` — Single select
- `Select` — Dropdown select
- `Slider` — Range selection
- `Switch` — Toggle
- `Textarea` — Multi-line input
- `Toggle` — Toggle button
- `ToggleGroup` — Button group

### Feedback
- `Alert` — Info messages
- `AlertDialog` — Confirmation dialogs
- `Dialog` — Modal windows
- `Drawer` — Bottom sheets
- `Popover` — Popup content
- `Progress` — Loading bars
- `Skeleton` — Loading placeholders
- `Sonner` — Toast notifications
- `Toast` — Notifications
- `Tooltip` — Hover hints

### Utilities
- `AspectRatio` — Maintain ratios
- `Calendar` — Date display
- `Chart` — Data visualization
- `Command` — Command palette
- `ContextMenu` — Right-click menus
- `DropdownMenu` — Dropdown menus
- `Menubar` — App menubars

---

## Code Examples

### Hero with Badge and Buttons

```tsx
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

function Hero() {
  return (
    <section className="py-24 text-center">
      <Badge variant="secondary" className="mb-4">
        Now in beta
      </Badge>
      
      <h1 className="text-5xl font-bold mb-6">
        Your headline here
      </h1>
      
      <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
        Subheadline with more details about your product.
      </p>
      
      <div className="flex gap-4 justify-center">
        <Button size="lg">Get Started</Button>
        <Button size="lg" variant="outline">Learn More</Button>
      </div>
    </section>
  )
}
```

### Feature Cards

```tsx
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Zap, Shield, Globe } from "lucide-react"

const features = [
  { icon: Zap, title: "Fast", description: "Lightning quick performance" },
  { icon: Shield, title: "Secure", description: "Enterprise-grade security" },
  { icon: Globe, title: "Global", description: "CDN in 200+ locations" },
]

function Features() {
  return (
    <section className="py-24">
      <div className="grid md:grid-cols-3 gap-8">
        {features.map((f) => (
          <Card key={f.title}>
            <CardHeader>
              <f.icon className="h-10 w-10 mb-4 text-primary" />
              <CardTitle>{f.title}</CardTitle>
              <CardDescription>{f.description}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>
    </section>
  )
}
```

### Pricing Table

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Check } from "lucide-react"

const plans = [
  { name: "Free", price: 0, features: ["5 projects", "Basic support"] },
  { name: "Pro", price: 19, features: ["Unlimited projects", "Priority support", "API access"], popular: true },
  { name: "Team", price: 49, features: ["Everything in Pro", "Team features", "SSO"] },
]

function Pricing() {
  return (
    <section className="py-24">
      <div className="grid md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.popular ? "border-primary" : ""}>
            <CardHeader>
              {plan.popular && <Badge className="w-fit mb-2">Most Popular</Badge>}
              <CardTitle>{plan.name}</CardTitle>
              <CardDescription>
                <span className="text-4xl font-bold">${plan.price}</span>
                <span className="text-muted-foreground">/month</span>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    {f}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
                Get Started
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </section>
  )
}
```

### FAQ Accordion

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
  { q: "How does it work?", a: "Our platform uses AI to..." },
  { q: "Is there a free trial?", a: "Yes, you get 14 days free..." },
  { q: "Can I cancel anytime?", a: "Absolutely, no questions asked..." },
]

function FAQ() {
  return (
    <section className="py-24 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-12">
        Frequently Asked Questions
      </h2>
      
      <Accordion type="single" collapsible>
        {faqs.map((faq, i) => (
          <AccordionItem key={i} value={`item-${i}`}>
            <AccordionTrigger>{faq.q}</AccordionTrigger>
            <AccordionContent>{faq.a}</AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}
```

### Mobile Navigation with Sheet

```tsx
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"

function MobileNav() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-6 w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right">
        <nav className="flex flex-col gap-4 mt-8">
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
          <Button className="mt-4">Get Started</Button>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
```

### Video Modal with Dialog

```tsx
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Play } from "lucide-react"

function VideoModal() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="lg">
          <Play className="mr-2 h-4 w-4" />
          Watch Demo
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl p-0">
        <div className="aspect-video">
          <iframe
            src="https://www.youtube.com/embed/..."
            className="w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

---

## Styling Tips

### Customizing Colors

shadcn uses CSS variables. Override in your globals.css:

```css
:root {
  --primary: 220 90% 56%;
  --primary-foreground: 0 0% 100%;
  --accent: 25 95% 53%;
}

.dark {
  --primary: 220 90% 66%;
}
```

### Extending Variants

```tsx
// components/ui/button.tsx
const buttonVariants = cva(
  "...",
  {
    variants: {
      variant: {
        default: "...",
        // Add custom variant
        gradient: "bg-gradient-to-r from-primary to-accent text-white hover:opacity-90",
      },
    },
  }
)
```

### Using with Tailwind

All components accept `className` for additional styling:

```tsx
<Button className="rounded-full px-8">
  Pill Button
</Button>

<Card className="bg-gradient-to-br from-primary/10 to-accent/10">
  Gradient Card
</Card>
```
