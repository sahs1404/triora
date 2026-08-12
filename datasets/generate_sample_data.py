"""
Triora — Sample Dataset Generator
Regenerates the Round 1 synthetic project (22-activity schedule, 137 materials,
2 real critical risks + 1 late-but-safe decoy) in the NEW schema format:
datasets/sample_activities.csv, sample_materials.csv, sample_vendors.csv

Run this once to produce the starter datasets for local testing / the Upload demo.
    python generate_sample_data.py
"""

import csv
import numpy as np

np.random.seed(42)

# -----------------------------------------------------------------------
# 1. ACTIVITIES — same 22-activity project schedule as Round 1, but now
#    with explicit "predecessors" column (what the new schema expects)
#    instead of a separate edge list.
# -----------------------------------------------------------------------
# (id, name, duration_days, predecessors)
activities = [
    ("A01", "Site Mobilization", 5, []),
    ("A02", "Foundation Excavation", 10, ["A01"]),
    ("A03", "Foundation Pour", 8, ["A02"]),
    ("A04", "Structural Steel Erection", 20, ["A03"]),
    ("A05", "Structural Steel Inspection", 3, ["A04"]),
    ("A06", "Envelope / Facade", 25, ["A05"]),
    ("A07", "Roofing", 12, ["A04"]),
    ("A08", "Electrical Rough-In", 18, ["A05"]),
    ("A09", "Switchgear Installation", 22, ["A08"]),
    ("A10", "Transformer Installation", 19, ["A09"]),
    ("A11", "HVAC Ductwork", 15, ["A08"]),
    ("A12", "AHU Installation", 7, ["A11"]),
    ("A13", "Chiller Installation", 6, ["A12"]),
    ("A14", "Plumbing Rough-In", 14, ["A08"]),
    ("A15", "Fire Suppression System", 10, ["A14"]),
    ("A16", "Elevator Installation", 20, ["A06", "A07"]),
    ("A17", "Electrical Energization", 4, ["A10"]),
    ("A18", "HVAC Commissioning", 8, ["A17", "A13"]),
    ("A19", "Fire & Life Safety Inspection", 5, ["A15", "A18"]),
    ("A20", "Interior Finishes", 22, ["A16", "A19"]),
    ("A21", "Final MEP Commissioning", 10, ["A20"]),
    ("A22", "Substantial Completion", 3, ["A21"]),
]

with open("/home/claude/triora/datasets/sample_activities.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "duration_days", "predecessors"])
    for aid, name, dur, preds in activities:
        writer.writerow([aid, name, dur, "|".join(preds)])  # pipe-separated for multi-predecessor cells

print(f"Wrote sample_activities.csv ({len(activities)} activities)")

# -----------------------------------------------------------------------
# 2. VENDORS — a small vendor pool, each with a historical_delay_rate.
#    Materials will reference these by vendor_id instead of embedding
#    p_delay directly, matching the new Tier-4 (vendor memory) design.
# -----------------------------------------------------------------------
vendor_pool = [
    ("V01", "Apex Steel Fabricators", 0.12),
    ("V02", "Meridian Electricals", 0.10),
    ("V03", "Suncore Switchgear Ltd", 0.78),   # unreliable — feeds the hero risk
    ("V04", "PowerLine Transformers", 0.71),   # unreliable — feeds the hero risk
    ("V05", "CoolAir HVAC Systems", 0.18),
    ("V06", "FlowTech Plumbing Supplies", 0.15),
    ("V07", "SafeGuard Fire Systems", 0.14),
    ("V08", "Vertical Elevator Co.", 0.85),    # unreliable, but sits on high-float activity (the decoy)
    ("V09", "Facade Glass Works", 0.11),
    ("V10", "GeneralBuild Materials", 0.13),
]

with open("/home/claude/triora/datasets/sample_vendors.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "historical_delay_rate", "jobs_completed", "jobs_delayed"])
    for vid, name, rate in vendor_pool:
        jobs_completed = int(np.random.randint(8, 40))
        jobs_delayed = round(jobs_completed * rate)
        writer.writerow([vid, name, rate, jobs_completed, jobs_delayed])

print(f"Wrote sample_vendors.csv ({len(vendor_pool)} vendors)")

# -----------------------------------------------------------------------
# 3. MATERIALS — same 137-material logic as Round 1: mostly reliable
#    vendors (low delay rate) on the bulk, plus 2 hero critical risks
#    (Switchgear/Transformer, unreliable vendor + zero-float activity)
#    and 1 late-but-safe decoy (Elevator Cab, unreliable vendor but
#    sits on a high-float activity).
# -----------------------------------------------------------------------
material_catalog = [
    "Structural Steel Beams", "Rebar Bundles", "Ready-Mix Concrete", "Curtain Wall Panels",
    "Roofing Membrane", "Cable Trays", "MV Cables", "Ductwork Sections", "VAV Boxes",
    "Copper Piping", "PVC Piping", "Sprinkler Heads", "Fire Pumps",
    "Gypsum Board", "Ceiling Tiles", "Flooring Tiles", "Paint & Coatings",
    "Insulation Rolls", "Conduit", "Junction Boxes", "Lighting Fixtures", "Control Panels",
    "Access Doors", "Louvers", "Dampers", "VFD Drives", "Generator Set",
]

# activities materials can legitimately be tied to (skip pure start/end milestones)
activity_ids = [a[0] for a in activities if a[0] not in ("A01", "A22")]

# vendor_id -> which activities that vendor's materials would realistically feed
# (kept loose/random for the bulk; heroes and decoy are hand-pinned below)
reliable_vendor_ids = ["V01", "V02", "V05", "V06", "V07", "V09", "V10"]

rows = []

# --- Bulk: 134 materials, reliable vendors, random activity assignment ---
for i in range(134):
    mat_id = f"M{i+1:03d}"
    name = np.random.choice(material_catalog)
    act = np.random.choice(activity_ids)
    vendor = np.random.choice(reliable_vendor_ids)
    lead_time = int(np.random.gamma(shape=4, scale=6)) + 5
    rows.append([mat_id, name, act, vendor, lead_time, "", "", "", ""])

# --- Hero risk 1: Switchgear Unit, unreliable vendor, zero-float activity ---
rows.append(["M135", "Switchgear Unit", "A09", "V03", 45, "", "", "delayed - factory backlog", ""])

# --- Hero risk 2: Transformer, unreliable vendor, zero-float activity ---
rows.append(["M136", "Transformer", "A10", "V04", 52, "", "", "delayed - testing backlog", ""])

# --- Decoy: Elevator Cab, unreliable vendor, BUT high-float activity (A16) ---
rows.append(["M137", "Elevator Cab", "A16", "V08", 40, "", "", "delayed - shipping", ""])

with open("/home/claude/triora/datasets/sample_materials.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "id", "name", "activity_id", "vendor_id", "lead_time_days",
        "promised_delivery_date", "need_by_date", "vendor_reported_status",
        "manual_p_delay_override"
    ])
    writer.writerows(rows)

print(f"Wrote sample_materials.csv ({len(rows)} materials)")
print("\nDone. 3 files written to /home/claude/triora/datasets/")
print("Expected result when scored: M135 (Switchgear) and M136 (Transformer)")
print("rank as critical; M137 (Elevator Cab) ranks low despite an unreliable vendor,")
print("because A16 has schedule float. That contrast is the whole point of the demo.")
