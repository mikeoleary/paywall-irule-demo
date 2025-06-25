# paywall-irule-demo

## Instructions

1. Let's start our mock weather API:
```bash
python3 weather_api.py
```

2. In a new window, let's start our python app to proxy requests for redis:
```bash
export STRIPE_API_KEY='sk_live_...'
export STRIPE_ENDPOINT_SECRET='whsec_...'
python3 stripe-webhook.py
```

3. Now let's make API calls to our service.

## Why is this cool?

1. Notice that **the Weather API and the paywall iRule are completely separate**.

2. This can be **extended** for other API endpoints:
- **Multiple endpoints**: 
  - a datagroup can store premium endpoints and the prices for each endpoint. E.g.:
    - /api/v1/hyperlocal = $0.50 / hr
    - /api/v1/local = $0.25 / hr
    - /api/v1/regional = free
  - endpoints could be **batched**. E.g.: 
    - /api/v1/* = free
    - /api/v2/* = $0.50 / hr
- **Price variations**:
  - Cheaper prices can be offered for internal users
  - Pricing can be tested by business users independently of the application team
- **Rate limiting**:
  - Rate limiting could be enforced in iRule logic + redis, outside of the app team
  - bypassing the iRule could be allowed, i.e., for internal requests the paywall could be waived
