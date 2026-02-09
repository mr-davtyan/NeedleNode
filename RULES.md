# Cursor Rules

This file defines strict constraints, assumptions, and behavioral rules that Cursor must follow when generating code for this project.

## General Principles

* Follow the scope defined in `project.md`
* Prefer simplicity, clarity, and maintainability over premature optimization
* Do not introduce features that are not explicitly requested
* Design all components to be extensible, but do not implement future features unless instructed

## Feature Constraints

### Payments

* **Do NOT implement online payments**
* Do NOT integrate payment gateways (Stripe, PayPal, etc.)
* All orders are cash-only (pickup)
* Payment handling is informational only and affects order status logic

### Delivery

* Delivery is not offered, only pickup
* Do NOT implement real-time tracking or third-party delivery services

### Authentication & Users

* Users must authenticate to place and view orders
* Order history is visible only to the authenticated user
* Do NOT implement social login unless explicitly requested

### Orders

* Orders must be persisted and associated with a user account
* Orders must include fulfillment type (pickup only)
* Order status should follow a simple, deterministic workflow
* Do NOT auto-cancel or auto-complete orders unless explicitly defined

### Shopping Cart

* Cart state must persist per user or session
* Cart modifications must not affect inventory until order submission

### Deployment & Environment

* Admin credentials (`ADMIN_EMAIL`, `ADMIN_PASSWORD`) must be provided via environment variables.
* The application must support execution in a Docker container (standalone mode).
* Domain is `yumbakeries.com`; ensure headers are compatible with Cloudflare proxy.

## Technical Rules

* Maintain clear separation of concerns (frontend, backend, data)
* Use consistent naming conventions across models, APIs, and UI
* Avoid hardcoding business rules; use configuration where reasonable
* Prefer explicit, readable logic over abstraction-heavy patterns
* **Code Testability**: Design code to be modular and testable (e.g., extract complex logic into helper functions).
* **Test Suite Retention**: Any tests created during implementation must be saved into the test suite (e.g., `backend/test_*.py`) for future regression prevention.

## Non-Goals (Strict)

* No online payments
* No subscriptions
* No coupons, discounts, or loyalty systems
* No real-time notifications unless requested

## AI Behavior Rules (Cursor)

* Do not invent requirements
* Do not assume external services unless specified
* Ask for clarification only if a requirement is ambiguous
* When in doubt, follow the simplest valid implementation

---

This file is authoritative. If `rules.md` conflicts with other instructions, `rules.md` takes precedence.
