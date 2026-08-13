\# Triora



\### 40 alerts. Only 2 matter.



\*\*Construction material risk triage for the AI-native supply chain.\*\*



Built for the \*\*Kaya AI India Hackathon 2026\*\* — Track 2: Supply Chain



\[!\[Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://triora-xi.vercel.app)

\[!\[Backend API](https://img.shields.io/badge/API-FastAPI-009688)](https://triora-zouh.onrender.com)



\---



\## The Problem



Every active construction project tracks hundreds of material packages — steel, switchgear, ductwork, fasteners. On any given week, dozens of them show \*some\* kind of delay signal: a late vendor email, a missed submittal date, a shipment running behind schedule.



Existing tools flag all of them the same way. Red. Late. At risk.



\*\*A project manager staring at 40 identical red flags has no way to know which ones actually threaten the project — so in practice, they act on none of them.\*\*



This is the real failure mode in construction supply chains. Not a lack of data. A lack of triage.



\## The Insight



> \*\*Delivery delay ≠ project delay.\*\*



A material that arrives \*\*10 days late\*\* might cost the project \*nothing\*, if the activity it feeds has 10 days of schedule float to absorb it.



A material that's only \*\*2 days late\*\* can \*\*halt commissioning\*\*, if it sits with zero float directly on the critical path.



Existing trackers cannot tell these two cases apart. They're both just "late."



Triora can — because it doesn't ask \*"is this late?"\* It asks \*"does this lateness reach anything that matters?"\*



\---



\## What Triora Does



Triora ingests a project's schedule, materials, and vendor data, then computes a \*\*Criticality-Weighted Risk Score (CWRS)\*\* for every tracked material — ranking risk not by how late something is, but by how much of that lateness the project can actually absorb.



$$

\\text{CWRS} = P(\\text{delay}) \\times \\left(1 - \\frac{\\text{float}}{\\text{lead time}}\\right) \\times \\text{downstream blast radius}

$$



| Term | What it captures |

|---|---|

| \*\*P(delay)\*\* | Probability this material misses its need-by date — learned from vendor reliability, not guessed |

| \*\*Urgency\*\* (float-adjusted) | How much schedule slack exists to absorb a delay before it matters |

| \*\*Blast radius\*\* | How many downstream activities and milestones depend on this material |



Out of 137 tracked materials in our demo project, this consistently surfaces \*\*just 1–2 that are genuinely critical\*\* — while correctly ranking a material with the \*worst vendor reliability score in the dataset\* as low-priority, because it sits on an activity with real schedule float. \*\*That contrast is the proof of the entire thesis, reproducible in the running system, not just claimed on a slide.\*\*



\---



\## Live Demo



| | |

|---|---|

| \*\*Frontend (Vercel)\*\* | \[triora-xi.vercel.app](https://triora-xi.vercel.app) |

| \*\*Backend API (Render)\*\* | \[triora-zouh.onrender.com](https://triora-zouh.onrender.com) |

| \*\*CV Inference Service (Render)\*\* | \[cverify-ph84.onrender.com](https://cverify-ph84.onrender.com) \*(see note below)\* |

| \*\*Demo Video\*\* | \[Link — YouTube/Loom] |



> \*\*Note on free-tier hosting:\*\* Render's free tier spins down on inactivity, so the first request to the backend or CV service after idle time can take 30–60s to wake up. Subsequent requests are fast. Our CV inference service, in particular, runs reliably but is CPU-slow on free-tier hardware — it's fully built and functional (see Architecture below), and demonstrated locally in our demo video rather than depending on live free-tier latency during judging.



\---



\## Architecture

┌─────────────────────────────────────────────────────────────┐

│ FRONTEND (React + Vite) │

│ │

│ Dashboard Upload Simulate Vendors CV Verify │

│ (triage (CSV → (what-if (reliability (photo → │

│ list) score) engine) learning) evidence) │

└───────────────────────────┬────────────────────────────────────┘

│ REST (JSON)

┌───────────────────────────▼────────────────────────────────────┐

│ BACKEND (FastAPI + SQLite) │

│ │

│ ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐ │

│ │ graph\_service │→│ cpm\_service │→│ cwrs\_service │ │

│ │ builds DAG │ │ forward/back │ │ scores every │ │

│ │ from schedule │ │ pass → float, │ │ material, ranks by │ │

│ │ │ │ critical path │ │ risk, tags status │ │

│ └──────────────┘ └──────────────┘ └─────────────────────┘ │

│ │

│ ┌───────────────────┐ ┌────────────────────────────────┐ │

│ │ simulation\_service │ │ vendor\_service │ │

│ │ re-runs the full │ │ Bayesian-ish reliability update │ │

│ │ engine on a │ │ from real job outcomes — this │ │

│ │ hypothetical change│ │ is what makes P(delay) a │ │

│ │ (vendor swap, │ │ learning signal, not a static │ │

│ │ duration change) │ │ lookup │ │

│ └───────────────────┘ └────────────────────────────────┘ │

└───────────────────────────┬────────────────────────────────────┘

│

┌───────────────────────────▼────────────────────────────────────┐

│ CV INFERENCE SERVICE (FastAPI + YOLOv8) │

│ Site photo → detected construction stage → compared against │

│ expected schedule state → mismatch feeds back into P(delay) │

└─────────────────────────────────────────────────────────────────┘

\### Why this shape



\- \*\*The graph and CPM layer is the actual differentiator.\*\* Most competing approaches predict "is this late" as a classification problem. We treat it as a \*\*structural\*\* problem — build the real dependency graph, run a proper forward/backward CPM pass, and derive float honestly. This is what lets us tell "late but safe" apart from "on-time but critical," live, on any uploaded project — not just our demo data.

\- \*\*The what-if simulator reuses the exact same scoring engine\*\* for a "before" and "after" run — nothing is faked or pre-scripted. Swap a vendor, stretch an activity's duration, and the entire 137-material ranking recalculates in real time. This is the strongest proof that the system is a real engine, not a static score.

\- \*\*Vendor learning closes the loop.\*\* `P(delay)` isn't a number someone typed in once — it updates from recorded job outcomes via a weighted-average rule, so a vendor's reliability score reflects real history and grows more resistant to single-outlier swings as more jobs are recorded.

\- \*\*CV verification extends the evidence layer\*\*, grounding P(delay) updates in physical reality (a site photo) rather than only self-reported vendor status.



\---



\## What's Built vs. Roadmap



We were deliberate about scope rather than claiming more than we could prove. Everything below \*\*Built\*\* is running, tested, and demonstrated in the video — not aspirational.



| Layer | Status |

|---|---|

| Dependency graph + CPM float/critical-path calculation | ✅ Built |

| CWRS scoring engine, applied to any uploaded project (not just our demo data) | ✅ Built |

| CSV upload → live scoring pipeline | ✅ Built |

| What-if simulator (vendor swap, duration change, expedite/delay) | ✅ Built |

| Vendor reliability learning (job-outcome → updated P(delay)) | ✅ Built |

| CV site-photo verification (YOLOv8 stage detection → evidence signal) | ✅ Built, demoed locally (see hosting note above) |

| Document intelligence (auto-extracting evidence from unstructured emails/PDFs) | 🔜 Roadmap |

| Prescriptive recovery optimizer (OR-Tools cost/time-optimal interventions) | 🔜 Roadmap |

| Cross-project inventory rebalancing | 🔜 Roadmap |



\---



\## Tech Stack



\*\*Backend:\*\* Python, FastAPI, SQLAlchemy, SQLite, NetworkX

\*\*Frontend:\*\* React, Vite, React Router, Papaparse

\*\*ML/CV:\*\* YOLOv8, Ultralytics

\*\*Deployment:\*\* Render (backend + CV service), Vercel (frontend)



\---



\## Running Locally



\### Backend

```bash

cd backend

pip install -r requirements.txt --break-system-packages

python -m database.init\_db

uvicorn app:app --reload --port 8000

```



\### Frontend

```bash

cd frontend

npm install

npm run dev

```



Visit `http://localhost:5173`. The app expects the backend at `http://127.0.0.1:8000` by default (see `frontend/src/api/client.js`).



\### Sample data

Test datasets (137 materials, 22 activities, 10 vendors) are in `datasets/` — see `datasets/README.md` for the CSV schema and the specific "story" baked into the sample data that proves the core thesis.



\---



\## The Team



Built by \*\*\[Team Name]\*\* — \[Sahasra Oleti, Ayusha Hongekar, Tanvi Gattani, Sachi Sarda] — for Track 2: Supply Chain, Kaya AI India Hackathon 2026.



Our team came in from Industrial Engineering and Operations Research — which is exactly why we reached for critical-path method and dependency graphs instead of treating this purely as a prediction problem. Decades-old OR ideas, paired with an AI layer that lets them act on live, messy, real-world data — that pairing is the whole bet behind Triora.



\---



\## Round 1 Proposal



The full written proposal, pitch deck, and original insight write-up are in \[`docs/round1\_proposal.md`](docs/round1\_proposal.md).

