"""
Test script for the Triora what-if simulator.
Run with the server already running in another terminal:
    python whatif_test.py
"""

import requests

BASE_URL = "http://127.0.0.1:8000/project/demo_project/whatif"


# -----------------------------------------------------------------------
# TEST 1 — reassign Switchgear to a reliable vendor
# Expected: p_delay drops (V03 @ 78% -> V01 @ 12%), so CWRS should drop
# visibly. Project duration should stay the same (vendor swap doesn't
# touch schedule).
# -----------------------------------------------------------------------
print("=" * 60)
print("TEST 1 — Reassign Switchgear to a reliable vendor (V03 -> V01)")
print("=" * 60)

payload1 = {
    "project_name": "demo_project",
    "changes": [
        {"change_type": "reassign_vendor", "target_id": "M135", "value": "V01"}
    ]
}

response1 = requests.post(BASE_URL, json=payload1)
print("Status:", response1.status_code)

if response1.status_code == 200:
    result1 = response1.json()
    before1 = next(m for m in result1['before']['materials'] if m['material_id'] == 'M135')
    after1 = next(m for m in result1['after']['materials'] if m['material_id'] == 'M135')

    print(f"\nSwitchgear BEFORE: p_delay={before1['p_delay']:.3f}, cwrs={before1['cwrs']:.3f}, "
          f"rank=#{before1['rank']}, status={before1['status']}")
    print(f"Switchgear AFTER:  p_delay={after1['p_delay']:.3f}, cwrs={after1['cwrs']:.3f}, "
          f"rank=#{after1['rank']}, status={after1['status']}")
    print(f"\nMaterials whose status changed: {result1['materials_changed_status']}")
else:
    print("Error:", response1.text)


# -----------------------------------------------------------------------
# TEST 2 — stretch Switchgear Installation's duration (A09 is on the
# critical path, so this should push project duration out by the same
# amount, 1:1).
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 2 — Stretch A09 (Switchgear Installation) duration 22 -> 30 days")
print("=" * 60)

payload2 = {
    "project_name": "demo_project",
    "changes": [
        {"change_type": "change_duration", "target_id": "A09", "value": 30}
    ]
}

response2 = requests.post(BASE_URL, json=payload2)
print("Status:", response2.status_code)

if response2.status_code == 200:
    result2 = response2.json()
    print(f"\nProject duration BEFORE: {result2['before']['summary']['project_duration_days']} days")
    print(f"Project duration AFTER:  {result2['after']['summary']['project_duration_days']} days")
    print(f"Delta: {result2['project_duration_delta_days']} days")
else:
    print("Error:", response2.text)