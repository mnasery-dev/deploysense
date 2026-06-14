# Pre-Deployment Risk Assessment: release-1174

## 1. Current Deployment Analysis

### Files Changed
**Core Application Logic:**
- `NrqlConditionController.kt` (+4 -4): Core controller handling NRQL condition creation/updates
- `RpmNrqlController.kt` (+4 -4): RPM-specific NRQL condition controller

**Test Files (Non-Production):**
- `no_ff.http` (2 files): HTTP test definitions
- `no_ff.log` (2 files): HTTP test expected outputs

**Classification:** 2 core application files + 4 test files = **Low structural risk** (focused change)

### Code Diff Size
- **Total Lines:** +151 / -11 (net +140)
- **Production Code:** +8 / -8 (net 0) — **Micro change**
- **Test Code:** +143 / -3 — Test coverage expansion
- **Single commit** with clear, isolated scope

**Assessment:** Micro-scale production change with extensive test coverage addition.

### Semantic/Contextual Analysis

**Change Purpose:** Feature flag validation logic refinement for `disable_event_creation` field

**Before:**
```kotlin
// Checks if disableEventCreation field is set (any value including null)
if (condition.terms.orEmpty().any { it.disableEventCreation != null })
```

**After:**
```kotlin
// Only checks if disableEventCreation is explicitly set to true
if (condition.terms.orEmpty().any { it.disableEventCreation == true })
```

**Behavioral Impact:**
- **Previous logic:** Required feature flag for ANY modification to `disable_event_creation` (including setting to `false` or `null`)
- **New logic:** Only requires feature flag when setting to `true`
- **User Impact:** Allows users WITHOUT feature flag to clear/disable event creation settings (set to `false`)

**Risk Vectors:**
1. ✅ **Logic is more permissive** — reduces gate-keeping on flag-disabled accounts
2. ⚠️ **Authorization bypass risk** — If feature flag was intended as hard gate, this weakens it
3. ✅ **Symmetric changes** — Applied consistently across 2 controllers (4 call sites total)
4. ✅ **Test coverage** — New tests explicitly validate both `true` and `false` pathways without FF
5. ⚠️ **Feature flag semantics** — Assumes FF controls enabling feature, not controlling field modification

### Time of Deployment
- **Scheduled:** Wednesday 2026-06-10 02:58:33 UTC
- **Day of week:** Mid-week (Wednesday) ✅
- **Time:** 02:58 UTC (early morning, low traffic) ✅
- **Pattern:** Matches clean deploy at `release-1171` (2026-06-03 03:10:21) ✅

**Assessment:** **Optimal deployment window** — off-peak hours, mid-week, consistent with successful historical pattern.

### Blast Radius
**Connected Services:** 47 entities across:
- **APM Applications:** 9 (beyond-api-v2-web, nrql-query-gateway, alerts-graphql-service, etc.)
- **Kafka Topics:** 2 (alert_condition_crud in both regions)
- **DB Clusters:** 1 (alerts-conditions)
- **S3 Buckets:** 1 (archived-conditions-production)
- **Uninstrumented Services:** 2 (cssp-customer-impact-account-service)
- **Containers:** 11 (condition-api instances)
- **Workloads:** 21 (test transactions and monitoring workloads)

**Critical Dependency Chain:**
```
condition-api → alert_condition_crud (Kafka) → alerts-conditions (DB)
              ↓
         beyond-api-v2-web (upstream consumer)
              ↓
         alerts-graphql-service
```

**Failure Propagation Risk:** Medium — Changes authorization logic that could affect downstream event creation/publishing patterns.

---

## 2. Historical Failure Analysis

### Pattern Recognition Across Failed Deployments

#### release-1164 (BOTH regions, infrastructure failure)
- **Change:** Dependency endpoint migration (`internal-dirac-unauthed` → `internal-dirac`)
- **Impact:** Infrastructure configuration change affecting external service discovery
- **Alert Pattern:** Silent SRE agent change detection (expected)
- **Root Cause Category:** **External dependency/configuration**

#### release-1163 (SUCCESS with error rate alerts)
- **Change:** Added `entity_count` field, dependency version bump (ace-condition 4.18.0→4.19.0)
- **Impact:** Error rate deviations at +8min and +59min post-deploy
- **Alert Pattern:** Baseline deviation on error rate (actual operational issue)
- **Root Cause Category:** **Dependency version incompatibility or query load**

#### release-1162 (FAILURE, multiple attempts)
- **Change:** Null value threshold scope handling, dependency bump (ace-condition 4.17.5→4.18.0)
- **Impact:** Multiple redeploy attempts, error rate alerts
- **Alert Pattern:** Error rate baseline deviations persisting
- **Root Cause Category:** **Complex logic change + dependency coupling**

### Systemic Patterns Identified

| Pattern | Occurrences | Severity |
|---------|-------------|----------|
| **Dependency version bumps causing errors** | 2/3 problematic releases | High correlation |
| **Error rate baseline deviations** | release-1163, release-1162 | Critical indicator |
| **Silent SRE alerts (change detection)** | All releases | Expected, not actionable |
| **Configuration/endpoint changes** | release-1164 | Infrastructure-level risk |
| **Complex conditional logic changes** | release-1162 | Moderate risk when combined with deps |

### Critical Observation
**ace-condition dependency bumps correlate strongly with error rate issues:**
- release-1163: 4.18.0→4.19.0 (error rate alerts)
- release-1162: 4.17.5→4.18.0 (error rate alerts + failure)

**Current release:** No dependency version changes ✅

---

## 3. Dimension Comparison & Risk Matrix

| Dimension | Current Deployment Details | Historical Pattern Correlation | Risk Rating | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Files Changed** | 2 core controllers (NrqlConditionController, RpmNrqlController) + 4 test files | Similar scope to release-1162 (focused logic change) but without dependency changes | **🟡 LOW-MEDIUM** | Focused on authorization logic; similar file count to problematic releases but better isolated |
| **Diff Size** | +151/-11 total, +8/-8 production (net 0 production LOC) | Micro-change in production; smaller than release-1163 (+1860/-139) and release-1162 (+2939/-138) | **🟢 LOW** | Production footprint is minimal; test expansion indicates thoroughness |
| **Semantic Risk** | Authorization gate relaxation (FF check only on `true` not `false`) | Unlike historical failures (deps, endpoints, complex nulls), this is pure conditional logic refinement | **🟡 MEDIUM** | Loosening authorization controls inherently risky but change is symmetric, tested, and well-scoped |
| **Deployment Time** | Wednesday 02:58 UTC (off-peak, mid-week) | Matches clean deploy pattern (release-1171: Wed 03:10 UTC); problematic deploys at varied times | **🟢 LOW** | Optimal window; mid-week off-peak has 100% clean deploy history in dataset |
| **Blast Radius** | 47 connected entities including Kafka, DB, APM services | Condition API is central to alerting infrastructure; similar to all historical deploys | **🟡 MEDIUM** | Inherent to service role; no expansion of blast radius vs. historical baseline |

---

## 4. Red Flags & Final Recommendations

### Risk-Prone Lines & Code Points

#### 🔴 **HIGH SCRUTINY ZONES:**

**NrqlConditionController.kt:317-318**
```kotlin
if (condition.terms.orEmpty().any { it.disableEventCreation == true }) {
    if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
```
**Risk:** Accounts without FF can now set `disable_event_creation: false` without validation. If downstream Kafka consumers or event processors expect FF-gated behavior, this could cause:
- Event creation when not expected
- Missing events in analytics pipelines
- Inconsistent state between condition config and runtime behavior

**NrqlConditionController.kt:394** (PATCH endpoint)
```kotlin
if (body.terms?.value.orEmpty().any { it.disableEventCreation?.value == true }) {
```
**Risk:** Same authorization bypass on PATCH operations; potentially higher risk as PATCH is used for incremental updates.

**RpmNrqlController.kt:195, 275** (RPM variants)
**Risk:** Identical changes in RPM controller; doubles surface area but validates consistency.

---

### Evidence-Based Flags (Pure History)

#### 🟢 **POSITIVE INDICATORS:**
1. ✅ **No dependency version changes** — Primary correlation with historical errors absent
2. ✅ **Optimal deployment timing** — 100% success rate for Wednesday 03:XX UTC window
3. ✅ **Micro production footprint** — Net-zero LOC change in production code
4. ✅ **Extensive test coverage** — +143 lines of test code validating both pathways
5. ✅ **Single focused commit** — Clear intent, no scope creep
6. ✅ **Prior successful deploy** — release-1174 already deployed once cleanly (2026-06-10 02:57:59)

#### 🟡 **CAUTION INDICATORS:**
1. ⚠️ **Authorization logic relaxation** — Loosening gates historically problematic (not in dataset but general SRE principle)
2. ⚠️ **Feature flag semantics shift** — Changing FF meaning from "controls field" to "enables true value only"
3. ⚠️ **Complex service mesh** — 47 connected entities amplify any behavioral change
4. ⚠️ **Critical path service** — Condition API is core to alerting infrastructure

#### 🔴 **CONCERNING PATTERNS (from history):**
1. ❌ **Logic changes in controllers** — release-1162 had similar controller logic changes + errors
2. ❌ **Error rate baseline deviations** — 2/3 recent releases triggered error rate alerts
3. ❌ **Silent failure modes possible** — Authorization bugs may not immediately surface

---

### Go/No-Go Recommendation

## ✅ **PROCEED WITH ENHANCED MONITORING**

### Confidence Level: **75%** (Medium-High)

### Rationale:
1. **Strong positive signals outweigh risks:** No dependency changes, optimal timing, clean prior deploy, micro footprint
2. **Historical failure modes not present:** Primary correlations (dependency bumps, config changes) absent
3. **Test coverage validates behavior:** New tests explicitly cover both pathways
4. **Previous identical deploy succeeded:** release-1174 at 02:57:59 was clean

### MANDATORY CONDITIONS:

#### Pre-Deploy Requirements:
- [ ] **Verify rollback plan:** Ensure `release-1173` is tagged and deployable within 5 minutes
- [ ] **Confirm feature flag state:** Validate `DISABLE_EVENT_CREATION_APIS` FF configuration across accounts
- [ ] **Alert runbook ready:** On-call engineer briefed on authorization change semantics

#### Deploy-Time Monitoring (First 30 minutes):
```
CRITICAL METRICS:
- Error rate baseline (primary failure indicator from history)
- Alert condition CRUD operation latency (P50, P95, P99)
- Kafka topic lag: alert_condition_crud (both regions)
- Feature flag evaluation errors/exceptions
- HTTP 4xx rate on condition API endpoints (authorization errors)

WATCH FOR:
- Error rate deviation >10% from baseline (release-1163 pattern)
- Increased 403/401 errors (authorization misconfiguration)
- Kafka consumer lag spikes (event flow disruption)
- Database connection pool exhaustion (query pattern change)
```

#### Canary Strategy (RECOMMENDED):
1. Deploy to **us-that-paul** first (matches historical pattern)
2. Monitor for 15 minutes
3. Validate test transaction workloads (21 workloads in blast radius)
4. Deploy to **us-fresh-mint** if clean

#### Rollback Triggers:
- Error rate >5% above baseline for >3 minutes
- HTTP 5xx rate >1% for >2 minutes
- Any critical alert violation (non-Silent SRE)
- Kafka consumer lag >10,000 messages
- Database query timeout rate >0.1%

---

### Additional Safeguards:

**Validate in staging/pre-prod:**
```bash
# Test scenarios:
1. Create condition with disable_event_creation: true (WITHOUT FF) → Should fail
2. Create condition with disable_event_creation: false (WITHOUT FF) → Should succeed (NEW)
3. PATCH condition to false from true (WITHOUT FF) → Should succeed (NEW)
4. Verify Kafka events published correctly in all scenarios
```

**Communication:**
- Notify Detection Configuration team of deploy start
- Keep #alerting-incidents channel open
- Prepare rollback announcement template

---

### Final Risk Score: **5.5/10** (Medium Risk, Acceptable with Monitoring)

**Proceed with deployment but maintain heightened vigilance for first 30 minutes post-deploy.**
