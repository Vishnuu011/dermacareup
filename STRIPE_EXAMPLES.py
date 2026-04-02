"""
Example usage of Stripe payment integration endpoints
These examples show how to interact with the payment API
"""

# Example 1: Create a Payment Intent
# ====================================

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/payments"
AUTH_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Create a payment intent for a one-time payment
payload = {
    "amount": 9999,  # $99.99 in cents
    "currency": "usd",
    "description": "Premium subscription renewal",
    "subscription_id": "optional-subscription-id"
}

response = requests.post(
    f"{BASE_URL}/create-payment-intent",
    headers=headers,
    json=payload
)

print("Create Payment Intent Response:")
print(json.dumps(response.json(), indent=2))
print()

# Extract client_secret for frontend payment collection
payment_intent = response.json()
client_secret = payment_intent["client_secret"]
payment_intent_id = payment_intent["payment_intent_id"]


# Example 2: Get Payment Status
# ==============================

response = requests.get(
    f"{BASE_URL}/payment-status/{payment_intent_id}",
    headers=headers
)

print("Get Payment Status Response:")
print(json.dumps(response.json(), indent=2))
print()


# Example 3: Confirm Payment
# ===========================

# After frontend has processed payment with Stripe.js
confirm_payload = {
    "stripe_payment_id": payment_intent_id,
    "payment_status": "succeeded"
}

response = requests.post(
    f"{BASE_URL}/confirm-payment",
    headers=headers,
    json=confirm_payload
)

print("Confirm Payment Response:")
print(json.dumps(response.json(), indent=2))
print()


# Example 4: Create Subscription
# ===============================

subscription_payload = {
    "price_id": "price_1234567890",  # From Stripe Dashboard
    "plan_name": "Premium Monthly",
    "scan_limit": 100
}

response = requests.post(
    f"{BASE_URL}/create-stripe-subscription",
    headers=headers,
    json=subscription_payload
)

print("Create Subscription Response:")
print(json.dumps(response.json(), indent=2))
print()

subscription_id = response.json()["subscription_id"]


# Example 5: Cancel Subscription
# ===============================

response = requests.post(
    f"{BASE_URL}/cancel-subscription/{subscription_id}",
    headers=headers
)

print("Cancel Subscription Response:")
print(json.dumps(response.json(), indent=2))
print()


# Example 6: Get Payment History
# ================================

response = requests.get(
    f"{BASE_URL}/history",
    headers=headers
)

print("Payment History Response:")
print(json.dumps(response.json(), indent=2))
print()


# Example 7: Frontend Stripe.js Integration
# ==========================================

frontend_code = """
{% raw %}
// Include Stripe.js
<script src="https://js.stripe.com/v3/"></script>

<form id="payment-form">
  <div id="card-element"></div>
  <div id="card-errors" role="alert"></div>
  <button id="submit-payment" type="button">Pay Now</button>
</form>

<script>
// Initialize Stripe
const stripe = Stripe('pk_test_YOUR_PUBLISHABLE_KEY');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

// Handle card errors
cardElement.addEventListener('change', (e) => {
  const displayError = document.getElementById('card-errors');
  displayError.textContent = e.error ? e.error.message : '';
});

// Handle form submission
document.getElementById('submit-payment').addEventListener('click', async (e) => {
  e.preventDefault();
  
  // Step 1: Get client_secret from backend
  const createIntentResponse = await fetch('/api/v1/payments/create-payment-intent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
      amount: 9999,
      currency: 'usd',
      description: 'Premium subscription'
    })
  });
  
  const intentData = await createIntentResponse.json();
  if (!intentData.success) {
    alert('Failed to create payment intent: ' + intentData.error);
    return;
  }
  
  // Step 2: Confirm payment with card details
  const { paymentIntent, error } = await stripe.confirmCardPayment(
    intentData.client_secret,
    {
      payment_method: {
        card: cardElement,
        billing_details: {
          email: 'customer@example.com'
        }
      }
    }
  );
  
  if (error) {
    document.getElementById('card-errors').textContent = error.message;
    return;
  }
  
  // Step 3: Confirm payment on backend
  const confirmResponse = await fetch('/api/v1/payments/confirm-payment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: JSON.stringify({
      stripe_payment_id: paymentIntent.id,
      payment_status: paymentIntent.status
    })
  });
  
  const confirmData = await confirmResponse.json();
  if (confirmData.success) {
    alert('Payment successful! Payment ID: ' + confirmData.payment_id);
  } else {
    alert('Failed to confirm payment');
  }
});
</script>
{% endraw %}
"""

print("Frontend Integration Code:")
print(frontend_code)
