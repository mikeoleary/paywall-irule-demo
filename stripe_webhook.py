from flask import Flask, request, jsonify, abort
import stripe, time, os, uuid, requests

app = Flask(__name__)
stripe.api_key = os.environ['STRIPE_API_KEY']
YOUR_ENDPOINT_SECRET =  os.environ['STRIPE_ENDPOINT_SECRET']
TOKEN_CACHE_SECRET =  os.environ['TOKEN_CACHE_SECRET']

def push_token_to_bigip(token):
    try:
        resp = requests.post(
            "https://demo.my-f5.com/cache-token",
            headers={
                "X-Webhook-Secret": TOKEN_CACHE_SECRET,  # must match static::shared_token_secret
                "Content-Type": "application/json"
            },
            json={"token": token},
            verify=False  # optional: add CA validation if needed
        )
        print("BIG-IP cache response:", resp.status_code)
    except Exception as e:
        print(f"Failed to push token to BIG-IP: {e}")

# The /stripe-webhook endpoint is intended to receive the webhook payload from Stripe after a successful payment
# the webhook payload will contain the session object, which includes the metadata and an entitlement token we set when creating the checkout session

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, YOUR_ENDPOINT_SECRET
        )
    except Exception as e:
        return str(e), 400

    # Handle successful Checkout Session
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # We’ll use session.client_reference_id or metadata["token"]
        token = session["metadata"]["entitlement_token"]
        expires = int(time.time()) + 3600  # 1-hour TTL
        # Store in token in BIG-IP irules table space
        push_token_to_bigip(token)
    return "", 200

# The /pricing endpoint is intended to generate a checkout URL to purchase access to the endpoint they have requested
@app.route('/pricing', methods=['GET'])
def pricing():
    requested_endpoint = request.headers.get("x-requested-endpoint", "None")
    price_id = request.headers.get("x-price-id", "None")
    """Root endpoint with API information"""

    # 1) Generate a fresh one-time token
    new_token = uuid.uuid4().hex

    # 2) Create Stripe Checkout session passing token in metadata & success_url
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://demo.my-f5.com/api/v1/hyperlocal?entitlement_token={new_token}",
            cancel_url=f"https://demo.my-f5.com/pricing",
            metadata={ "entitlement_token": new_token }
        )
        session_url = session.url
    except Exception as e:
        app.logger.error(f"Stripe session error: {e}")
        session_url = None


    return jsonify({
        "message": "You must supply a valid entitlement token in order to reach this endpoint",
        "requested_endpoint": requested_endpoint,
        "checkout_url": session_url,
        "version": "1.0"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)