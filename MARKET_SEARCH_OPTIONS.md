# Market / City Search — Current State & Implementation Options

## Does census_data have "Market" or "City"?

**No.** The `census_data` table does **not** have a "Market" or "City" column.

**What it does have:**

| Column | Notes |
|--------|--------|
| `zip_code` | Primary geography; all census rows are by zip (ZCTA). |
| `state` | Exists in the schema but is **not populated** (comment: "avoids DDL timeout"). |
| `county` | Exists in the schema but is **not populated**. |
| `population`, `median_age`, `average_household_income`, etc. | Populated from Census API. |

The Census API we use returns data by **ZCTA (zip code tabulation area)** only. It does not return city or market names, so we’d need another source to attach “market” or “city” to zips.

---

## Ideal behavior you described

- **Separate from zip/address search:** A **“Search by Market”** (or city) in the **Data Layers** section.
- **Result:** Highlight **all zip codes** that belong to that market on the map.

That’s doable once we have a way to know which zips belong to which market.

---

## How difficult to implement?

**Medium**, if you have (or can create) a **zip → market** mapping. Breakdown:

### 1. Data: zip → market

You need a list of which zips belong to which market (or city).

**Options:**

- **A. Add a `market` column to `census_data`**  
  - Add `market` (e.g. `VARCHAR`) to the model and run a migration.  
  - Populate via a one-time script from a CSV/spreadsheet: `zip_code, market_name`.  
  - Pros: Simple queries (`WHERE market = ?`).  
  - Cons: Schema change; need to backfill and keep in sync.

- **B. Separate mapping table** (e.g. `zip_market`)  
  - Table: `zip_code`, `market_name` (and optionally `city`).  
  - No change to `census_data` schema.  
  - Pros: Flexible; can have multiple “market” definitions.  
  - Cons: Join or two-step query (zips by market → then census for those zips).

- **C. External source**  
  - e.g. HUD, Nielsen DMAs, or your own “markets” list.  
  - Script to build option A or B from that source.

**Difficulty:** Low if you already have a CSV/list of zip → market; medium if you need to define and build that list.

### 2. Backend

- **New (or extended) API:** e.g. `GET /api/census-data?market=Charlotte` or `GET /api/markets/{market_name}/zips` returning zip codes (and optionally census rows) for that market.
- **Implementation:** Query by `market` (if column on `census_data`) or from `zip_market` + filter census_data by those zips. Straightforward.

**Difficulty:** Low.

### 3. Frontend (Data Layers + map)

- **Data Layers:** Add a “Search by Market” control (e.g. dropdown or typeahead of market names, separate from zip/address).
- **On “Go”:** Call the new API to get the list of zips for that market.
- **Map:** Use the same boundary/heatmap logic you already have, but **restrict to those zips** (and optionally highlight their boundaries). Same patterns as “highlight one zip,” but loop over many zips.

**Difficulty:** Low–medium (reuse existing “load census + draw boundaries” flow, filtered by market zips).

### 4. Backup before changing code

You asked to save the current version as a backup before making changes. Recommended:

- **Tag or branch in git:** e.g. `git tag pre-market-search` or `git checkout -b backup-pre-market-search` and push.
- **Or zip the project** (excluding `node_modules`, `.venv`, large `data/` if needed) and name it e.g. `Data-Site-Selection-Process-backup-YYYYMMDD.zip`.

Then implement market search on a new branch or in a copy.

---

## Summary

| Question | Answer |
|----------|--------|
| Does census_data have Market or City? | **No.** Only zip-level fields; `state`/`county` exist but are unpopulated. |
| How hard to add “search by market” and highlight all zips in that market? | **Medium** overall: need a zip→market data source and a place to store it (new column or table); backend and UI are straightforward. |
| What to do before coding? | **Back up current version** (git tag/branch or project zip), then add market data + API + UI. |

If you later want to implement it, the sequence is: (1) define markets and get zip→market data, (2) add storage (column or table), (3) add API for “zips by market,” (4) add “Search by Market” in Data Layers and wire it to highlight those zips on the map. No code changes were made in this step; this doc is for reference when you’re ready.
