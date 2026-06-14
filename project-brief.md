# AFA 2026 — Project Brief

## Project Name
DeploySense

## One-line description
AI-powered deployment risk analysis that learns from your service's history — what broke, when, and why — to predict if your next deploy is safe to ship.

## What problem are you solving?
Engineers deploy without knowing if their change is risky. No tool currently answers: "Based on everything that happened with past deploys to this service, should I be worried about THIS one?"

We analyzed 2,221 internal deployments across 3 NR accounts and found that 34% of "successful" deploys actually caused production issues (alerts escalated to incidents). These failures concentrate along specific dimensions — certain services, code diff characteristics, deploy timing, and deployment frequency — suggesting patterns that could inform pre-deploy risk assessment. Yet each deploy starts from zero context.

Existing tools solve adjacent problems: GC Deployment Safety Score measures pipeline configuration maturity (static, project-level). GC Deployment Agent explains why a K8s deploy failed (post-failure). Neither predicts whether a specific change is likely to cause problems before it ships.

## Why should we do this?
The data already exists in NR but isn't being used predictively. Change Tracking captures every deployment with metadata (version, commit, user, timing). NrAiIncident records every alert. NrAiIssue tracks escalations. We just need to connect them.

As AI-generated code increases deployment velocity, even peer-reviewed changes can fail due to unexpected factors — environment-specific issues, timing, interaction with recent changes, or service dependencies. Engineers need a data-backed signal — not gut feeling — to decide when to add extra caution (canary, staging-first, senior review) versus shipping with confidence.

## What are we building?
We are building DeploySense, an AI tool that catches risky code changes before they break production, fitting seamlessly into your workflow via GitHub Actions. The moment a developer creates a Pull Request (PR), DeploySense triggers an automated data pipeline to gather telemetry from New Relic, GitHub Enterprise, and Confluence. It extracts the service’s 30-day deployment history, past incident timelines, and code diff characteristics. Crucially, it queries New Relic's topology maps to identify downstream dependencies, ensuring the system understands the entire structural blast radius of the change.

All of this data is passed to Claude, our AI reasoning engine, which compares the incoming code change against historical failure patterns. Claude evaluates multi-factor risks—like dangerous deployment timing windows, re-introduced architectural bugs, or changes that threaten to trigger cascading failures in dependent downstream microservices. Instead of a vague risk score, DeploySense posts an evidence-backed status check directly on the GitHub PR. It outlines explicit red flags, cites historical version and incident IDs as concrete proof, and provides clear, actionable advice on how to deploy safely (e.g., routing through staging first, executing a canary release, or requesting a senior peer review).


## Scale and scope
GitHub Action Integration: CI/CD workflow code that hooks into PR lifecycles to trigger the risk analysis and post markdown summaries back as PR status checks.
New Relic Data Connector: A Python module utilizing the NerdGraph API to pull Change Tracking, NrAiIncident, and NrAiIssue logs within a 30-day time window.
GitHub Enterprise API Client: Authentication and data fetching scripts to parse code diff size and complexity from changelog URLs.
Topology Mapping: Queries New Relic's entity relationships API to map downstream dependencies and identify which service graphs are sitting in the direct blast radius of the deployment.
Connectivity Verification: A live, fully instrumented 8-microservice test bed used exclusively to validate API authentication, GraphQL query performance, webhook structures, and distributed tracing topology maps.
Logic Validation (Out-of-Time Backtesting): Because the test bed microservices are placeholders, algorithmic accuracy is judged using an historical backtest. The AI evaluates a pre-labeled real production deployments, predicting risks blindly before validating against known historical outcomes.

## How does AI fit in?
Predicting deployment risk is a blind spot for both traditional rules and classical Machine Learning (ML). While classical ML can find basic statistical correlations (e.g., "large diffs fail 15% more"), it cannot connect relational context.

 - This PR modifies the payment-gateway wrapper. The structural diff characteristics closely match release-1164 (large payload serialization change), which triggered incident #88241 on a Friday last month, causing a 12% cascading latency spike in the downstream checkout-service`
 - The last deploy that failed for this entity wasn't just a large diff—it specifically touched the same config files, targeted the same environment, and was shipped by the same team.
 - CRITICAL RISK: This code change modifies a database model that is heavily queried by downstream checkout-service. Past metrics show that changes to this component spike errors in checkout-service within 5 minutes.

 This kind of multi-factor reasoning across unstructured data (deploy descriptions, incident titles, code change context) is where statistical models break down and LLM reasoning adds value. It also explains why something is risky — not just a number, but actionable reasoning an engineer can evaluate.

## AI tools and technologies
- **Claude** (Sonnet via Anthropic API) — analyzes deployment context, identifies red flags, generates evidence-backed recommendations
- **Claude Code** — spec-driven development, data exploration
- **New Relic NerdGraph API** — Change Tracking events, NrAiIncident, NrAiIssue, entity relationships, Transaction metrics
- **GitHub Actions** — automated PR-level risk analysis triggered on deploy
- **GitHub Enterprise API** — code diff retrieval via changelog URLs and commit SHAs from Change Tracking

## How will we judge success?
1. Prediction Accuracy (The Backtest): When the AI flags a change as HIGH or CRITICAL risk, it needs to be right. In our historical data, at least 3 out of 10 deployments with those exact same risk factors actually went on to cause a real alert violation or incident.
2. Evidence-Backed Warnings: The generated red flags must cite explicit, concrete proof directly from the fetched data—specifically naming actual version numbers, deployment dates, and historical incident IDs instead of generic advice.
3. Pipeline Speed (SLA) : The entire end-to-end loop—fetching multi-source data, analyzing it with Claude, and posting the status check—must complete in under 90 seconds so it doesn't slow down the developer's deployment workflow.


## Dependencies and potential blockers
