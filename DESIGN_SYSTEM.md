# Cardora Design System

**"Quietly Powerful"** - Simple, elegant, powerful, with subtle delightful details.

Inspired by: Linear, Vercel, Stripe, Raycast, Apple

---

## 🎨 Design Philosophy

### Core Principles
1. **Clarity Over Cleverness** - Users should understand instantly
2. **Speed Matters** - Every interaction feels instant
3. **Details Delight** - Micro-interactions show we care
4. **Consistency Builds Trust** - Predictable patterns throughout
5. **Accessible by Default** - Works for everyone, everywhere

### Visual Language
- **Minimalist** - Remove until you can't remove anymore
- **Spacious** - Generous whitespace, room to breathe
- **Purposeful** - Every element has a reason
- **Modern** - Contemporary but timeless
- **Professional** - Serious about finance, friendly in tone

---

## 🎨 Color Palette

### Primary Colors
```css
/* Sky Blue - Trust, Clarity, Financial */
--primary-50:  #f0f9ff;
--primary-100: #e0f2fe;
--primary-200: #bae6fd;
--primary-300: #7dd3fc;
--primary-400: #38bdf8;
--primary-500: #0ea5e9;  /* Main primary */
--primary-600: #0284c7;
--primary-700: #0369a1;
--primary-800: #075985;
--primary-900: #0c4a6e;
```

### Secondary Colors
```css
/* Violet - Premium, Elegant, AI-powered */
--secondary-50:  #faf5ff;
--secondary-100: #f3e8ff;
--secondary-200: #e9d5ff;
--secondary-300: #d8b4fe;
--secondary-400: #c084fc;
--secondary-500: #a855f7;  /* Main secondary */
--secondary-600: #9333ea;
--secondary-700: #7e22ce;
--secondary-800: #6b21a8;
--secondary-900: #581c87;
```

### Accent Colors
```css
/* Success - Emerald */
--success: #10b981;
--success-light: #34d399;
--success-dark: #059669;

/* Warning - Amber */
--warning: #f59e0b;
--warning-light: #fbbf24;
--warning-dark: #d97706;

/* Error - Rose */
--error: #ef4444;
--error-light: #f87171;
--error-dark: #dc2626;

/* Info - Sky */
--info: #0ea5e9;
--info-light: #38bdf8;
--info-dark: #0284c7;
```

### Category Colors (Transaction Categories)
```css
--category-groceries:      #4CAF50;  /* Green */
--category-dining:         #FF6B6B;  /* Coral Red */
--category-transport:      #2196F3;  /* Blue */
--category-shopping:       #FF9800;  /* Orange */
--category-bills:          #9C27B0;  /* Purple */
--category-entertainment:  #00BCD4;  /* Cyan */
--category-healthcare:     #E91E63;  /* Pink */
--category-travel:         #3F51B5;  /* Indigo */
--category-education:      #795548;  /* Brown */
--category-others:         #9E9E9E;  /* Gray */
```

### Neutral Colors (Warm Gray)
```css
/* Background & Surface */
--background:    #fafafa;  /* Soft white, not harsh */
--surface:       #ffffff;  /* Pure white for cards */
--surface-hover: #f9fafb;  /* Subtle hover state */

/* Borders */
--border-light:  #f3f4f6;  /* Barely visible */
--border:        #e5e7eb;  /* Standard border */
--border-medium: #d1d5db;  /* Emphasized border */
--border-dark:   #9ca3af;  /* Strong border */

/* Text */
--text-primary:   #1f2937;  /* Almost black (easier on eyes) */
--text-secondary: #6b7280;  /* Medium gray */
--text-tertiary:  #9ca3af;  /* Light gray */
--text-disabled:  #d1d5db;  /* Disabled state */
--text-inverse:   #ffffff;  /* White text on dark */
```

### Gradients
```css
/* Hero Sections */
--gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-hero-2: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);

/* Card Hover Effects */
--gradient-card: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%);

/* Button Hover */
--gradient-button: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);

/* Background Mesh (Ambient) */
--gradient-mesh: radial-gradient(at 40% 20%, #e0f2fe 0px, transparent 50%),
                 radial-gradient(at 80% 0%, #f3e8ff 0px, transparent 50%),
                 radial-gradient(at 0% 50%, #dbeafe 0px, transparent 50%);
```

---

## 📝 Typography

### Font Families
```css
/* Body Text */
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Headings (Alternative: Cal Sans, Satoshi) */
--font-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace (Code, Numbers) */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Type Scale (Fluid, Responsive)
```css
/* Desktop Sizes */
--text-xs:   0.75rem;   /* 12px - Captions, labels */
--text-sm:   0.875rem;  /* 14px - Small body text */
--text-base: 1rem;      /* 16px - Body text */
--text-lg:   1.125rem;  /* 18px - Large body */
--text-xl:   1.25rem;   /* 20px - Small headings */
--text-2xl:  1.5rem;    /* 24px - H3 */
--text-3xl:  1.875rem;  /* 30px - H2 */
--text-4xl:  2.25rem;   /* 36px - H1 */
--text-5xl:  3rem;      /* 48px - Hero */
--text-6xl:  3.75rem;   /* 60px - Large hero */

/* Font Weights */
--font-light:     300;
--font-normal:    400;
--font-medium:    500;
--font-semibold:  600;
--font-bold:      700;
--font-extrabold: 800;

/* Line Heights */
--leading-tight:  1.25;   /* Headings */
--leading-normal: 1.5;    /* Body text */
--leading-relaxed: 1.75;  /* Long-form content */

/* Letter Spacing */
--tracking-tight:  -0.025em;  /* Large headings */
--tracking-normal: 0;         /* Body text */
--tracking-wide:   0.025em;   /* Small caps, labels */
```

### Typography Usage
```css
/* H1 - Page Titles */
font-size: var(--text-4xl);
font-weight: var(--font-bold);
line-height: var(--leading-tight);
letter-spacing: var(--tracking-tight);

/* H2 - Section Titles */
font-size: var(--text-3xl);
font-weight: var(--font-bold);
line-height: var(--leading-tight);

/* H3 - Subsection Titles */
font-size: var(--text-2xl);
font-weight: var(--font-semibold);
line-height: var(--leading-tight);

/* Body - Default Text */
font-size: var(--text-base);
font-weight: var(--font-normal);
line-height: var(--leading-normal);

/* Small - Captions, Labels */
font-size: var(--text-sm);
font-weight: var(--font-medium);
color: var(--text-secondary);
```

---

## 📏 Spacing System

### 8px Grid System
```css
--space-0:   0;
--space-1:   0.25rem;  /* 4px  - Tight spacing */
--space-2:   0.5rem;   /* 8px  - Base unit */
--space-3:   0.75rem;  /* 12px - Small spacing */
--space-4:   1rem;     /* 16px - Medium spacing */
--space-5:   1.25rem;  /* 20px - Comfortable */
--space-6:   1.5rem;   /* 24px - Component padding */
--space-8:   2rem;     /* 32px - Section spacing */
--space-10:  2.5rem;   /* 40px - Large gaps */
--space-12:  3rem;     /* 48px - Page margins */
--space-16:  4rem;     /* 64px - Hero spacing */
--space-20:  5rem;     /* 80px - Extra large */
--space-24:  6rem;     /* 96px - Massive spacing */
```

### Component Spacing
```css
/* Card Padding */
padding: var(--space-6);  /* 24px */

/* Section Spacing */
margin-bottom: var(--space-8);  /* 32px */

/* Grid Gaps */
gap: var(--space-6);  /* 24px */

/* Button Padding */
padding: var(--space-3) var(--space-6);  /* 12px 24px */

/* Input Padding */
padding: var(--space-3) var(--space-4);  /* 12px 16px */
```

---

## 🔲 Border Radius

```css
--radius-none: 0;
--radius-sm:   0.25rem;  /* 4px  - Badges, tags */
--radius-base: 0.5rem;   /* 8px  - Buttons, inputs */
--radius-md:   0.75rem;  /* 12px - Cards */
--radius-lg:   1rem;     /* 16px - Modals */
--radius-xl:   1.5rem;   /* 24px - Large cards */
--radius-full: 9999px;   /* Circular - Pills, avatars */
```

---

## 🌑 Shadows & Elevation

```css
/* Subtle Shadows */
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

/* Colored Shadows (for emphasis) */
--shadow-primary: 0 10px 25px -5px rgb(14 165 233 / 0.3);
--shadow-secondary: 0 10px 25px -5px rgb(168 85 247 / 0.3);

/* Inner Shadow (for inputs) */
--shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
```

### Elevation Hierarchy
```
Level 0: Base (no shadow)
Level 1: Inputs, small cards (shadow-sm)
Level 2: Cards, dropdowns (shadow-md)
Level 3: Modals, popovers (shadow-lg)
Level 4: Dialogs, tooltips (shadow-xl)
```

---

## ✨ Animation & Motion

### Timing Functions
```css
/* Easing Curves */
--ease-linear:     linear;
--ease-in:         cubic-bezier(0.4, 0, 1, 1);
--ease-out:        cubic-bezier(0, 0, 0.2, 1);      /* Most common */
--ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce:     cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-elastic:    cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

### Duration
```css
/* Transitions */
--duration-fast:    100ms;  /* Instant feedback */
--duration-normal:  200ms;  /* Standard transitions */
--duration-slow:    300ms;  /* Emphasized transitions */
--duration-slower:  500ms;  /* Complex animations */

/* Page Transitions */
--duration-page:    200ms;
```

### Common Transitions
```css
/* Hover States */
transition: all 200ms cubic-bezier(0, 0, 0.2, 1);

/* Button Press */
transition: transform 100ms cubic-bezier(0, 0, 0.2, 1);

/* Card Lift */
transition: transform 200ms cubic-bezier(0, 0, 0.2, 1),
            box-shadow 200ms cubic-bezier(0, 0, 0.2, 1);

/* Color Fade */
transition: background-color 200ms cubic-bezier(0, 0, 0.2, 1),
            color 200ms cubic-bezier(0, 0, 0.2, 1);
```

### Framer Motion Variants
```javascript
// Fade In
const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.2 }
};

// Slide Up
const slideUp = {
  initial: { y: 20, opacity: 0 },
  animate: { y: 0, opacity: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
};

// Stagger Children
const staggerContainer = {
  animate: {
    transition: { staggerChildren: 0.1 }
  }
};

// Card Hover
const cardHover = {
  whileHover: {
    y: -4,
    boxShadow: "0 10px 25px -5px rgb(0 0 0 / 0.15)",
    transition: { duration: 0.2 }
  }
};
```

---

## 🧩 Component Patterns

### Buttons

#### Primary Button
```css
background: var(--primary-500);
color: white;
padding: 12px 24px;
border-radius: var(--radius-base);
font-weight: var(--font-semibold);
box-shadow: var(--shadow-sm);
transition: all 200ms ease-out;

&:hover {
  background: var(--primary-600);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

&:active {
  transform: translateY(0);
}
```

#### Secondary Button
```css
background: transparent;
color: var(--primary-600);
border: 1.5px solid var(--primary-500);
padding: 12px 24px;
border-radius: var(--radius-base);
font-weight: var(--font-semibold);

&:hover {
  background: var(--primary-50);
  border-color: var(--primary-600);
}
```

### Cards

#### Base Card
```css
background: white;
padding: var(--space-6);
border-radius: var(--radius-md);
border: 1px solid var(--border);
box-shadow: var(--shadow-sm);
transition: all 200ms ease-out;

&:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--primary-200);
}
```

#### Stat Card
```css
background: white;
padding: var(--space-6);
border-radius: var(--radius-md);
border: 1px solid var(--border);
box-shadow: var(--shadow-sm);

/* Icon container with gradient */
.icon-container {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-base);
  background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Large number */
.value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin-top: var(--space-4);
}

/* Label */
.label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-2);
}
```

### Inputs

#### Text Input
```css
width: 100%;
padding: 12px 16px;
border: 1.5px solid var(--border);
border-radius: var(--radius-base);
background: white;
font-size: var(--text-base);
color: var(--text-primary);
transition: all 200ms ease-out;

&:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

&:hover {
  border-color: var(--border-medium);
}

/* With icon */
&.with-icon {
  padding-left: 44px;
}
```

### Badges

```css
/* Base Badge */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Success Badge */
.badge-success {
  background: #d1fae5;
  color: #065f46;
}

/* Warning Badge */
.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

/* Error Badge */
.badge-error {
  background: #fee2e2;
  color: #991b1b;
}
```

---

## 📱 Responsive Design

### Breakpoints
```css
--screen-sm:  640px;   /* Mobile landscape */
--screen-md:  768px;   /* Tablet */
--screen-lg:  1024px;  /* Desktop */
--screen-xl:  1280px;  /* Large desktop */
--screen-2xl: 1536px;  /* Extra large */
```

### Mobile-First Approach
```css
/* Base: Mobile (< 640px) */
.container {
  padding: var(--space-4);
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: var(--space-6);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: var(--space-8);
  }
}
```

---

## ♿ Accessibility

### Focus States
```css
/* Visible focus ring */
*:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* Remove default outline */
*:focus {
  outline: none;
}
```

### Color Contrast
- Text on white: Minimum 4.5:1 ratio (WCAG AA)
- Large text (18px+): Minimum 3:1 ratio
- Interactive elements: Minimum 3:1 ratio

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Tab order must be logical
- Skip links for screen readers

---

## 🎯 Quality Benchmarks

### Performance
- ✅ Lighthouse Score: 95+ (all categories)
- ✅ 60fps animations (no jank)
- ✅ < 1s initial page load
- ✅ No layout shift (CLS < 0.1)

### Design
- ✅ Consistent 8px spacing grid
- ✅ WCAG AA color contrast
- ✅ No orphaned elements
- ✅ Proper visual hierarchy

### Code
- ✅ Reusable components
- ✅ DRY principles
- ✅ Type-safe (TypeScript)
- ✅ Well-documented

---

## 📚 References

### Inspiration Sources
- [Linear Design System](https://linear.app)
- [Vercel Design](https://vercel.com/design)
- [Stripe Design](https://stripe.com/docs/design)
- [Raycast Design](https://raycast.com)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/)

### Tools & Resources
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Recharts](https://recharts.org)
- [Lucide Icons](https://lucide.dev)

---

**Last Updated:** 2025-10-24
**Version:** 1.0.0
