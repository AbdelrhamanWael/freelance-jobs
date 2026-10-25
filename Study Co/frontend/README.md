# StudyCo Frontend

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://study-co-beta.vercel.app/ar)

A modern, high-performance, bilingual landing page built for **StudyCo**, an educational consulting agency dedicated to helping students (especially from Indonesia) achieve their dreams of studying abroad in top universities and institutions.

## 🚀 Features

- **Bilingual Support (RTL & LTR)**: Full support for both Arabic (`ar`) and Indonesian (`id`) languages with dynamic layout adjustments using `i18next` and `next-i18n-router`.
- **Modern UI & Aesthetics**: Built with Tailwind CSS v4 featuring premium design elements like glassmorphism, smooth gradients, and clean typography.
- **Micro-Animations**: Engaging user experience powered by `framer-motion` for scroll animations, hover effects, and page transitions.
- **Responsive Design**: Fully optimized for mobile, tablet, and desktop viewports.
- **Next.js App Router**: Utilizes the latest Next.js 16 app directory structure for optimal performance, routing, and SEO capabilities.
- **React 19 Ready**: Leverages the latest React features and the Babel React Compiler.

## 🛠️ Tech Stack

- **Framework:** [Next.js (v16.3.0)](https://nextjs.org/)
- **Library:** [React (v19.2.8)](https://react.dev/)
- **Styling:** [Tailwind CSS (v4)](https://tailwindcss.com/)
- **Animations:** [Framer Motion](https://www.framer.com/motion/)
- **Internationalization:** `react-i18next`, `next-i18n-router`
- **Icons:** [Lucide React](https://lucide.dev/)
- **Language:** TypeScript

## 📁 Project Structure

```text
frontend/
├── src/
│   ├── app/
│   │   └── [locale]/         # Dynamic route for internationalization
│   │       └── page.tsx      # Main landing page assembling all sections
│   ├── components/           # Reusable UI components & Sections
│   │   ├── HeroSection.tsx
│   │   ├── DestinationsSection.tsx
│   │   ├── ServicesSection.tsx
│   │   ├── TestimonialsSection.tsx
│   │   ├── LanguageSwitcher.tsx
│   │   └── ...
│   ├── locales/              # Translation dictionaries (ar, id)
│   ├── i18n.ts               # i18n configuration
│   └── proxy.ts              # Middleware/proxy configuration
├── package.json
├── tailwind.config.ts        # Tailwind configuration
└── tsconfig.json
```

## 🚦 Getting Started

### Prerequisites
Make sure you have **Node.js** (v20+ recommended) installed on your machine.

### Installation

1. Clone the repository and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the dependencies:
   ```bash
   npm install
   ```
   *(or use `yarn install`, `pnpm install`, `bun install`)*

### Development Server

Run the development server locally:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the result. The application will automatically route you to the default locale based on your browser settings or fallback to the defined default.

### Build for Production

To create an optimized production build:

```bash
npm run build
```

To start the production server after building:

```bash
npm start
```

## 🌐 Internationalization (i18n)

The project handles translations through the `src/locales` directory. 
- To add or modify translations, edit the JSON files within `src/locales/[language]`.
- The layout automatically adapts its `dir` attribute (`rtl` for Arabic, `ltr` for Indonesian), ensuring text alignment, padding, and animations flow naturally.
