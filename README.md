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
python3 stripe_webhook.py
```

3. Now let's make API calls to our service.

```bash
curl https://demo.my-f5.com/api/v1/local  # -> this returns local weather data (mock API)
curl https://demo.my-f5.com/api/v1/regional # -> returns regional data

```

## Why is this cool?

1. **Business Value:** notice that the Weather API and the Paywall iRule are *separately managed*. This means:
  - The paywall can be managed independently of the app
  - Different pricing models can be tested or implemented based on network metrics

2. **Best practices** for iRules are followed:
- This is intended for API clients / web crawlers, but will work for browser clients and CLI/API clients alike (allows use of HTTP Headers or URI query parameters for easy browser testing) 
- iRule [debug logging](https://my.f5.com/manage/s/article/K55131641) can be toggled on/off for troubleshooting
- Caching of frequently accessed data is enabled with the [table](https://clouddocs.f5.com/api/irules/table.html) command.

3.  This can be **extended** for other API endpoints:
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

## Why Use iRules LX?
| Capability | Benefit |
| ------------- | ------------- |
| ✅ Node.js engine | Full programming model |
| ✅ HTTP clients | Talk to Stripe, REST APIs, etc. |
| ✅ JSON parsing | Native in Node.js |
| ✅ Redis | Many clients supported |
| ✅ Local filesystem | Store cache, configs |
| ✅ Asynchronous logic | Avoid delays in request flow |
| ✅ Tight F5 integration | Inline with traffic enforcement |

## Why NOT to Use iRules LX?

| Note | Reason |
| ------------- | ------------- |
| ❓ NodeJS 6.9.1 | Outdated NodeJS version |
| ❓ Supportability | More difficult than NodeJS on external VM/container |
| ❌ Future support | No plan for iRulesLX in BIG-IP Next |