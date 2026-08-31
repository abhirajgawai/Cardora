---
name: cardora-frontend
description: >
  Coding standards enforcer for Cardora's Next.js frontend. Use this skill whenever
  writing, editing, or reviewing any TypeScript/React frontend code in this project —
  new pages, new components, new feature modules, API layer additions, type definitions,
  or styling changes. Invoke this skill for any frontend work even if the user doesn't
  ask for a review, so every change meets Cardora's standards before it lands.
---

# Cardora Frontend Standards

Cardora is a Next.js 16 App Router application targeting the **Singapore market**. The
frontend lives at `frontend/src/` and mirrors the backend's feature-based module structure.

---

## Module Structure

Every feature lives under `frontend/src/features/<name>/` and **must** contain:

```
features/<name>/
├── api/
│   └── <name>Api.ts       # All API calls for this feature
├── components/
│   └── <ComponentName>.tsx
├── types/
│   └── index.ts           # All TypeScript types for this feature
└── index.ts               # Barrel: export * from each sub-folder
```

New pages live in `frontend/src/app/<route>/page.tsx`. Every new page **must** also get
an entry in `Sidebar.tsx` (`frontend/src/shared/components/layout/Sidebar.tsx`) —
a page without a nav link is invisible to users.

---

## API Calls — Always Use the Shared Axios Client

**Never use `fetch()` directly.** The shared Axios client at
`@/shared/lib/api/client` handles JWT injection and 401 interception globally.

```typescript
// Correct
import apiClient from '@/shared/lib/api/client';

export const getCards = async (): Promise<CreditCard[]> => {
  const response = await apiClient.get('/cards');
  return response.data;
};

// Wrong — never do this
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/cards`, { ... });
```

The Axios interceptor:
- Injects `Authorization: Bearer <token>` on every request automatically.
- On 401: clears `localStorage.access_token`, saves the current path, and redirects to
  `/login?expired=true`.

Because the interceptor handles 401, **pages and components must not duplicate this logic**.
Keep catch blocks silent for auth errors:

```typescript
// Correct
try {
  const data = await getCards();
  setCards(data);
} catch {
  // 401 handled globally; other errors can be shown in UI if needed
}

// Wrong — race condition, double redirect
} catch (error) {
  if (isAuthError(error)) {
    localStorage.removeItem('access_token');
    router.push('/login');
  }
}
```

---

## Currency Formatting

This app is Singapore-market only. **Always format money with `formatCurrency`** from
`@/shared/lib/utils/formatCurrency`. Never use `.toLocaleString('en-US')`, never use
the `$` symbol manually.

```typescript
import { formatCurrency, formatCurrencyCompact } from '@/shared/lib/utils/formatCurrency';

// In JSX
<span>{formatCurrency(card.creditLimit)}</span>     // → "S$5,000.00"
<span>{formatCurrency(transaction.amount)}</span>   // accepts string or number

// For chart axis ticks where cents clutter the label
<YAxis tickFormatter={(v) => formatCurrencyCompact(v)} />  // → "S$5,000"
```

The backend returns `Numeric(10,2)` fields as **strings** over JSON. `formatCurrency`
accepts both `string` and `number`, so you never need to `parseFloat` before passing it.

---

## Chart Colors

**Never define inline color arrays.** Import from `@/shared/lib/utils/colors`:

```typescript
import { CHART_COLORS, BRAND_COLORS } from '@/shared/lib/utils/colors';

// For pie/bar charts with multiple segments
<Cell key={name} fill={CHART_COLORS[index % CHART_COLORS.length]} />

// For single-series brand-colored lines or bars
<Bar dataKey="amount" fill={BRAND_COLORS.primary} />
<Line stroke={BRAND_COLORS.accent} />
```

`CHART_COLORS` is a 10-colour tuple cycling through the Cardora palette. `BRAND_COLORS`
provides named aliases: `primary`, `accent`, `navy`, `slate`.

---

## No Console Output in Production Code

Pages and components **must not** contain `console.log`, `console.warn`, or
`console.error`. These leak API response shapes to anyone with DevTools open.

```typescript
// Wrong
const data = await getCards();
console.log('cards loaded:', data);  // exposes card data to DevTools

// Correct
const data = await getCards();
setCards(data);
```

The only exception is a catch block for an unexpected, non-auth error where you genuinely
want to surface it to the developer during development — and even then, prefer an
in-UI error state over a console call.

---

## TypeScript Types

**No `any`.** Use `unknown` when the shape is genuinely unknown; narrow it before use.

```typescript
// Wrong
educational_content: { [key: string]: any }

// Correct
educational_content: Record<string, unknown>
```

**No duplicate type definitions.** Types live in `features/<name>/types/index.ts` and are
exported through the feature barrel. Never create a `models/` folder alongside `types/` —
that pattern caused conflicting interfaces in the past.

Pydantic-derived response types follow the naming convention `*Response`; POST input types
are `*Create`; PATCH input types are `*Update`. Mirror these in the frontend types.

---

## Component Conventions

- Use `const` arrow functions — not `function` declarations — for all React components.
- Mark pages and any component using browser APIs (localStorage, window) with
  `'use client';` at the top.
- Prefer `async/await` over `.then()` chains.
- Data fetching belongs in `useEffect` with `async` inner functions — not directly as the
  effect callback.

```typescript
// Correct
'use client';

const CardList = () => {
  const [cards, setCards] = useState<CreditCard[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getCards();
        setCards(data);
      } catch {
        // interceptor handles 401
      }
    };
    load();
  }, []);

  return <ul>{cards.map(c => <li key={c.id}>{c.name}</li>)}</ul>;
};

export default CardList;
```

---

## Error Messages

Use `extractErrorMessage` from `@/shared/lib/utils/errorHandler` to convert Axios errors
into human-readable strings for display. Do **not** call `isAuthError` in pages — that
check belongs in the interceptor.

```typescript
import { extractErrorMessage } from '@/shared/lib/utils/errorHandler';

} catch (error) {
  setError(extractErrorMessage(error));  // shows a localised message in the UI
}
```

---

## Shared Utilities Barrel

`@/shared/lib/utils/index.ts` re-exports everything. Prefer named imports from there:

```typescript
import { formatCurrency, formatCurrencyCompact, CHART_COLORS, BRAND_COLORS, extractErrorMessage } from '@/shared/lib/utils';
```

---

## Pre-Flight Checklist

Run through this before completing any frontend change:

- [ ] New feature? Created `api/`, `components/`, `types/`, `index.ts` under `features/<name>/`
- [ ] New page? Added a nav entry to `Sidebar.tsx`
- [ ] All API calls go through `apiClient` — no raw `fetch()`
- [ ] All money values use `formatCurrency` / `formatCurrencyCompact`
- [ ] All chart colours from `CHART_COLORS` / `BRAND_COLORS` — no inline arrays
- [ ] No `console.log/warn/error` in pages or components
- [ ] No manual 401 handling — catch blocks are silent for auth errors
- [ ] No `any` types — replaced with `unknown` or a proper interface
- [ ] No `models/` folder created — types live in `types/index.ts`
- [ ] `tsc --noEmit` passes with no new errors

Run the type-check from the frontend directory:

```powershell
cd frontend; npx tsc --noEmit
```
