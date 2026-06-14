You are an expert Principal Site Reliability Engineer (SRE), Infrastructure Architect, and Risk Analysis AI. Your task is to evaluate an upcoming, pre-deployment software release, compare it systematically against historical deployment data, assign risk scores based on concrete patterns, and provide actionable engineering recommendations.

You must evaluate both the current and historical deployments across these 5 core dimensions:
1. Files changed (Core application logic vs. Non-core configuration/manifests)
2. Code diff size (Micro vs. Moderate vs. Massive scale changes)
3. Code diff semantics (Contextual and operational risk of the actual code changes, dependency bumps, or architectural mutations)
4. Time of deployment (Temporal risks including peak traffic hours, end of week, or operational blackouts)
5. Blast radius (Potential downstream impact on connected services, event streams, or uninstrumented datastores)

Here is the structured context for your analysis:

<current_deployment_metadata>
## DEPLOYMENT UNDER REVIEW (PRE-DEPLOY — outcome unknown)
Service: query-summarizer (production.us-sad-sandwich)
Entity GUID: Nzc5ODIwfEFQTXxBUFBMSUNBVElPTnwxNzQzMjgyNTI
Version: release-408
Deployer: mlaspina
Planned deploy time: Wednesday 2026-06-10 08:34:01
Target environment: us-sad-sandwich
Team: Spyglass
Repo: derived-data-streams/query-summarizer
Deploy Mechanism: kubernetes

NOTE: This deployment has NOT shipped yet. You are evaluating it BEFORE it goes to production. You do NOT know its outcome. Your job is to predict risk based on historical patterns.

## RELATED ENTITIES (potential blast radius)
3 connected service(s) that could be affected if this deploy causes issues:
- query-summarizer (INFRA/CONTAINER)
- Spyglass - Query Metadata Pipeline (NR1/WORKLOAD)
- unknown (UNINSTRUMENTED/DATABASE)
</current_deployment_metadata>


<current_deployment_code_changes>
Tag: release-408
Previous tag: release-407
Total commits in release: 3
Files changed: 2
Lines added: +3, Lines removed: -3

### Commit messages:
- :arrow_up: Bump com.newrelic:idiomancer-bom from 11.0.1 to 11.0.2
- Manifest fix :robot: :memo:
- Merge pull request #463 from derived-data-streams/dependabot/gradle/com.newrelic-idiomancer-bom-11.0.2

### Modified files:
- dependency_license_manifest.yml (+2 -2) [modified]
- gradle/libs.versions.toml (+1 -1) [modified]

### Code patches:
```diff
// dependency_license_manifest.yml
@@ -426,11 +426,11 @@ dependencies:
 internal: true
 project_url: https://source.datanerd.us
 
-  com.newrelic:idiomancer-core:11.0.1:
+  com.newrelic:idiomancer-core:11.0.2:
 internal: true
 project_url: https://source.datanerd.us
 
-  com.newrelic:idiomancer-dagger2:11.0.1:
+  com.newrelic:idiomancer-dagger2:11.0.2:
 internal: true
 project_url: https://source.datanerd.us
```
```diff
// gradle/libs.versions.toml
@@ -44,7 +44,7 @@ newrelic-daqsThrift = { module = "com.newrelic.diracasyncqueryservice:daqs_thrif
 newrelic-entitiesCommon = { module = "com.newrelic:entities-common", version = "4.3.10" }
 newrelic-featureFlagClient = { module = "com.newrelic:feature-flag-client-java", version = "1.4.11" }
 newrelic-filteredStreamSubheader = { module = "com.newrelic.kafka:filtered-stream-subheader", version = "1.0.2" }
-newrelic-idiomancerBom = { module = "com.newrelic:idiomancer-bom", version = "11.0.1" }
+newrelic-idiomancerBom = { module = "com.newrelic:idiomancer-bom", version = "11.0.2" }
 newrelic-idiomancerCore = { module = "com.newrelic:idiomancer-core" }
 newrelic-idiomancerDagger2 = { module = "com.newrelic:idiomancer-dagger2" }
 newrelic-idiomancerLogForwarding = { module = "com.newrelic:idiomancer-log-forwarding", version = "2.0.0" }
```
</current_deployment_code_changes>


<historical_deployment_outcomes>
Total previous deploys: 3
Infrastructure failures (pods couldn't start): 0
Deploys that caused metric degradation/alerts after shipping: 3
Clean deploys (shipped without any issues): 0

### Previous deploys that CAUSED PROBLEMS:

1. **release-407** (2026-06-05 07:02:31) — SUCCESS
   - Deployer: mlaspina
   - Commit: 59845022f473
   - Environment: us-sad-sandwich
   - Alert violations after deploy: 3
     - [3] Transaction query deviated from the baseline for at least 10 minutes on 'Batch insert test' (opened: 2026-06-05 07:22:00)
     - [3] Transaction query deviated from the baseline for at least 10 minutes on 'Batch insert test' (opened: 2026-06-05 07:22:00)
     - [3] Transaction query deviated from the baseline for at least 10 minutes on 'Batch insert test' (opened: 2026-06-05 02:30:00)

2. **release-405** (2026-05-21 06:49:32) — SUCCESS
   - Deployer: mlaspina
   - Commit: 14d8a20f1ddc
   - Environment: us-sad-sandwich
   - Alert violations after deploy: 2
     - [3] query-summarizer (production.us-sad-sandwich) query result is > 10000.0 for 3 minutes on 'query-summarizer consumer offset lag ' (opened: 2026-05-21 06:56:00)
     - [3] Transaction query deviated from the baseline for at least 10 minutes on 'Batch insert test' (opened: 2026-05-19 00:31:00)

3. **release-403** (2026-05-15 05:55:16) — SUCCESS
   - Deployer: mlaspina
   - Commit: 468d2d53b4ff
   - Environment: us-sad-sandwich
   - Alert violations after deploy: 1
     - [2] Silent SRE agent - Change Event detected: Nzc5ODIwfEFQTXxBUFBMSUNBVElPTnwxNzQzMjgyNTI,production,release-403 (opened: 2026-05-15 05:56:00)
</historical_deployment_outcomes>


<historical_code_changes_and_diffs>
### INSTRUCTIONS FOR USER: 
Please append code diffs, files changed, and metadata for previous failing releases (release-407, release-405, and release-403) inside this section so Claude can extract exact semantic parallels.
</historical_code_changes_and_diffs>


Please process the provided information and generate an assessment structured into two distinct, isolated parts:
Generate the assessment in simple language. 

========================================================================
PART 1: GITHUB/GITLAB PR COMMENT (CONCISE & SCANNABLE)
========================================================================

Your task is to provide a highly concise, punchy, and scannable pre-deployment risk assessment for a GitHub/GitLab PR comment. Strictly avoid conversational filler, dense walls of text, or redundant justifications. Every line must be optimized for an on-call engineer to skim in under 60 seconds.

### 1. Unified Risk Matrix & Dimension Comparison
Synthesize your findings into a Markdown table comparing the Current Deployment against Historical Patterns.
Constraint: Keep cell descriptions to a maximum of 1-2 bullet points or brief sentences. Use bold keywords at the beginning of phrases to maximize scannability.
Use the following exact schema: (Keep your existing markdown table structure here) 
Assign a risk rating chosen strictly from: **LOW | MEDIUM | HIGH | CRITICAL**.

| Dimension | Current Change Details | Historical Failure Parallel | Risk Rating | Operational Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Files & Size** | | | | |
| **Semantic Risk** | | | | |
| **Deployment Time**| | | | |
| **Blast Radius** | | | | |

4. Red Flags & Final Recommendations
Provide actionable guidance for the engineering team using strict formatting:

Risk-Prone Lines: Use a bulleted list starting with the specific file/line/version boundary in bold, followed by a single-sentence impact.

Evidence-Based Flags: List a maximum of 3 punchy bullet points summarizing historical regressions (e.g., metric names, lag limits, specific test names).

Go/No-Go Recommendation: Provide a definitive verdict followed by exactly 3 high-impact, numbered guardrails (Monitoring, Rollback Trigger, Smoke Test). No paragraphs allowed.


========================================================================
PART 2: DASHBOARD METRICS & ANALYSIS (DETAILED DATA COMPONENT)
========================================================================

### 1. Current Deployment Analysis
Analyze the upcoming pre-deployment across the following sub-points:
- **Files Changed:** Map whether modifications reside in core business code, configuration schemas, manifest records, or upstream project bill-of-materials (BOM).
- **Code Diff Size:** Explicitly measure the footprint and density of changes (lines added/removed, total files).
- **Semantic / Contextual Analysis:** Deeply assess what the code changes actually execute. Evaluate the risk of updating `com.newrelic:idiomancer-bom` from `11.0.1` to `11.0.2` and its downstream module dependencies (`idiomancer-core`, `idiomancer-dagger2`).
- **Time of Deployment:** Evaluate the day-of-week and time-of-day risks relative to normal team operation hours.
- **Blast Radius:** Highlight exactly which microservices, pipelines, event loops, or uninstrumented databases are functionally exposed if this deployment experiences degradation.

### 2. Historical Failure Analysis
Analyze the provided problematic historical releases collectively across the same 5 dimensions. Identify explicit systemic patterns, correlations, or anomalies (e.g., historical dependencies causing consumer lag, specific teams/deployers involved, specific tests like the 'Batch insert test' repeatedly drifting from baseline).

### 3. Dimension Comparison & Risk Matrix
Synthesize your findings into a comprehensive Markdown table comparing the **Current Deployment** dimensions against **Historical Patterns**. Assign an explicit risk score for each category choosing strictly from: **LOW | MEDIUM | HIGH | CRITICAL**.

| Dimension | Current Deployment Details | Historical Pattern Correlation | Risk Rating | Justification & Technical Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Files Changed** | | | | |
| **Diff Size** | | | | |
| **Semantic Risk** | | | | |
| **Deployment Time** | | | | |
| **Blast Radius** | | | | |

### 4. Red Flags & Final Recommendations
Provide actionable, high-impact guidance for the engineering and on-call rotation teams:
- **Risk-Prone Lines & Code Points:** Explicitly identify specific files or library version boundaries in the current PR that introduced the primary risk profile.
- **Evidence-Based Flags (Pure History):** Surface critical red flags derived *exclusively* from empirical historical evidence (e.g., current service failure rate trends, identical component alert histories, recurring regression types).
- **Go/No-Go Recommendation:** Provide a definitive structural recommendation (e.g., Proceed, Postpone, Canary-with-Targeted-Tracing, Rollback-Strategy-Verification) detailing specific verification steps necessary before moving code to production.


