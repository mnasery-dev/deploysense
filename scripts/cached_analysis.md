# PART 1: GITHUB/GITLAB PR COMMENT (CONCISE & SCANNABLE)

## 🚦 Pre-Deployment Risk Assessment: `release-1174`

### 1. Unified Risk Matrix & Dimension Comparison

| Dimension | Current Change Details | Historical Failure Parallel | Risk Rating | Operational Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Files & Size** | 6 files (+151/-11 lines)<br/>🧪 4 test files, 2 core controllers | ❌ No match: Failed deploys had 13-24 files with massive deletions (3.6k lines) or large additions (2.9k lines) | **LOW** | Micro-scale change; test-heavy footprint (67% test files) |
| **Semantic Risk** | 🔧 Feature flag logic fix<br/>Changes `!= null` → `== true` in FF checks | ✅ Low similarity: Past failures involved config changes, dependency bumps, large features | **MEDIUM** | Logic inversion around FF gating is subtle but affects production validation path; potential for unintended FF bypass |
| **Deployment Time** | ⏰ Wed 02:58 UTC (off-peak) | ✅ Safe window: Historical failures occurred during business hours (13:12, 15:26, 19:50, 21:32) | **LOW** | Deployment during low-traffic window with team coverage |
| **Blast Radius** | 48 connected services<br/>Critical: Alerts GraphQL, beyond-api, Kafka topics, RDS cluster | ⚠️ Same surface area as failed deploys | **MEDIUM** | Condition API is foundational; any logic error impacts alert creation/modification across all accounts |

**Overall Risk Score: MEDIUM** ⚠️

---

### 2. High-Risk Code Points & Empirical Warnings

#### 🎯 **Line-Level Risks (Current PR)**
- **`NrqlConditionController.kt:317` & `RpmNrqlController.kt:195,275`**
  - **Risk:** Changed from `!= null` to `== true` for `disableEventCreation` feature flag check
  - **Concern:** If client sends `disableEventCreation: false` explicitly (not null), old logic would require FF, new logic allows it
  - **Impact:** Could allow users to **clear** the `disable_event_creation` field without FF when it was previously blocked
  - **Mitigation Gap:** Test coverage shows setting to `true` and `false`, but edge case: what if field was previously `true` with FF, then FF removed, and user tries to preserve `true`?

#### 📊 **Purely Historical Flags**
- ⚠️ **56% alert rate** (9/16 deployments triggered alerts)
- 🔴 **Most recent similar-scale deploy** (`release-1161`: 1 commit, SUCCESS) still triggered 1 alert
- ⚠️ **Error rate spikes:** `release-1163` caused baseline deviations on error rate metrics (21:43, 22:36 UTC)
- 🚨 **Infrastructure failures:** 2/16 deploys had infra-level failures (12.5% failure rate)

---

### 3. Final Go/No-Go Verdict

**✅ Recommendation:** **PROCEED WITH ENHANCED MONITORING** (Canary deployment strongly recommended)

**🛡️ Mandatory Guardrails:**

1. **🔍 Active Monitoring (First 30 mins):**
   - Error rate on `SpringController/api/v2/{accountId}/nrql_conditions` endpoints
   - `DisableEventCreationDisabled` error frequency (should NOT increase)
   - Success rate for PATCH operations with `disable_event_creation: false` payload

2. **🧪 Smoke Test Sequence (Immediate post-deploy):**
   ```bash
   # Test 1: Account WITHOUT FF, set disable_event_creation=false → Should 200
   # Test 2: Account WITHOUT FF, set disable_event_creation=true → Should 403
   # Test 3: Account WITH FF, set disable_event_creation=true → Should 200
   ```

3. **⏱️ Rollback Trigger:** If error rate increases >5% baseline OR DisableEventCreationDisabled errors spike unexpectedly, initiate immediate rollback

**⚠️ Red Flag to Watch:** The logic change is **inverse** in nature (blocking on `!= null` vs `== true`). This pattern has high potential for boolean logic errors. Validate FF evaluation behavior in production under load.

---

# PART 2: DASHBOARD METRICS & ANALYSIS (DETAILED DATA COMPONENT)

## 1. Current Deployment Analysis (`release-1174`)

### Files Changed
**Core Application Logic:**
- `src/main/kotlin/com/newrelic/alert/conditions/NrqlConditionController.kt` (+4/-4)
- `src/main/kotlin/com/newrelic/alert/conditions/rpm/controller/RpmNrqlController.kt` (+4/-4)

**Test/Configuration Files:**
- `src/http_tests/rpm/term_disable_event_creation/no_ff.http` (+1/-1)
- `src/http_tests/rpm/term_disable_event_creation/no_ff.log` (+1/-1)
- `src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.http` (+30/-0)
- `src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.log` (+111/-1)

**Classification:** 67% test files, 33% core controllers. **Zero** infrastructure/manifest changes.

---

### Code Diff Size
- **Total Files:** 6
- **Lines Added:** +151
- **Lines Removed:** -11
- **Net Change:** +140 lines
- **Density:** Micro-scale change. Bulk of additions are test expectations (142 lines in `.log` files)
- **Actual Logic Changes:** 8 lines across 2 controller files

**Scale Classification:** **MICRO** (actual business logic: 8 lines; rest is test scaffolding)

---

### Semantic / Contextual Analysis

**Change Summary:**
The deployment modifies feature flag validation logic for the `disable_event_creation` field in NRQL alert conditions.

**Before:**
```kotlin
if (condition.terms.orEmpty().any { it.disableEventCreation != null }) {
    if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
        return DisableEventCreationDisabled.failure().toResponse(tx)
    }
}
```

**After:**
```kotlin
if (condition.terms.orEmpty().any { it.disableEventCreation == true }) {
    if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
        return DisableEventCreationDisabled.failure().toResponse(tx)
    }
}
```

**Semantic Impact:**
- **Old behavior:** Any explicit value for `disableEventCreation` (including `false`) required the feature flag
- **New behavior:** Only setting `disableEventCreation = true` requires the feature flag
- **Intent:** Allow users to **clear/disable** the field (`false`) without needing the FF, while still gating the **enable** operation (`true`) behind FF

**Risk Analysis:**
1. **Positive:** Aligns with typical FF patterns (gate new functionality, not removal)
2. **Concern:** Boolean logic inversions are historically error-prone
3. **Test Coverage:** New tests validate:
   - Setting to `true` without FF → 403 (blocked) ✅
   - Setting to `false` without FF → 200 (allowed) ✅
   - GET after PATCH to `false` → Returns `false` ✅

**Dependencies:** No library version changes. No external service contract modifications.

**Operational Risk Factors:**
- Affects 2 API endpoints: `/api/v2/{accountId}/nrql_conditions` and RPM legacy endpoint
- Touches CREATE and PATCH operations
- Involves feature flag evaluation (runtime configuration dependency)

---

### Time of Deployment
- **Planned Time:** Wednesday 2026-06-10 02:58:33 UTC
- **Day of Week:** Mid-week (Wednesday) ✅
- **Time of Day:** ~3 AM UTC
  - US Eastern: ~10 PM Tuesday (off-peak)
  - US Pacific: ~7 PM Tuesday (moderate)
  - Europe: ~4 AM Wednesday (off-peak)
  
**Traffic Analysis:** Off-peak for primary US customer base. European early morning (minimal usage).

**Operational Context:**
- Detection Configuration team deployment
- Deployer: gfuentes (has clean deploy history in dataset)
- No blackout period indicated
- Wednesday provides 2 business days for stabilization before weekend

**Risk Assessment:** **LOW** temporal risk. Optimal deployment window.

---

### Blast Radius

**Directly Impacted Service:** `Condition API (production)`

**Connected Downstream Services (48 total):**

**CRITICAL (High-Severity Impact):**
1. **Alerts GraphQL Service** (production) - Primary customer-facing alert configuration interface
2. **beyond-api-v2-web** (3 environments) - Alert policy/condition CRUD operations
3. **alert_condition_crud** (Kafka topics: us-that-paul, us-fresh-mint) - Event streaming for condition changes
4. **alerts-conditions** (RDS cluster) - Primary datastore for alert conditions
5. **Condition Cleanup Service** - Automated condition lifecycle management

**MODERATE (Transitive Impact):**
6. **nrql-query-gateway** (2 environments) - Query validation/execution
7. **feature-flag-api** - FF evaluation dependency
8. **entitlement-service** - Account permission validation
9. **cssp-customer-impact-account-service** (3 environments) - Customer impact tracking

**MONITORING/OBSERVABILITY:**
10. Multiple NR1 Workloads and test transactions (35+ entities)
11. Container infrastructure (multiple INFRA/CONTAINER entities)

**UNINSTRUMENTED (Unknown Impact):**
12. `cssp-customer-impact-account-service.vip.cf.nr-ops.net` (HTTP)
13. `synthetics.newrelic.com` (HTTP)
14. `archived-conditions-production.s3.amazonaws.com` (S3)

**Failure Cascade Risk:**
- **Primary:** Logic error → Invalid alert condition states → Kafka event malformation → Downstream consumer failures
- **Secondary:** RDS connection exhaustion if validation loops trigger
- **Tertiary:** Customer-facing alert creation/modification failures across all accounts

**Mitigation Factors:**
- Change is FF-gated behavior (affects subset of accounts)
- Read operations unaffected
- Database schema unchanged

---

## 2. Historical Failure Analysis

### Pattern Analysis Across Failed Deployments

#### `release-1164` (FAILURE × 2 instances)
- **Files:** 13, **Lines:** +2/-3607 (massive deletion)
- **Change Type:** Infrastructure configuration (Dirac query endpoint migration)
- **Semantic:** Changed `internal-dirac-unauthed` → `internal-dirac` (authentication requirement change)
- **Failure Mode:** Both us-fresh-mint and us-that-paul environments failed
- **Alerts:** "Change Event detected" (Silent SRE agent)
- **Time:** 15:26 UTC (business hours)
- **Pattern:** Configuration change affecting external service dependency

#### `release-1163` (SUCCESS but with 3-4 alerts)
- **Files:** 24, **Lines:** +1860/-139 (large feature addition)
- **Change Type:** New API field (`entity_count`), dependency bump (BouncyCastle 1.80 → 1.80.2)
- **Semantic:** Threshold API expansion with facet validation
- **Failure Mode:** Error rate baseline deviations (21:43, 22:36 UTC)
- **Alerts:** Error rate anomalies + Change Event detection
- **Time:** 21:32-21:36 UTC (late evening US time)
- **Pattern:** Large feature deployment caused transient error spikes

#### `release-1162` (FAILURE + SUCCESS with alerts)
- **Files:** 19, **Lines:** +2939/-138 (massive feature addition)
- **Change Type:** Null value threshold scopes feature
- **Semantic:** Complex validation logic for NRQL facets with null handling
- **Failure Mode:** Multiple deployment attempts, eventual success with monitoring
- **Alerts:** Change Event detection
- **Times:** 03:17 (SUCCESS), 13:12 (FAILURE), 19:50 (FAILURE)
- **Pattern:** Large, complex feature with multiple rollout attempts

#### `release-1161` (SUCCESS with 1 alert)
- **Files:** Unknown from data
- **Alerts:** Change Event detection only
- **Time:** 00:19 UTC (midnight)
- **Pattern:** Baseline alert triggering (change detection)

---

### Systemic Patterns Identified

**Failure Correlations:**
1. **Size Matters:** 100% of FAILURE deployments had >13 files changed and >1000 lines modified
2. **Configuration Risk:** Infrastructure/config changes (Dirac endpoint) caused immediate failures
3. **Large Features:** Complex business logic additions (threshold scopes, entity_count) triggered error rate spikes
4. **Time Sensitivity:** Business hour deployments (13:12, 15:26, 19:50) had higher failure rates
5. **Multi-Environment Risk:** Failures often affected both environments simultaneously

**Alert Patterns:**
- **Silent SRE "Change Event detected":** Triggered on 100% of deployments (baseline noise)
- **Error rate baseline deviations:** Specific to large feature additions (release-1163)
- **56% overall alert rate** (9/16 deployments)

**Success Patterns:**
- Small, focused changes during off-peak hours had better outcomes
- Dependency-only updates (BouncyCastle bump in 1163) succeeded but caused monitoring alerts

---

## 3. Dimension Comparison & Risk Matrix

| Dimension | Current Deployment Details | Historical Pattern Correlation | Risk Rating | Justification & Technical Reasoning |
| :--- | :--- | :--- | :--- | :--- |
| **Files Changed** | 6 files (2 core, 4 test)<br/>Zero config/manifest changes | **LOW correlation**<br/>Failed deploys: 13-24 files<br/>Config-heavy (grandcentral.yml, build.gradle) | **LOW** | Current change is 2.3x-4x smaller than historical failures. No infrastructure config touched. Test-heavy footprint reduces production risk. |
| **Diff Size** | +151/-11 (net +140)<br/>Actual logic: 8 lines<br/>Test scaffolding: 142 lines | **VERY LOW correlation**<br/>Failed deploys: +2939/-138, +2/-3607<br/>Success with alerts: +1860/-139 | **LOW** | Current change is 20x-25x smaller than problematic releases. Micro-scale logic adjustment vs. massive feature additions or deletions in failures. |
| **Semantic Risk** | Feature flag logic inversion<br/>`!= null` → `== true`<br/>Affects validation gating | **MODERATE correlation**<br/>release-1164: Auth change (failed)<br/>release-1162: Validation logic (multiple attempts)<br/>Boolean logic inversions historically risky | **MEDIUM** | While small in size, the change modifies **conditional logic** around feature flags—a critical control plane. Historical validation logic changes (1162) required multiple deployment attempts. Logic inversions are cognitively error-prone. |
| **Deployment Time** | Wed 02:58 UTC<br/>Off-peak, mid-week | **NEGATIVE correlation with failures**<br/>Failures: 13:12, 15:26, 19:50, 21:32 UTC<br/>Success: 00:19, 03:17 UTC (off-peak) | **LOW** | Current timing aligns with successful deployment pattern. Off-peak window provides monitoring buffer. Wednesday provides stabilization runway before weekend. |
| **Blast Radius** | 48 connected services<br/>Kafka topics,
