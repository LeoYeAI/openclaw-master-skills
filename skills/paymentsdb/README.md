Go to https://paymentsdb.com to provision a read only postgres database and then modify `query.sh` with your username & password.

This is a secure implementation with major advantages compared to calling the Stripe API directly:
- OpenClaw has no access to your Stripe API Key.
- You cannot hit rate limits and break your Stripe, you are just querying a replica postgres database