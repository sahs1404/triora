# Triora

**40 alerts. Only 2 matter.**

Construction material risk triage for the AI-native supply chain.

Built for the **Kaya AI India Hackathon 2026 — Track 2: Supply Chain**.

[Live Demo](https://triora-xi.vercel.app) · [Backend API](https://triora-zouh.onrender.com)

---

## Overview

Construction projects deal with hundreds of material packages at any given time — steel, switchgear, ductwork, fasteners, equipment, and more. A typical project can have dozens of materials showing some kind of delay signal: a late vendor update, a missed submittal date, or a shipment that is running behind schedule.

Most tracking systems treat these signals similarly. If something is late, it gets flagged.

The problem is that **not every late material is actually a project risk**.

A material that arrives 10 days late may have no impact if the activity using it has 10 days of schedule float. On the other hand, a material that is only two days late could delay commissioning if it is required for an activity sitting directly on the critical path.

Triora is built around this distinction.

Instead of asking:

> Is this material late?

Triora asks:

> **If this material is late, does the delay actually reach something that matters?**

---

## The Core Idea

Triora combines project dependencies, schedule information, material data, and vendor reliability to calculate a **Criticality-Weighted Risk Score (CWRS)** for each tracked material.

The score is based on three main factors:

* Probability that the material will miss its need-by date
* The amount of schedule float available to absorb the delay
* The downstream impact of the material on the rest of the project

Conceptually:

$$
\text{CWRS} =
P(\text{delay})
\times
\left(1-\frac{\text{float}}{\text{lead time}}\right)
\times
\text{downstream blast radius}
$$

The three components capture different aspects of risk:

| Component                  | What it captures                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **P(delay)**               | Probability that the material will miss its need-by date, based on vendor reliability and available evidence |
| **Float-adjusted urgency** | How much schedule slack exists before a material delay starts affecting the project                          |
| **Blast radius**           | How many downstream activities and milestones depend on the material                                         |

This means a material with a poor vendor history does not automatically become the highest-risk item. Its actual position in the project schedule matters.

In our demo project, Triora tracks **137 materials across 22 activities and 10 vendors**. The system narrows these down to a small number of materials that have meaningful project-level risk.

---

## Why the Dependency Graph Matters

The key differentiator in Triora is that we do not treat material delay purely as a prediction problem.

The project schedule is represented as a dependency graph, after which we use the **Critical Path Method (CPM)** to calculate activity timings and schedule float.

This gives us a structural view of the project.

For example:

* Material A may be 10 days late but feed an activity with 12 days of float.
* Material B may be only 2 days late but feed an activity with zero float on the critical path.

A simple delay-based system would likely rank A as more urgent.

Triora can rank B higher because its delay has a much greater chance of reaching a project milestone.

This is what allows the system to distinguish between **"late but safe"** and **"slightly late but critical."**

---

## What Triora Does

The system currently supports four main workflows.

### 1. Risk Triage

Upload project schedule and material data and generate a ranked list of materials based on their project-level risk.

The scoring engine can be applied to new project data rather than being limited to the sample dataset.

### 2. What-If Simulation

Triora can simulate changes such as:

* Switching a vendor
* Changing an activity duration
* Expediting a material
* Introducing an additional delay

The system reruns the same dependency, CPM, and CWRS pipeline after the change, allowing users to see how the project's risk ranking changes.

### 3. Vendor Reliability Learning

Vendor reliability is updated from historical job outcomes.

Instead of treating vendor reliability as a fixed value, the system updates the estimate as more outcomes are recorded. This allows the probability of delay to gradually reflect observed vendor performance.

### 4. Site Photo Verification

The CV service uses YOLOv8 to detect construction stages from site photographs.

The detected stage can then be compared with the expected state of the project schedule, providing an additional source of evidence when assessing delay risk.

---

## Architecture

```text
                         FRONTEND
                    React + Vite
                           |
                           | REST / JSON
                           v
                 -----------------------
                 |       BACKEND       |
                 | FastAPI + SQLite    |
                 -----------------------
                    |       |       |
                    v       v       v
                 Graph     CPM     CWRS
                Service  Service  Service
                    |       |       |
                    +-------+-------+
                            |
                    Simulation Service
                            |
                    Vendor Service
                            |
                            v
                 -----------------------
                 |   CV INFERENCE     |
                 | FastAPI + YOLOv8   |
                 -----------------------
                            |
                       Site Photo
                            |
                            v
                  Construction Stage
```

### Backend

The backend is divided into several services.

**Graph Service**

Builds the project's dependency graph from the uploaded schedule.

**CPM Service**

Runs the forward and backward passes required for Critical Path Method calculations and derives activity float and critical-path information.

**CWRS Service**

Calculates the Criticality-Weighted Risk Score for each material and ranks the resulting risks.

**Simulation Service**

Reruns the complete scoring pipeline after hypothetical project changes such as vendor swaps or activity-duration changes.

**Vendor Service**

Updates vendor reliability estimates based on historical job outcomes.

### CV Inference Service

The CV component runs separately using FastAPI and YOLOv8.

A site photograph is processed to identify the construction stage. This can then be compared with the expected project state and used as an additional evidence signal for delay assessment.

---

## What's Built

| Component                                  | Status                         |
| ------------------------------------------ | ------------------------------ |
| Dependency graph and CPM float calculation | Built                          |
| Critical-path identification               | Built                          |
| CWRS scoring engine                        | Built                          |
| CSV upload and live scoring pipeline       | Built                          |
| What-if simulation                         | Built                          |
| Vendor reliability learning                | Built                          |
| CV site-photo verification                 | Built and demonstrated locally |
| Document intelligence for emails and PDFs  | Planned                        |
| Prescriptive recovery optimization         | Planned                        |
| Cross-project inventory rebalancing        | Planned                        |

We have deliberately separated implemented functionality from future work. The components marked as built are running in the current system and were demonstrated during development.

---

## Live Demo

**Frontend:** [triora-xi.vercel.app](https://triora-xi.vercel.app)

**Backend API:** [triora-zouh.onrender.com](https://triora-zouh.onrender.com)

**CV Inference Service:** [cverify-ph84.onrender.com](https://cverify-ph84.onrender.com)

**Demo Video:** Coming soon

The backend and CV service are hosted on Render's free tier. Because the services can spin down after periods of inactivity, the first request after an idle period may take some time to respond.

The CV inference service is also CPU-bound on the free-tier hardware. It is fully implemented and functional, and the complete workflow is demonstrated locally in our project demo.

---

## Tech Stack

**Backend**

Python, FastAPI, SQLAlchemy, SQLite, NetworkX

**Frontend**

React, Vite, React Router, PapaParse

**Machine Learning / Computer Vision**

YOLOv8, Ultralytics

**Deployment**

Vercel, Render

---

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages
python -m database.init_db
uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

By default, it expects the backend to be running at:

```text
http://127.0.0.1:8000
```

The API configuration can be found in:

```text
frontend/src/api/client.js
```

### Sample Data

The repository includes sample datasets containing:

* 137 materials
* 22 activities
* 10 vendors

The datasets are available in the `datasets/` directory.

See `datasets/README.md` for the CSV schema and information about the example scenario used to demonstrate the risk-triage workflow.

---

## Project Structure

```text
Triora/
├── backend/
│   ├── services/
│   ├── database/
│   └── app.py
│
├── frontend/
│   ├── src/
│   └── ...
│
├── datasets/
│   └── README.md
│
├── docs/
│   └── round1_proposal.md
│
└── README.md
```

---

## Team

Built by **Sahasra Oleti, Ayusha Hongekar, Tanvi Gattani, and Sachi Sarda** for the **Kaya AI India Hackathon 2026 — Track 2: Supply Chain**.

We come from the Industrial Engineering and Operations Research program at IIT Bombay. That background influenced one of the central decisions behind Triora: rather than treating supply-chain risk purely as a prediction problem, we model the underlying project structure using dependency graphs and Critical Path Method.

The goal was to combine established Operations Research techniques with machine learning and real-world project data to make risk signals more useful for decision-making.

---

## Future Work

There are several directions we would like to explore further:

* Automatically extracting schedule and risk signals from emails, PDFs, and other unstructured project documents
* Adding a prescriptive optimization layer to recommend cost- and time-efficient recovery actions
* Extending the system to rebalance inventory across multiple projects
* Improving the CV pipeline and incorporating richer site-level evidence
* Learning more sophisticated vendor delay models from larger historical datasets

---

## Project Documentation

The original Round 1 proposal and supporting documentation are available in:

`docs/round1_proposal.md`
