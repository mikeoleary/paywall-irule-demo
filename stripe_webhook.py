from flask import Flask, request, jsonify, abort
import stripe, redis, time, os, uuid

app = Flask(__name__)
stripe.api_key = os.environ['STRIPE_API_KEY']
YOUR_ENDPOINT_SECRET =  os.environ['STRIPE_ENDPOINT_SECRET']
r = redis.Redis()

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
        # Store in Redis: key=token, value="hyperlocal", with TTL
        r.setex(f"{token}", expires - int(time.time()), "hyperlocal")
    return "", 200

# The /pricing endpoint is intended to generate a checkout URL to purchase access to the endpoint they have requested
@app.route('/pricing', methods=['GET'])
def pricing():
    requested_endpoint = request.headers.get("x-requested-endpoint", "None")
    price_id = request.headers.get("x-price-id", "None")
    """Root endpoint with API information"""

    # 1) Generate a fresh one-time token
    new_token = uuid.uuid4().hex
    # We'll set a short-lived stub entry; real entry comes via webhook
    r.setex(f"{new_token}", 300, "pending")  # 5min TTL pending

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

# The /validate endpoint checks if the token exists in Redis
@app.route('/validate', methods=['GET'])
def validate():
    entitlement_token = request.headers.get("X-Entitlement-Token", "None")
    if r.exists(f"{entitlement_token}"):
        return r.get(f"{entitlement_token}").decode(), 200
    else:
        abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)