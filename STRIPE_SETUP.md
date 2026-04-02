# Stripe Payment Integration Guide

This guide explains how to use the Stripe payment integration in the Derma FastAPI backend.

## Setup Instructions

### 1. Add Stripe Keys to `.env` File

Add the following to your `.env` file:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLIC_KEY=pk_test_YOUR_PUBLIC_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

**To get these keys:**

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Sign up or log in
3. Navigate to Developers > API Keys
4. Copy your **Secret Key** and **Publishable Key**
5. For webhook secret, go to Developers > Webhooks and create a new endpoint

### 2. Ensure Stripe is Installed

The `stripe` package is already in `requirements.txt`. Install dependencies if needed:

```bash
pip install stripe
```

## Available Endpoints

### Payment Intents (One-time Payments)

#### 1. Create Payment Intent

**POST** `/api/v1/payments/create-payment-intent`

Create a Stripe payment intent for one-time payments.

**Request:**

```json
{
  "amount": 5000,
  "currency": "usd",
  "description": "Subscription payment for premium plan",
  "subscription_id": "optional-subscription-id"
}
```

**Response:**

```json
{
  "success": true,
  "client_secret": "pi_1234567890_secret_1234567890",
  "payment_intent_id": "pi_1234567890",
  "amount": 5000,
  "currency": "usd",
  "status": "requires_payment_method"
}
```

**Frontend Integration:**
Use the `client_secret` with Stripe.js Elements to collect payment details.

#### 2. Get Payment Status

**GET** `/api/v1/payments/payment-status/{payment_intent_id}`

Check the status of a payment intent.

**Response:**

```json
{
  "success": true,
  "payment_intent_id": "pi_1234567890",
  "status": "succeeded",
  "amount": 5000,
  "currency": "usd",
  "client_secret": "pi_1234567890_secret_1234567890"
}
```

#### 3. Confirm Payment

**POST** `/api/v1/payments/confirm-payment`

Save payment confirmation to database after Stripe processes it.

**Request:**

```json
{
  "stripe_payment_id": "pi_1234567890",
  "payment_status": "succeeded"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Payment confirmed successfully",
  "payment_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "succeeded"
}
```

### Subscriptions

#### 1. Create Stripe Subscription

**POST** `/api/v1/payments/create-stripe-subscription`

Create a recurring subscription with Stripe.

**Request:**

```json
{
  "price_id": "price_1234567890",
  "plan_name": "Premium Plan",
  "scan_limit": 100
}
```

**Note:** You need to create prices in Stripe Dashboard first:

1. Go to Product Catalog > Prices
2. Create or select a product
3. Set up recurring price (e.g., $29.99/month)
4. Copy the price ID

**Response:**

```json
{
  "success": true,
  "subscription_id": "sub_1234567890",
  "customer_id": "cus_1234567890",
  "status": "active",
  "current_period_start": 1672531200,
  "current_period_end": 1675209600
}
```

#### 2. Cancel Subscription

**POST** `/api/v1/payments/cancel-subscription/{subscription_id}`

Cancel an active subscription.

**Response:**

```json
{
  "success": true,
  "message": "Subscription cancelled successfully",
  "subscription_id": "sub_1234567890",
  "status": "cancelled"
}
```

### Payment History

#### Get Payment History

**GET** `/api/v1/payments/history`

Retrieve all payments for the authenticated organization.

**Response:**

```json
{
  "success": true,
  "total_payments": 5,
  "payments": [
    {
      "payment_id": "550e8400-e29b-41d4-a716-446655440000",
      "organization_id": "org_id",
      "subscription_id": "sub_id",
      "stripe_payment_id": "pi_1234567890",
      "amount": 5000,
      "currency": "usd",
      "payment_status": "succeeded",
      "payment_date": "2024-01-15T10:30:00"
    }
  ]
}
```

### Webhooks

#### Setup Webhook

**POST** `/api/v1/payments/webhook`

Stripe sends webhook events to this endpoint. You must configure it in Stripe Dashboard:

1. Go to Developers > Webhooks
2. Click "Add endpoint"
3. Enter your endpoint: `https://yourdomain.com/api/v1/payments/webhook`
4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the signing secret to your `.env` as `STRIPE_WEBHOOK_SECRET`

**Handled Events:**

- `payment_intent.succeeded` - Saves successful payment to database
- `payment_intent.payment_failed` - Logs failed payment attempts
- `customer.subscription.updated` - Tracks subscription changes
- `customer.subscription.deleted` - Marks subscription as cancelled

## Frontend Integration Example

### Using Stripe.js Elements

```html
<script src="https://js.stripe.com/v3/"></script>

<div id="card-element"></div>
<button id="submit">Pay Now</button>

<script>
  const stripe = Stripe("{{ STRIPE_PUBLIC_KEY }}");
  const elements = stripe.elements();
  const cardElement = elements.create("card");
  cardElement.mount("#card-element");

  document.getElementById("submit").addEventListener("click", async () => {
    // 1. Get client_secret from backend
    const response = await fetch("/api/v1/payments/create-payment-intent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: 5000,
        currency: "usd",
        description: "Premium subscription",
      }),
    });

    const data = await response.json();
    const clientSecret = data.client_secret;

    // 2. Confirm payment with card details
    const result = await stripe.confirmCardPayment(clientSecret, {
      payment_method: {
        card: cardElement,
        billing_details: { email: "customer@example.com" },
      },
    });

    if (result.error) {
      console.error("Payment failed:", result.error.message);
    } else {
      // 3. Confirm payment on backend
      const confirmResponse = await fetch("/api/v1/payments/confirm-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stripe_payment_id: result.paymentIntent.id,
          payment_status: result.paymentIntent.status,
        }),
      });

      if (confirmResponse.ok) {
        alert("Payment successful!");
      }
    }
  });
</script>
```

## Database Schema

### Payments Table

```
- payment_id (UUID, Primary Key)
- organization_id (Foreign Key)
- subscription_id (Foreign Key, Optional)
- stripe_payment_id (String) - Stripe's payment intent ID
- amount (Integer) - Amount in cents
- currency (String) - Currency code (usd, eur, etc.)
- payment_status (String) - succeeded, failed, pending, etc.
- payment_date (DateTime)
```

### Subscriptions Table

```
- subscription_id (UUID, Primary Key)
- organization_id (Foreign Key)
- plan_name (String)
- scan_limit (Integer)
- price (Integer) - Price in cents (0 if managed by Stripe)
- start_date (DateTime)
- end_date (DateTime)
- status (String) - active, inactive, cancelled
```

## Testing with Stripe Test Cards

Use these test card numbers in test mode:

| Card Type  | Number              | Expiry          | CVC          |
| ---------- | ------------------- | --------------- | ------------ |
| Visa       | 4242 4242 4242 4242 | Any future date | Any 3 digits |
| Mastercard | 5555 5555 5555 4444 | Any future date | Any 3 digits |
| Declined   | 4000 0000 0000 0002 | Any future date | Any 3 digits |
| 3D Secure  | 4000 0025 0000 3155 | Any future date | Any 3 digits |

## Error Handling

The integration includes comprehensive error handling:

- **Invalid payment intent**: Returns 400 Bad Request
- **Unauthorized access**: Returns 403 Forbidden
- **Missing resources**: Returns 404 Not Found
- **Stripe errors**: Returns 400 Bad Request with error details
- **Server errors**: Returns 500 Internal Server Error

All errors are logged for debugging.

## Security Best Practices

1. **Never expose Secret Key**: Keep `STRIPE_SECRET_KEY` in `.env` only
2. **Use HTTPS**: Always use HTTPS in production
3. **Verify webhooks**: The webhook endpoint verifies Stripe signature
4. **Store securely**: Don't store full card details, use Stripe Payment Methods instead
5. **Rate limiting**: Consider implementing rate limiting on payment endpoints
6. **PCI compliance**: Use Stripe Elements to stay PCI compliant

## Common Issues

### "Invalid API Key"

- Check `STRIPE_SECRET_KEY` in `.env`
- Ensure you're using the correct key for the environment (test vs live)

### "Webhook signature verification failed"

- Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- Check timestamp validity (webhooks expire after 5 minutes)

### "Customer not found"

- Ensure customer email is valid
- Check stripe account permissions

## Additional Resources

- [Stripe Python SDK Documentation](https://stripe.com/docs/stripe-sdk/python)
- [Stripe Payment Intent Guide](https://stripe.com/docs/payments/payment-intents)
- [Stripe Subscriptions Guide](https://stripe.com/docs/billing/subscriptions/overview)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)

## Support

For issues or questions:

1. Check Stripe Dashboard logs
2. Review application logs in `logs/` directory
3. Verify webhook configuration
4. Test with Stripe test cards
