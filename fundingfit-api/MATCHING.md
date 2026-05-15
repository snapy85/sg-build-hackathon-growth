# Matching Engine

The matching engine scores each funding scheme against a business profile without making any LLM calls at request time. All AI involvement is limited to a one-time offline step that populates `data/schemes.json` — after that, matching is pure deterministic Python.

---

## Request flow

```
POST /api/match
  │
  ├── identity_service: resolve X-Session-ID → BusinessProfile
  ├── schemes_service:  load schemes.json, filter by postcode region
  ├── matching_service: score each scheme in parallel (asyncio + thread pool)
  └── sort results: strong_match first, then local before national at equal fit
```

The endpoint is in `routers/match.py`. It accepts an optional `?mock=true` query parameter that returns hardcoded results without touching the database or matching engine — useful for frontend development before a real profile exists.

---

## Scheme data structure

Each scheme in `data/schemes.json` has two machine-readable sections added alongside the existing human-readable fields:

### `rules`

An array of explicit eligibility conditions evaluated directly against the business profile:

```json
"rules": [
  {
    "field": "trading_age_years",
    "operator": "lt",
    "value": 3,
    "label": "Trading under 3 years",
    "knockout": true
  },
  {
    "field": "annual_revenue",
    "operator": "gte",
    "value": 50000,
    "label": "Turnover of £50,000 or above",
    "knockout": false
  }
]
```

- **`field`** — which profile attribute to test (see [Supported fields](#supported-fields))
- **`operator`** — comparison: `lt`, `lte`, `gt`, `gte`, `eq`, `in`, `not_in`, `any_in`
- **`value`** — the threshold or set to compare against
- **`label`** — plain-English label shown to the user in eligibility lists
- **`knockout`** — if `true`, a failing rule immediately produces `not_suitable` regardless of all other rules

### `tags`

Keyword sets used for soft scoring when all hard rules have passed:

```json
"tags": {
  "sectors": ["creative", "digital"],
  "goals":   ["equipment", "marketing", "growth"]
}
```

Schemes with empty `sectors` and `goals` are treated as broadly applicable and score 1.0 automatically (e.g. Start Up Loans, which has no sector restriction).

---

## Matching algorithm

For each scheme, `match_scheme()` in `services/matching_service.py` runs three stages:

### Stage 1 — Rule evaluation

Every rule is evaluated against the business profile. Each rule produces one of three outcomes:

| Outcome | Condition | Placed in |
|---------|-----------|-----------|
| Pass | Rule condition is true | `eligibility_met` |
| Fail | Rule condition is false | `eligibility_unmet` |
| Unknown | Profile field is `None` (not collected yet) | `uncertain` |

If a rule returns **Unknown** but has `knockout: true`, the criterion cannot be confirmed — this blocks `strong_match` even though it does not produce `not_suitable`.

### Stage 2 — Fit tier assignment

```
any knockout rule fails    →  not_suitable
any uncertain knockout     →  possible
all knockouts pass:
  keyword score >= 0.5
  AND no soft rule fails   →  strong_match
  otherwise                →  possible
```

### Stage 3 — Keyword scoring

Only reached when all knockout rules pass with no unknowns.

The business profile's `sector` field is normalised into a set of canonical tags (e.g. `"Creative services"` → `{"creative"}`). The `goals` list is similarly normalised (e.g. `"buy equipment"` → `{"equipment"}`).

The score is the average of two binary signals:

- **Sector match** — does any business sector tag appear in the scheme's `tags.sectors`? (1.0 or 0.0; skipped if scheme has no sector tags)
- **Goal match** — does any business goal tag appear in the scheme's `tags.goals`? (1.0 or 0.0; skipped if scheme has no goal tags)

A score ≥ 0.5 with no soft-rule failures gives `strong_match`. Below that gives `possible`.

---

## Supported fields

| Field | Source | Type | Notes |
|-------|--------|------|-------|
| `trading_age_years` | Derived from `registration_date` | float | Calculated at match time from today's date |
| `employee_count` | PAYE / user-provided | int or None | None → uncertain |
| `annual_revenue` | HMRC self-assessment / user-provided | float or None | None → uncertain |
| `trading_status` | HMRC / Companies House | string | `sole_trader`, `limited_company`, `partnership` |
| `sector` | Derived from SIC code | string | Normalised to tags via `_SECTOR_MAP` |
| `has_rd_activity` | User-provided (onboarding) | bool or None | None → uncertain; collected for R&D schemes |
| `owner_age` | User-provided (onboarding) | int or None | None → uncertain; collected for King's Trust |
| `funding_needed` | User-provided (onboarding) | int or None | None → uncertain; for funding range filtering |

Fields marked *None → uncertain* will hold many profiles back from `strong_match` until they are explicitly collected during onboarding and stored via `PATCH /api/business/me`.

---

## Region filtering

Before matching runs, `schemes_service.filter_by_region()` narrows the scheme list to those geographically relevant to the business's postcode. This happens in `match.py` before `match_all()` is called.

| Postcode prefix | Schemes shown |
|-----------------|---------------|
| `LS` | Leeds + West Yorkshire + national |
| `BD`, `HX`, `HD`, `WF` | West Yorkshire + national |
| Anything else (or blank) | National only |

Region is inferred from each scheme's eligibility criteria — a scheme with `"Registered and operating in West Yorkshire"` is tagged `west_yorkshire`; `"UK-based business"` is tagged `national`.

---

## Result sorting

Results are sorted by `routers/match.py` after matching, not by the matching engine itself:

1. Fit tier: `strong_match` → `possible` → `not_suitable`
2. Within the same tier: local schemes (`leeds`, `west_yorkshire`) before `national`

---

## Extending the engine

### Adding a new scheme

Add an entry to `data/schemes.json` with `rules` and `tags` populated. The matching engine picks it up automatically — no code changes needed.

### Adding a new eligibility field

1. Add the field as `Optional[...]` to `BusinessProfile` and `BusinessProfileUpdate` in `models/business.py`
2. Add a handler for it in `_evaluate_rule()` in `services/matching_service.py`
3. Add the relevant `rules` entries to whichever schemes use it in `schemes.json`
4. If the field needs to be collected from the user, add it to the onboarding flow and expose it via `PATCH /api/business/me`

### Adding a new sector or goal keyword

Edit `_SECTOR_MAP` or `_GOAL_MAP` in `services/matching_service.py`. Both are plain dicts — the key is the canonical tag name and the value is a list of substrings matched case-insensitively against the profile's free-text field.
