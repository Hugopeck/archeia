# Architecture

## System Overview

Polar is an open-source payment infrastructure platform for developers. It provides a merchant-of-record service that handles billing, subscriptions, digital product sales, tax compliance (VAT/sales tax), and customer management. The platform consists of a Python/FastAPI backend API, a Next.js web dashboard, and background workers for asynchronous processing.

**Evidence:** `README.md`, `AGENTS.md`, `server/pyproject.toml`

## Topology

The system follows a client-server architecture with the backend serving as a centralized API that the frontend consumes.

- **API Server** (`server/polar/app.py`): FastAPI application serving REST endpoints at port 8000. Handles authentication, business logic, and database operations. Uses ASGI with Uvicorn.
- **Background Worker** (`server/polar/worker/`): Dramatiq-based worker processes that consume jobs from Redis queues. Handles async tasks like webhook delivery, payment processing callbacks, and email sending.
- **Web Dashboard** (`clients/apps/web/`): Next.js application at port 3000. Provides the merchant dashboard for managing products, subscriptions, orders, and customers.
- **PostgreSQL**: Primary data store for all business entities.
- **Redis**: Used as both a cache and message broker for Dramatiq job queues.
- **S3/MinIO**: Object storage for file uploads, customer invoices, and payout invoices.

**Evidence:** `DEVELOPMENT.md` (mermaid diagram), `dev/docker/docker-compose.dev.yml`, `server/polar/app.py`, `server/pyproject.toml`

## Module Boundaries

The backend is organized into domain modules under `server/polar/`, each following a consistent internal structure:

| Module Pattern | Purpose |
|----------------|---------|
| `endpoints.py` | FastAPI route definitions |
| `service.py` | Business logic encapsulated in service classes |
| `repository.py` | Database query logic using SQLAlchemy |
| `schemas.py` | Pydantic request/response models |
| `tasks.py` | Dramatiq background job definitions |
| `auth.py` | Module-specific authenticators with scopes |

Key domain modules (under `server/polar/`):

- **checkout/**, **checkout_link/**: Checkout flow and checkout link management
- **product/**: Product catalog with pricing, benefits, and custom fields
- **subscription/**: Subscription lifecycle management with metered billing
- **order/**: Order processing, payment locks, and fulfillment
- **customer/**, **customer_portal/**, **customer_seat/**: Customer identity, self-service portal, and seat-based access
- **benefit/**: Digital product benefits (GitHub repo access, Discord, file downloads, license keys)
- **transaction/**, **payment/**, **payout/**: Financial transaction processing and payouts
- **discount/**: Coupon and discount management
- **meter/**, **customer_meter/**: Usage-based billing meters and customer usage tracking
- **oauth2/**: OAuth2 authorization server (authorization codes, tokens, clients, grants)
- **integrations/**: Third-party integrations (GitHub, Stripe, Discord)
- **webhook/**: Outbound webhook delivery to merchant endpoints
- **worker/**: Dramatiq worker configuration and job scheduling

SQLAlchemy models are centralized in `server/polar/models/` (exception to the per-module pattern).

The frontend workspace (`clients/`) contains:
- **apps/web/**: Next.js dashboard (main merchant-facing UI)
- **apps/app/**: Secondary Next.js application
- **packages/ui/**: Shared React component library (Radix UI + Tailwind CSS)
- **packages/client/**: Auto-generated TypeScript API client from OpenAPI schema
- **packages/checkout/**: Embeddable checkout components
- **packages/orbit/**: Additional shared package
- **packages/i18n/**: Internationalization
- **packages/currency/**: Currency formatting utilities

**Evidence:** `AGENTS.md`, `server/polar/app.py`, `server/polar/models/`, `clients/pnpm-workspace.yaml`

## Data Flow

Primary request flow: User interacts with the Next.js web dashboard, which calls the FastAPI REST API. The API authenticates via session cookies or API tokens, processes business logic through service classes, queries PostgreSQL via SQLAlchemy repositories, and returns JSON responses. Asynchronous operations (webhook delivery, payment callbacks, email sending) are dispatched to Dramatiq workers via Redis queues.

Checkout flow: Customer → checkout page → API validates cart → Stripe payment intent → webhook callback → order creation → benefit grant → webhook delivery to merchant.

**Evidence:** `DEVELOPMENT.md`, `server/polar/app.py`, `server/polar/middlewares.py`, `server/polar/worker/`

## Data Model

The system uses SQLAlchemy with PostgreSQL. Key entity groups:

- **Commerce**: `Product`, `ProductPrice`, `Order`, `OrderItem`, `Checkout`, `CheckoutLink`, `Subscription`, `SubscriptionMeter`
- **Customer**: `Customer`, `CustomerSeat`, `CustomerSession`, `CustomerMeter`
- **Billing**: `Transaction`, `Payment`, `PaymentMethod`, `Payout`, `PayoutAttempt`, `BillingEntry`, `ProcessorTransaction`
- **Benefits**: `Benefit`, `BenefitGrant`, `LicenseKey`, `LicenseKeyActivation`, `Downloadable`
- **Organization**: `Organization`, `Member`, `OrganizationAccessToken`, `PersonalAccessToken`
- **Identity**: `User`, `UserSession`, `LoginCode`, `EmailVerification`
- **OAuth2**: `OAuth2Client`, `OAuth2AuthorizationCode`, `OAuth2Token`, `OAuth2Grant`
- **Discounts**: `Discount`, `DiscountProduct`, `DiscountRedemption`
- **Webhooks**: `WebhookEndpoint`, `WebhookEvent`, `WebhookDelivery`
- **Events**: `Event`, `EventType`, `ExternalEvent`

All models inherit from `RecordModel` (`polar.kit.db.models`).

**Evidence:** `server/polar/models/`

## State Lifecycles

Key stateful entities detected via StrEnum patterns:

- **Checkout**: has status lifecycle (detected in `server/polar/models/checkout.py` via StrEnum)
- **Subscription**: has status lifecycle (detected in `server/polar/models/subscription.py` via StrEnum)
- **Order**: has status and billing reason enums (detected in `server/polar/models/order.py` via StrEnum)

<!-- INSUFFICIENT EVIDENCE: exact state values and transitions for StateMachine.json — would require reading full model files -->

## Authentication

Custom authentication system using FastAPI dependency injection:

- `AuthSubject[T]` where T is `User`, `Organization`, `Customer`, or `Anonymous`
- Module-specific `Authenticator` definitions with required scopes and allowed subjects
- Credential resolution order: customer session token → user session cookie → OAuth2 token → personal access token → organization access token → anonymous
- Predefined authenticators: `WebUser`, `WebUserOrAnonymous`, `AdminUser`

**Evidence:** `AGENTS.md` (Authentication section), `server/polar/auth/`
