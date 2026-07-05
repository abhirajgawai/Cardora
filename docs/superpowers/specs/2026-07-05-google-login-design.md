# Google Login for Customers — Design

## Summary

Add "Sign in with Google" as an additional authentication method alongside the existing email/password flow, using Google Identity Services (GIS) ID-token verification. Cardora only needs to confirm identity (a verified email) — not ongoing access to Google APIs — so no client secret, redirect callback, or token refresh handling is needed.

## Decisions

- **Account linking:** if a Google sign-in's email matches an existing email/password account, auto-link the Google identity to that account (Google has already verified the email, so this is safe). The user can then sign in either way.
- **No password-fallback UI in this pass:** Google-only accounts have no password and won't get a "set a password" option yet. That's an explicit follow-up feature, not part of this work.
- **Scope:** basic `openid`/`email`/`profile` claims only.

## Backend

**Migration (new Alembic revision):**
- `users.google_id` — new `String(255)`, nullable, unique, indexed (Google's `sub` claim)
- `users.hashed_password` — becomes nullable (Google-only signups never set one)

**New dependency:** `google-auth` (Python) — add to `requirements.txt`. Used for `google.oauth2.id_token.verify_oauth2_token`.

**New env var:** `GOOGLE_CLIENT_ID=302204730669-7ut65trrtl5cl9tdc4lkmrspjs74e960.apps.googleusercontent.com` (backend `.env`) — used to validate the token's `aud` claim.

**New schema** (`app/features/auth/schemas.py`): `GoogleLoginRequest { id_token: str }`.

**New endpoint:** `POST /auth/google` in `app/features/auth/router.py`:
1. Verify the ID token via `google-auth`. Reject 401 on bad signature/expired/wrong `aud`.
2. Reject 401 if the token's `email_verified` claim is `false`.
3. Look up `User` by `google_id`. If found → issue JWT.
4. Else look up by `email`. If found → set `google_id` on that row (auto-link) → issue JWT.
5. Else create a new `User`: `email`, `google_id`, `full_name` from the `name` claim, `hashed_password=None`, `is_verified=True`, default `timezone` → issue JWT.
6. Reject 403 if the resolved user has `is_active=False` (same behavior as `/auth/login`).
7. Response: same `Token` schema as `/auth/login`.

## Frontend

**New dependency:** `@react-oauth/google` — add to `frontend/package.json`.

**New env var:** `NEXT_PUBLIC_GOOGLE_CLIENT_ID=302204730669-7ut65trrtl5cl9tdc4lkmrspjs74e960.apps.googleusercontent.com` (`frontend/.env.local`).

**New shared component:** `frontend/src/features/auth/components/GoogleSignInButton.tsx` — wraps `<GoogleLogin>` from `@react-oauth/google`. On `onSuccess`, calls a new `googleLogin(idToken)` function, then performs the same post-login steps the existing login flow does: store the token, check `localStorage.redirectAfterLogin`, else push `/dashboard`. On `onError`, shows "Google sign-in failed, please try again."

**API layer:** `authApi.ts` gets `googleLogin(idToken: string): Promise<Token>` → `POST /auth/google` via the shared Axios client (`@/shared/lib/api/client`) — no raw `fetch()`.

**Wiring:** the app root layout is wrapped in `<GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}>`. The existing decorative Google button is replaced by `<GoogleSignInButton />` on both `/login/page.tsx` and `/register/page.tsx`.

## Data Flow

1. User clicks the Google button on `/login` or `/register`.
2. Google's popup handles auth, returns an ID token to `onSuccess`.
3. Frontend calls `POST /auth/google { id_token }`.
4. Backend verifies → finds/links/creates user → returns `{ access_token, token_type }`.
5. Frontend stores the token exactly like normal login, redirects to `/dashboard` (or saved `redirectAfterLogin`).

## Error Handling

All errors surface via the existing inline red error box on the login/register forms:
- Bad/expired/tampered token → backend 401 "Invalid Google token"
- Email not verified by Google → backend 401 "Google account email not verified"
- Existing account `is_active=False` → backend 403, same message as regular login
- Google popup closed/blocked/network failure client-side → "Google sign-in failed, please try again"

## Testing

- **Backend:** `tests/test_google_login.py` — monkeypatch the token-verification call (no real network call to Google). Cover: new-user creation, auto-link to existing email/password account, repeat login via existing `google_id`, rejected on bad token, rejected on unverified email, rejected on inactive account.
- **Frontend:** not automatable (requires a real Google account interaction) — verified manually in the browser: click through both `/login` and `/register`, confirm redirect to dashboard, confirm the returned JWT works against protected endpoints.

## Deployment Notes (not part of this implementation pass, but must not be forgotten)

1. Add the production domain as an Authorized JavaScript origin on the same OAuth Client in Google Cloud Console (`https://` required — `http://` only works for `localhost`).
2. Flip **Audience → Publishing status** from **Testing** to **In production** in Google Auth Platform before real customers can use it (no manual Google review needed since we only request basic `openid`/`email`/`profile` scopes).
3. Set `GOOGLE_CLIENT_ID` / `NEXT_PUBLIC_GOOGLE_CLIENT_ID` in whatever prod environment actually runs the backend/frontend.
4. Add the prod frontend origin to the CORS allowlist in `app/main.py` (currently hardcoded to `localhost:3000/3001`) — otherwise prod API calls fail regardless of auth method.

## Out of Scope

- "Set a password" flow for Google-only accounts
- Full OAuth Authorization Code / PKCE flow (not needed since we don't call Google APIs on the user's behalf)
- Any other social login providers
