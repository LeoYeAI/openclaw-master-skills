/**
 * Site Configuration
 * 
 * All editable content in one place. Update this file to change
 * text, links, and content throughout the site.
 */

export const siteConfig = {
  // === Meta ===
  name: "Acme AI",
  tagline: "Write better, faster",
  description: "AI-powered writing assistant that adapts to your style",
  url: "https://acme.ai",
  
  // === Navigation ===
  nav: {
    links: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#pricing" },
      { label: "FAQ", href: "#faq" },
      { label: "Blog", href: "/blog" },
    ],
    cta: { label: "Get Started", href: "/signup" },
  },
  
  // === Hero Section ===
  hero: {
    badge: "Now in public beta",
    title: "Your words,\nsupercharged",
    subtitle: "Write 10x faster with AI that learns your style. No more staring at blank pages.",
    cta: {
      primary: { label: "Start Free Trial", href: "/signup" },
      secondary: { label: "Watch Demo", href: "#demo" },
    },
    // Optional: stats under hero
    stats: [
      { value: "50K+", label: "Active users" },
      { value: "2M+", label: "Words written" },
      { value: "4.9", label: "App Store rating" },
    ],
  },
  
  // === Social Proof ===
  socialProof: {
    title: "Trusted by teams at",
    logos: [
      { name: "Vercel", src: "/logos/vercel.svg" },
      { name: "Stripe", src: "/logos/stripe.svg" },
      { name: "Notion", src: "/logos/notion.svg" },
      { name: "Linear", src: "/logos/linear.svg" },
      { name: "Figma", src: "/logos/figma.svg" },
    ],
  },
  
  // === Features Section ===
  features: {
    title: "Everything you need to write better",
    subtitle: "Powerful features that adapt to your workflow",
    items: [
      {
        icon: "Zap",
        title: "Lightning Fast",
        description: "Get suggestions in milliseconds, not seconds. Built on cutting-edge infrastructure.",
      },
      {
        icon: "Brain",
        title: "Learns Your Style",
        description: "The more you write, the better it gets. Your voice, amplified.",
      },
      {
        icon: "Shield",
        title: "Private by Default",
        description: "Your data stays yours. We never train on your content.",
      },
      {
        icon: "Globe",
        title: "Works Everywhere",
        description: "Browser extension, desktop app, and API. Write anywhere.",
      },
      {
        icon: "Sparkles",
        title: "Smart Suggestions",
        description: "Context-aware completions that actually make sense.",
      },
      {
        icon: "Users",
        title: "Team Collaboration",
        description: "Share styles across your team for consistent voice.",
      },
    ],
  },
  
  // === Pricing Section ===
  pricing: {
    title: "Simple, transparent pricing",
    subtitle: "Start free, upgrade when you need more",
    plans: [
      {
        name: "Free",
        price: 0,
        period: "forever",
        description: "Perfect for trying it out",
        features: [
          "500 suggestions/month",
          "Browser extension",
          "Basic style learning",
        ],
        cta: { label: "Get Started", href: "/signup" },
      },
      {
        name: "Pro",
        price: 19,
        period: "/month",
        description: "For serious writers",
        features: [
          "Unlimited suggestions",
          "All platforms",
          "Advanced style learning",
          "Priority support",
          "API access",
        ],
        cta: { label: "Start Free Trial", href: "/signup?plan=pro" },
        popular: true,
      },
      {
        name: "Team",
        price: 49,
        period: "/user/month",
        description: "For growing teams",
        features: [
          "Everything in Pro",
          "Team style sharing",
          "Admin dashboard",
          "SSO & SAML",
          "Dedicated support",
        ],
        cta: { label: "Contact Sales", href: "/contact" },
      },
    ],
  },
  
  // === FAQ Section ===
  faq: {
    title: "Frequently asked questions",
    subtitle: "Can't find what you're looking for? Reach out to our support team.",
    items: [
      {
        question: "How does the AI learn my style?",
        answer: "Our AI analyzes your writing patterns, vocabulary choices, and tone preferences. The more you write, the better it understands your unique voice. All learning happens locally and your data is never shared.",
      },
      {
        question: "Is there a free trial?",
        answer: "Yes! You can try Pro features free for 14 days, no credit card required. After that, you can continue on our free plan or upgrade to Pro.",
      },
      {
        question: "Can I cancel anytime?",
        answer: "Absolutely. No contracts, no cancellation fees. You can cancel your subscription at any time from your account settings.",
      },
      {
        question: "Do you offer discounts for students?",
        answer: "Yes, we offer 50% off for students and educators. Just verify your .edu email to get started.",
      },
      {
        question: "Is my data private?",
        answer: "100%. We use end-to-end encryption, never sell your data, and never train our models on your personal content. Your writing stays yours.",
      },
    ],
  },
  
  // === Testimonials ===
  testimonials: {
    title: "Loved by writers everywhere",
    items: [
      {
        quote: "This completely changed how I write. I'm 3x more productive now.",
        author: "Sarah Chen",
        role: "Content Lead",
        company: "Stripe",
        avatar: "/avatars/sarah.jpg",
      },
      {
        quote: "Finally, an AI that actually sounds like me, not a robot.",
        author: "Marcus Johnson",
        role: "Technical Writer",
        company: "Vercel",
        avatar: "/avatars/marcus.jpg",
      },
      {
        quote: "The best investment I've made for my writing workflow.",
        author: "Emily Park",
        role: "Freelance Writer",
        company: "",
        avatar: "/avatars/emily.jpg",
      },
    ],
  },
  
  // === CTA Section ===
  cta: {
    title: "Ready to write better?",
    subtitle: "Join 50,000+ writers who've upgraded their workflow.",
    button: { label: "Start Free Trial", href: "/signup" },
    note: "No credit card required · Cancel anytime",
  },
  
  // === Footer ===
  footer: {
    links: [
      {
        title: "Product",
        items: [
          { label: "Features", href: "#features" },
          { label: "Pricing", href: "#pricing" },
          { label: "Changelog", href: "/changelog" },
          { label: "Roadmap", href: "/roadmap" },
        ],
      },
      {
        title: "Company",
        items: [
          { label: "About", href: "/about" },
          { label: "Blog", href: "/blog" },
          { label: "Careers", href: "/careers" },
          { label: "Press", href: "/press" },
        ],
      },
      {
        title: "Resources",
        items: [
          { label: "Documentation", href: "/docs" },
          { label: "Help Center", href: "/help" },
          { label: "Community", href: "/community" },
          { label: "API", href: "/api" },
        ],
      },
      {
        title: "Legal",
        items: [
          { label: "Privacy", href: "/privacy" },
          { label: "Terms", href: "/terms" },
          { label: "Security", href: "/security" },
        ],
      },
    ],
    social: [
      { name: "Twitter", href: "https://twitter.com/acme", icon: "Twitter" },
      { name: "GitHub", href: "https://github.com/acme", icon: "Github" },
      { name: "Discord", href: "https://discord.gg/acme", icon: "MessageCircle" },
    ],
    copyright: `© ${new Date().getFullYear()} Acme AI. All rights reserved.`,
  },
}

// === Types ===
export type SiteConfig = typeof siteConfig
