"""
One-off test script — NOT part of the app. Run this manually to verify
the backend + engine work end-to-end using your existing sample CSVs.

Usage (from backend/, with the server running in another terminal):
    python csv_to_json_test.py
"""

import pandas as pd
import requests
import json

DATASETS_DIR = "../datasets"  # adjust if your folder layout differs

activities_df = pd.read_csv(f"{DATASETS_DIR}/sample_activities.csv").fillna("")
materials_df = pd.read_csv(f"{DATASETS_DIR}/sample_materials.csv").fillna("")
vendors_df = pd.read_csv(f"{DATASETS_DIR}/sample_vendors.csv").fillna("")

activities = [
    {
        "id": row["id"], "name": row["name"], "duration_days": int(row["duration_days"]),
        "predecessors": row["predecessors"].split("|") if row["predecessors"] else [],
    }
    for _, row in activities_df.iterrows()
]

vendors = [
    {
        "id": row["id"], "name": row["name"],
        "historical_delay_rate": float(row["historical_delay_rate"]),
        "jobs_completed": int(row["jobs_completed"]), "jobs_delayed": int(row["jobs_delayed"]),
    }
    for _, row in vendors_df.iterrows()
]

materials = [
    {
        "id": row["id"], "name": row["name"], "activity_id": row["activity_id"],
        "vendor_id": row["vendor_id"] or None, "lead_time_days": int(row["lead_time_days"]),
        "promised_delivery_date": row["promised_delivery_date"] or None,
        "need_by_date": row["need_by_date"] or None,
        "vendor_reported_status": row["vendor_reported_status"] or None,
        "manual_p_delay_override": float(row["manual_p_delay_override"]) if row["manual_p_delay_override"] != "" else None,
    }
    for _, row in materials_df.iterrows()
]

payload = {
    "project_name": "demo_project",
    "activities": activities,
    "materials": materials,
    "vendors": vendors,
}

response = requests.post("http://127.0.0.1:8000/project/build", json=payload)
print("Status:", response.status_code)

if response.status_code == 200:
    result = response.json()
    print(f"\nProject: {result['summary']['project_name']}")
    print(f"Total materials: {result['summary']['total_materials']}")
    print(f"Critical: {result['summary']['critical_count']}  |  Watch: {result['summary']['watch_count']}")
    print(f"Project duration: {result['summary']['project_duration_days']} days")

    print("\nTop 5 by CWRS:")
    for m in result["materials"][:5]:
        print(f"  #{m['rank']}  {m['name']:25s}  cwrs={m['cwrs']:.3f}  status={m['status']}")

    elevator = next(m for m in result["materials"] if m["material_id"] == "M137")
    print(f"\nDecoy check — Elevator Cab: rank #{elevator['rank']} of {len(result['materials'])}, "
          f"status={elevator['status']}, cwrs={elevator['cwrs']:.3f}")
else:
    print("Error:", response.text)