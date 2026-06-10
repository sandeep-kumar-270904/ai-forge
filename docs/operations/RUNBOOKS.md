# Runbooks

**STATUS: INCOMPLETE (Implementation Not Found During Analysis)**

## Active Runbooks
Currently, there are no documented step-by-step resolution procedures for production incidents.

### Required Runbooks (To be drafted by SRE)
1.  **`RB-001: Database Connection Exhaustion`**
    *   *Symptom:* `TimeoutError` from SQLAlchemy / `asyncpg`.
    *   *Draft Resolution:* Check `PgBouncer` active connections. Scale up max connections or horizontally scale database readers.
2.  **`RB-002: Model Gateway Rate Limit Breached`**
    *   *Symptom:* High frequency of `429 Too Many Requests` from OpenAI.
    *   *Draft Resolution:* Check Redis cache hit rates. Contact OpenAI for Tier upgrade. Temporarily hardcode gateway to route to Anthropic via environmental feature flag.
3.  **`RB-003: Redis Eviction Failure`**
    *   *Symptom:* Semantic cache stops returning hits; API latency spikes.
    *   *Draft Resolution:* Check `maxmemory-policy`. Ensure it is set to `allkeys-lru`. Increase Redis instance size.
