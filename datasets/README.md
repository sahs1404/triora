# Datasets

Sample project data for local testing of the Triora backend — used to test-drive
the upload endpoint and the CWRS engine before real project data exists.

## Files

| File | Rows | Purpose |
|---|---|---|
| `sample_activities.csv` | 22 | The project schedule (CPM graph nodes) |
| `sample_materials.csv` | 137 | Tracked materials, each tied to one activity + vendor |
| `sample_vendors.csv` | 10 | Supplier reliability data (feeds Tier 4 vendor memory) |
| `generate_sample_data.py` | — | Regenerates all 3 CSVs above from scratch |

Regenerate with:
```bash
python generate_sample_data.py
```

---

## Column formats

### `sample_activities.csv`

| Column | Type | Notes |
|---|---|---|
| `id` | string | Unique activity ID, e.g. `A09` |
| `name` | string | Human-readable activity name |
| `duration_days` | int | How long the activity takes |
| `predecessors` | string | Pipe-separated (`\|`) list of activity IDs that must finish first. Empty for the project's starting activity. |

**Example:** `A18,HVAC Commissioning,8,A17\|A13` means A18 takes 8 days and can't start until *both* A17 and A13 are done.

The activity graph must be a valid DAG (no cycles) — the backend will reject the
upload with an error if it finds one.

---

### `sample_vendors.csv`

| Column | Type | Notes |
|---|---|---|
| `id` | string | Unique vendor ID, e.g. `V03` |
| `name` | string | Vendor/supplier name |
| `historical_delay_rate` | float (0–1) | Prior probability this vendor delivers late. Starts as a rough estimate; updated over time by `ml/vendor_learning/reliability_update.py` as real job outcomes come in. |
| `jobs_completed` | int | Total jobs this vendor has been tracked on |
| `jobs_delayed` | int | How many of those were late |

---

### `sample_materials.csv`

| Column | Type | Notes |
|---|---|---|
| `id` | string | Unique material ID, e.g. `M135` |
| `name` | string | Material name |
| `activity_id` | string | Which activity this material feeds — must match an ID in `sample_activities.csv` |
| `vendor_id` | string | Which vendor supplies it — must match an ID in `sample_vendors.csv` |
| `lead_time_days` | int | Expected time from order to delivery |
| `promised_delivery_date` | string (ISO date) or empty | Optional — leave blank if unknown |
| `need_by_date` | string (ISO date) or empty | Optional — if blank, the engine derives this from the activity's early-start date via CPM |
| `vendor_reported_status` | string or empty | Free-text evidence, e.g. `"delayed - factory backlog"`. Not yet used in scoring — reserved for the document-intelligence layer (roadmap). |
| `manual_p_delay_override` | float (0–1) or empty | If set, overrides the vendor-based delay probability entirely. Leave blank to let the engine calculate `p_delay` from the vendor's `historical_delay_rate`. |

---

## The story baked into this sample data

This dataset isn't random — it's built to prove Triora's core insight when scored:

- **M135 (Switchgear Unit)** and **M136 (Transformer)** sit on **zero-float activities**
  (A09, A10 — the true critical path) and use **unreliable vendors** (78% and 71%
  historical delay rates). They should rank as **critical**.
- **M137 (Elevator Cab)** uses the *most* unreliable vendor in the dataset (85% delay
  rate) but sits on **A16, which has real schedule float**. It should rank **low**
  despite looking like the scariest material on paper.

If your CWRS engine is working correctly, M137 should NOT outrank M135/M136 — that
contrast (late-but-safe vs. on-time-but-critical) is the whole product thesis made
visible in the data. If it doesn't reproduce this pattern, check `cwrs_service.py`
and `cpm_service.py` before assuming the data is wrong.

## Uploading your own project

To test with a different project, create your own 3 CSVs following the column
formats above and POST them to `/project/build` (see `docs/api_contract.md`).
Activity IDs and vendor IDs referenced in `sample_materials.csv` must exist in
the corresponding activities/vendors file, or the upload will be rejected.
