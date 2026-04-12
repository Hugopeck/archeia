# customer_portal

Self-service customer portal allowing end users to manage their subscriptions, view orders, access benefits, and update billing information without merchant intervention.

## Key Concepts

- **Customer-facing API** -- Endpoints authenticated via `CustomerSession` tokens, not merchant credentials. Customers can view their orders, manage subscriptions, access downloads, and update payment methods.
- **Benefit access** -- Portal surfaces active benefit grants (license keys, file downloads) associated with the customer's purchases.
- **Subscription management** -- Customers can upgrade, downgrade, or cancel subscriptions through the portal.

## Usage

Accessed by the web dashboard's customer-facing views. Merchants embed or link to the portal for their customers.

## Learnings

_No learnings recorded yet._
