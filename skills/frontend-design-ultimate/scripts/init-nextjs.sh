#!/bin/bash
# Initialize a Next.js + TypeScript + Tailwind + shadcn/ui project
# Usage: bash scripts/init-nextjs.sh <project-name>

set -e

PROJECT_NAME="${1:-my-site}"

# Check Node version
NODE_VERSION=$(node -v 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Error: Node.js 18+ is required. Current: $(node -v 2>/dev/null || echo 'not installed')"
  exit 1
fi

echo "🚀 Creating Next.js project: $PROJECT_NAME"

# Create Next.js project with all options
npx create-next-app@latest "$PROJECT_NAME" \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"

cd "$PROJECT_NAME"

# Create .nvmrc for Node version
echo "18" > .nvmrc

echo "📦 Installing additional dependencies..."

# Install animation library
npm install framer-motion

# Install shadcn/ui
echo "📦 Initializing shadcn/ui..."
npx shadcn@latest init -y -d

# Install common components
echo "📦 Installing common components..."
npx shadcn@latest add button badge card accordion dialog navigation-menu tabs sheet separator avatar alert -y || {
  echo "⚠️ Warning: Some shadcn components may not have installed. Run 'npx shadcn@latest add [name]' manually."
}

# Install lucide icons
npm install lucide-react

# Create config directory
mkdir -p src/config

# Create site config
cat > src/config/site.ts << 'EOF'
export const siteConfig = {
  name: "My Site",
  tagline: "Build something amazing",
  description: "A modern website built with Next.js, Tailwind, and shadcn/ui",
  url: "https://mysite.com",
  
  nav: {
    links: [
      { label: "Features", href: "#features" },
      { label: "Pricing", href: "#pricing" },
      { label: "FAQ", href: "#faq" },
    ],
    cta: { label: "Get Started", href: "/signup" },
  },
  
  // Add more sections as needed
}

export type SiteConfig = typeof siteConfig
EOF

# Update globals.css with custom animations
cat >> src/app/globals.css << 'EOF'

/* Custom animations */
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}

/* Staggered animations */
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }
.stagger-5 { animation-delay: 0.5s; }
EOF

# Create a basic page with animation example
cat > src/app/page.tsx << 'EOF'
import { Button } from "@/components/ui/button"
import { siteConfig } from "@/config/site"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-5xl font-bold mb-4 animate-slide-up">
        {siteConfig.name}
      </h1>
      <p className="text-xl text-muted-foreground mb-8 animate-slide-up stagger-1">
        {siteConfig.tagline}
      </p>
      <Button size="lg" className="animate-slide-up stagger-2">
        Get Started
      </Button>
    </main>
  )
}
EOF

echo ""
echo "✅ Next.js project created successfully!"
echo ""
echo "Installed:"
echo "  ✓ Next.js 14+ with App Router"
echo "  ✓ TypeScript + Tailwind CSS"
echo "  ✓ shadcn/ui with 10 components"
echo "  ✓ Framer Motion for animations"
echo "  ✓ Site config pattern"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  npm run dev"
echo ""
echo "Add more components:"
echo "  npx shadcn@latest add [component-name]"
echo "  npx shadcn@latest add --all  # Install all components"
echo ""
echo "Deploy to Vercel:"
echo "  vercel"
echo ""
