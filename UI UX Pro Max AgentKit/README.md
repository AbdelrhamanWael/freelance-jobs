# BU3D.ai — Premium 3D AI SaaS Website

> حوّل كلماتك إلى عوالم ثلاثية الأبعاد | Transform Words into 3D Worlds

A premium, cinematic AI SaaS platform website built with React, React Three Fiber, GSAP, and Tailwind CSS v4. Features interactive WebGL animations, Glassmorphism UI, and a conversational 3D generation workspace.

---

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# → http://localhost:5173

# Build for production
npm run build
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + Vite 8 |
| 3D Graphics | React Three Fiber + Three.js + @react-three/drei |
| Animations | GSAP + ScrollTrigger |
| Styling | Tailwind CSS v4 (custom design tokens) |
| Icons | Lucide React |
| Supplementary | Framer Motion |

---

## 📁 Project Structure

```
src/
├── components/
│   ├── LogoJourney.jsx      # 3D scroll-animated logo
│   ├── ModelCard3D.jsx      # Inline R3F preview cards
│   ├── ChatWorkspace.jsx    # Conversational generation UI
│   ├── Viewer3D.jsx         # Edge-to-edge 3D modal
│   ├── Features.jsx         # Bento grid "How It Works"
│   ├── Pricing.jsx          # 3D tilt pricing cards
│   ├── Footer.jsx           # Professional footer
│   └── Sidebar.jsx          # History panel
├── App.jsx                  # Main shell + Navbar + Hero
├── index.css                # Design system + glassmorphism utilities
└── main.jsx                 # React entry point
public/
└── saudi-business-center.svg
```

---

## ✨ Key Features

### 🎬 Hero & 3D Logo Journey
- Compound 3D logo: distorted sphere nucleus + 3 orbital rings (violet, indigo, pink)
- Scroll-driven animation: logo starts centered in hero, "falls" to corner as user scrolls
- Cubic ease-out falling physics for natural motion
- GSAP text reveal on hero headline, badge, subtext, and CTAs

### 💬 Conversational Workspace
- ChatGPT-style input with textarea auto-grow
- Suggestion chips for quick prompts
- Triple-ring spinner + progress bar during AI generation
- 4 result cards each with an inline React Three Fiber 3D preview canvas
- GSAP stagger card entry animation

### 🔮 Edge-to-Edge 3D Viewer
- Full-screen modal (no scrollbars, no borders)
- Studio 3-point lighting (key + fill + rim)
- ACESFilmic tone mapping for cinematic look
- OrbitControls: auto-rotate, drag to rotate, scroll to zoom
- Shape switcher (Box, Sphere, Torus, Icosahedron, Cone)
- Download dropdown: STL, GLB, OBJ, FBX
- Floating glassmorphism control panel
- GSAP entry (scale + fade) and exit animations
- Toast notification system

### 💎 Pricing
- 3 tiers: Starter $19 / Creator $39 / Pro $69
- JS `mousemove` 3D perspective tilt per card
- Cursor-following radial glow
- GSAP scroll reveal
- Detailed feature lists with colored checkmarks

### 🔗 Footer
- BU3D.ai branding + tagline + WhatsApp link
- Quick navigation links (Terms, Refund Policy, About)
- Freelance Document badge (767983613-FL)
- Saudi Business Center logo
- Inline SVG QR code pointing to `bu3d.ai/verify`

---

## 🎨 Design System

```css
/* Core tokens in src/index.css */
--bg:           #050506   /* Near-black cinematic */
--primary:      #7C3AED   /* Violet */
--secondary:    #6366F1   /* Indigo */
--accent:       #EC4899   /* Pink */
--neon:         #00D4FF   /* Cyan */
--fg:           #EDEDEF   /* Warm white */
--muted-fg:     #8A8F98   /* Muted text */
```

### Utility Classes
- `.glass` — Standard glassmorphism card
- `.glass-panel` — Premium glass (stronger blur)
- `.glass-control` — Modal control panel glass
- `.glow-primary`, `.glow-accent`, `.glow-neon` — Glow shadows
- `.dot-grid` — Radial dot background pattern
- `.blob` — Animated ambient blob
- `.shimmer` — Loading shimmer animation

---

## 🌐 Browser Support

Modern browsers with WebGL support (Chrome 90+, Firefox 88+, Safari 15+, Edge 90+)

---

## 📞 Contact

- WhatsApp: [+966511466121](https://wa.me/966511466121)
- Email: support@bu3d.ai
- Verify: [bu3d.ai/verify](https://bu3d.ai/verify)

---

*جميع الحقوق محفوظة © 2026 — BU3D.ai*  
*مصنوع بـ ♥ في المملكة العربية السعودية*
