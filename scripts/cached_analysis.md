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
Service: Condition API (production)
Entity GUID: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3
Version: release-1174
Deployer: gfuentes
Planned deploy time: Wednesday 2026-06-10 02:58:33
Target environment: us-fresh-mint
Team: Detection Configuration
Repo: Alerting/condition-api
Deploy Mechanism: kubernetes

NOTE: This deployment has NOT shipped yet. You are evaluating it BEFORE it goes to production. You do NOT know its outcome.

## RELATED ENTITIES (potential blast radius)
47 connected service(s):
- ACE (NR1/WORKLOAD)
- Test Transaction - WebTransaction/SpringController/api/v2/{accountId}/nrql_conditions (GET) (NR1/WORKLOAD)
- Test Transaction - WebTransaction/SpringController/api/v2/{accountId}/nrql_conditions (GET) copy (NR1/WORKLOAD)
- condition-api (INFRA/CONTAINER)
- beyond-api-v2-web (production.us-fresh-mint) (APM/APPLICATION)
- Condition Cleanup Service (production) (APM/APPLICATION)
- nrql-query-gateway (production.us-that-paul) (APM/APPLICATION)
- alert_condition_crud (us-that-paul-kafka) (INFRA/AWSMSKTOPIC)
- alerts-conditions (INFRA/AWSRDSDBCLUSTER)
- condition-api (INFRA/CONTAINER)
- beyond-api-v2-web (production.us-that-paul) (APM/APPLICATION)
- condition-api (INFRA/CONTAINER)
- Alerts GraphQL Service (production) (APM/APPLICATION)
- archived-conditions-production (INFRA/AWSS3BUCKET)
- Transaction - WebTransaction/SpringController/api/v4/{accountId}/conditions/{familyId} (GET) Test (NR1/WORKLOAD)
- Test Transaction - SpringController/api/v2/{accountId}/nrql_conditions/{conditionFamilyId} (GET) copy (NR1/WORKLOAD)
- feature-flag-api (production.us-fresh-mint) (APM/APPLICATION)
- condition-api (INFRA/CONTAINER)
- condition-api (INFRA/CONTAINER)
- condition-api (INFRA/CONTAINER)
- condition-api (INFRA/CONTAINER)
- condition-api (INFRA/CONTAINER)
- nrql-query-gateway (production.us-fresh-mint) (APM/APPLICATION)
- Transaction - Testing  copy (NR1/WORKLOAD)
- Test Transaction - SpringController/api/v2/{accountId}/nrql_conditions/{conditionFamilyId} (GET) copy copy (NR1/WORKLOAD)
- cssp-customer-impact-account-service.vip.cf.nr-ops.net (UNINSTRUMENTED/HTTPSERVICE)
- Transaction - Testing  copy (NR1/WORKLOAD)
- entitlement-service (production) (APM/APPLICATION)
- compound_alerts_crud (us-fresh-mint-kafka) (INFRA/AWSMSKTOPIC)
- condition-api (INFRA/CONTAINER)
- Test workload from apm data team (NR1/WORKLOAD)
- cssp-customer-impact-account-service (production.us-that-paul) (APM/APPLICATION)
- Test Transaction - SpringController/api/v2/{accountId}/nrql_conditions/{conditionFamilyId} (GET) (NR1/WORKLOAD)
- Transaction - WebTransaction/SpringController/v2/alerts_synthetics_conditions.json (GET) (NR1/WORKLOAD)
- Test Transaction - SpringController/api/v2/{accountId}/nrql_conditions/{conditionFamilyId} (GET) copy copy (NR1/WORKLOAD)
- beyond-api-v2-web (production) (APM/APPLICATION)
- DCON (production) (NR1/WORKLOAD)
- cssp-customer-impact-account-service (production.us-fresh-mint) (APM/APPLICATION)
- Transaction - WebTransaction test (NR1/WORKLOAD)
- Policy Search test txn (NR1/WORKLOAD)
- condition-api (INFRA/CONTAINER)
- Test Mario (NR1/WORKLOAD)
- Transaction - Testing  copy (NR1/WORKLOAD)
- archived-conditions-production.s3.amazonaws.com (UNINSTRUMENTED/HTTPSERVICE)
- condition-api (INFRA/CONTAINER)
- alert_condition_crud (us-fresh-mint-kafka) (INFRA/AWSMSKTOPIC)
- condition-api (INFRA/CONTAINER)
</current_deployment_metadata>


<current_deployment_code_changes>
Tag: release-1174
Previous tag: release-1173
Total commits in release: 1
Files changed: 6
Lines added: +151, Lines removed: -11

### Commit messages:
- Only require disable_event_creation_apis FF for true, not false (#1317)

### Modified files:
- src/http_tests/rpm/term_disable_event_creation/no_ff.http (+1 -1) [modified]
- src/http_tests/rpm/term_disable_event_creation/no_ff.log (+1 -1) [modified]
- src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.http (+30 -0) [modified]
- src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.log (+111 -1) [modified]
- src/main/kotlin/com/newrelic/alert/conditions/NrqlConditionController.kt (+4 -4) [modified]
- src/main/kotlin/com/newrelic/alert/conditions/rpm/controller/RpmNrqlController.kt (+4 -4) [modified]

### Code patches:
```diff
// src/http_tests/rpm/term_disable_event_creation/no_ff.http
@@ -88,7 +88,7 @@ Service-Gateway-Organization-Id: org-a
         "priority": "critical",
         "threshold": "10",
         "time_function": "any",
-        "disable_event_creation": false
+        "disable_event_creation": true
       }
     ],
     "nrql": {
```
```diff
// src/http_tests/rpm/term_disable_event_creation/no_ff.log
@@ -135,7 +135,7 @@ Service-Gateway-Organization-Id: org-a
         "priority": "critical",
         "threshold": "10",
         "time_function": "any",
-        "disable_event_creation": false
+        "disable_event_creation": true
       }
     ],
     "nrql": {
```
```diff
// src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.http
@@ -72,6 +72,28 @@ Service-Gateway-Account-ID: 1
 Service-Gateway-User-ID: 999222
 Service-Gateway-Organization-Id: org-a
 
+{
+  "terms": [
+    {
+      "priority": "critical",
+      "threshold": 100,
+      "operator": "above",
+      "duration": 120,
+      "time_function": "all",
+      "disable_event_creation": true
+    }
+  ]
+}
+
+### Patch a condition's disable event creation to false, no FF. Should 200 (clearing the field doesn't require the FF).
+PATCH http://localhost:10200/api/v2/1/nrql_conditions/1
+Service-Gateway-Login-Context: test-read-write
+Content-Type: application/json
+Service-Gateway-API-Key: abcdefg
+Service-Gateway-Account-ID: 1
+Service-Gateway-User-ID: 999222
+Service-Gateway-Organization-Id: org-a
+
 {
   "terms": [
     {
@@ -84,3 +106,11 @@ Service-Gateway-Organization-Id: org-a
     }
   ]
 }
+
+### Get the condition back; the patch above should have persisted disable_event_creation: false.
+GET http://localhost:10200/api/v2/1/nrql_conditions/1
+Service-Gateway-Login-Context: test-read-write
+Content-Type: application/json
+Service-Gateway-API-Key: abcdefg
+Service-Gateway-Account-ID: 1
+Service-Gateway-User-ID: 999222
```
```diff
// src/http_tests/v2_nrql_conditions/term_disable_event_creation/no_ff.log
@@ -128,7 +128,7 @@ Service-Gateway-Organization-Id: org-a
       "operator": "above",
       "duration": 120,
       "time_function": "all",
-      "disable_event_creation": false
+      "disable_event_creation": true
     }
   ]
 }
@@ -139,4 +139,114 @@ Content-Type: application/json
 {
   "error" : "DisableEventCreationDisabled",
   "message" : "Disable event creation is not enabled for this account"
+}
+
+### Patch a condition's disable event creation to false, no FF. Should 200 (clearing the field doesn't require the FF).
+PATCH http://localhost:10200/api/v2/1/nrql_conditions/1
+Service-Gateway-Login-Context: test-read-write
+Content-Type: application/json
+Service-Gateway-API-Key: abcdefg
+Service-Gateway-Account-ID: 1
+Service-Gateway-User-ID: 999222
+Service-Gateway-Organization-Id: org-a
+
+{
+  "terms": [
+    {
+      "priority": "critical",
+      "threshold": 100,
+      "operator": "above",
+      "duration": 120,
+      "time_function": "all",
+      "disable_event_creation": false
+    }
+  ]
+}
+
+200 OK
+Content-Type: application/json
+
+{
+  "id" : 1,
+  "data_account_id" : 1,
+  "policy_id" : 2,
+  "entity_guid" : "MXxBSU9QU3xDT05ESVRJT058MQ",
+  "name" : "test condition",
+  "enabled" : true,
+  "violation_ttl_seconds" : 300,
+  "product" : "NRQL",
+  "type" : "query",
+  "updated_by" : "",
+  "updated_at" : 500000000000,
+  "created_by" : "",
+  "created_at" : 500000000000,
+  "terms" : [ {
+    "priority" : "critical",
+    "threshold" : 100.0,
+    "operator" : "above",
+    "duration" : 120,
+    "time_function" : "all",
+    "disable_event_creation" : false
+  } ],
+  "settings" : {
+    "query" : "select count(*) from foo",
+    "evaluation_type" : "STREAMING",
+    "aggregation_window" : 60,
+    "value_function" : "single_value",
+    "close_violations_on_expiration" : false,
+    "open_violation_on_expiration" : false,
+    "fill_option" : "none",
+    "aggregation_method" : "EVENT_FLOW",
+    "aggregation_delay" : 120,
+    "title_template" : "Your condition is {{condition.name}}",
+    "ignore_on_expected_termination" : false
+  }
+}
+
+### Get the condition back; the patch above should have persisted disable_event_creation: false.
+GET http://localhost:10200/api/v2/1/nrql_conditions/1
+Service-Gateway-Login-Context: test-read-write
+Content-Type: application/json
+Service-Gateway-API-Key: abcdefg
+Service-Gateway-Account-ID: 1
+Service-Gateway-User-ID: 999222
+
+200 OK
+Content-Type: application/json
+
+{
+  "id" : 1,
+  "data_account_id" : 1,
+  "policy_id" : 2,
+  "entity_guid" : "MXxBSU9QU3xDT05ESVRJT058MQ",
+  "name" : "test condition",
+  "enabled" : true,
+  "violation_ttl_seconds" : 300,
+  "product" : "NRQL",
+  "type" : "query",
+  "updated_by" : "",
+  "updated_at" : 500000000000,
+  "created_by" : "",
+  "created_at" : 500000000000,
+  "terms" : [ {
+    "priority" : "critical",
+    "threshold" : 100.0,
+    "operator" : "above",
+    "duration" : 120,
+    "time_function" : "all",
+    "disable_event_creation" : false
+  } ],
+  "settings" : {
+    "query" : "select count(*) from foo",
+    "evaluation_type" : "STREAMING",
+    "aggregation_window" : 60,
+    "value_function" : "single_value",
+    "close_violations_on_expiration" : false,
+    "open_violation_on_expiration" : false,
+    "fill_option" : "none",
+    "aggregation_method" : "EVENT_FLOW",
+    "aggregation_delay" : 120,
+    "title_template" : "Your condition is {{condition.name}}",
+    "ignore_on_expected_termination" : false
+  }
 }
\ No newline at end of file
```
```diff
// src/main/kotlin/com/newrelic/alert/conditions/NrqlConditionController.kt
@@ -314,8 +314,8 @@ class NrqlConditionController(
             }
         }
 
-        // check for FF if any term sets disableEventCreation
-        if (condition.terms.orEmpty().any { it.disableEventCreation != null }) {
+        // check for FF if any term sets disableEventCreation to true
+        if (condition.terms.orEmpty().any { it.disableEventCreation == true }) {
             if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
                 val disableEventCreationNotEnabled = DisableEventCreationDisabled.failure().toResponse(tx)
                 telemetry?.tx(tx)
@@ -391,8 +391,8 @@ class NrqlConditionController(
             }
         }
 
-        // check for FF if any term sets disableEventCreation
-        if (body.terms?.value.orEmpty().any { it.disableEventCreation?.value != null }) {
+        // check for FF if any term sets disableEventCreation to true
+        if (body.terms?.value.orEmpty().any { it.disableEventCreation?.value == true }) {
             if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
                 val disableEventCreationNotEnabled = DisableEventCreationDisabled.failure().toResponse(tx)
                 telemetry?.tx(tx)
```
```diff
// src/main/kotlin/com/newrelic/alert/conditions/rpm/controller/RpmNrqlController.kt
@@ -192,8 +192,8 @@ class RpmNrqlController(
             }
         }
 
-        // check for FF if any term sets disableEventCreation
-        if (wrapper.nrqlCondition.terms.orEmpty().any { it.disableEventCreation != null }) {
+        // check for FF if any term sets disableEventCreation to true
+        if (wrapper.nrqlCondition.terms.orEmpty().any { it.disableEventCreation == true }) {
             if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
                 return DisableEventCreationDisabled.failure().toResponse(tx)
             }
@@ -272,8 +272,8 @@ class RpmNrqlController(
             }
         }
 
-        // check for FF if any term sets disableEventCreation
-        if (wrapper.nrqlCondition.terms.orEmpty().any { it.disableEventCreation != null }) {
+        // check for FF if any term sets disableEventCreation to true
+        if (wrapper.nrqlCondition.terms.orEmpty().any { it.disableEventCreation == true }) {
             if (!flags.isEnabled(FeatureFlags.DISABLE_EVENT_CREATION_APIS, accountId)) {
                 return DisableEventCreationDisabled.failure().toResponse(tx)
             }
```
</current_deployment_code_changes>


<historical_deployment_outcomes>
Total previous deploys: 16
Infrastructure failures: 2
Deploys that caused alerts: 9
Clean deploys: 5

### Previous deploys that CAUSED PROBLEMS:

1. **release-1164** (2026-05-20 15:26:50) — FAILURE
   - Deployer: mdiener
   - Commit: 0dcc14a30cf8
   - Environment: us-fresh-mint
   - Alert violations: 2
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1164 (opened: 2026-05-20 15:27:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1164 (opened: 2026-05-20 15:27:00)

2. **release-1164** (2026-05-20 15:26:36) — FAILURE
   - Deployer: mdiener
   - Commit: 0dcc14a30cf8
   - Environment: us-that-paul
   - Alert violations: 2
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1164 (opened: 2026-05-20 15:27:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1164 (opened: 2026-05-20 15:27:00)

3. **release-1163** (2026-05-15 21:36:03) — SUCCESS
   - Deployer: broling
   - Commit: fd0d0427468f
   - Environment: us-that-paul
   - Alert violations: 3
     - [3] Metric query deviated from the baseline for at least 5 minutes on 'Error rate' (opened: 2026-05-15 22:36:00)
     - [3] Metric query deviated from the baseline for at least 5 minutes on 'Error rate' (opened: 2026-05-15 21:43:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1163 (opened: 2026-05-15 21:37:00)

4. **release-1163** (2026-05-15 21:32:27) — SUCCESS
   - Deployer: broling
   - Commit: fd0d0427468f
   - Environment: us-fresh-mint
   - Alert violations: 4
     - [3] Metric query deviated from the baseline for at least 5 minutes on 'Error rate' (opened: 2026-05-15 22:36:00)
     - [3] Metric query deviated from the baseline for at least 5 minutes on 'Error rate' (opened: 2026-05-15 21:43:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1163 (opened: 2026-05-15 21:37:00)

5. **release-1162** (2026-05-15 19:50:59) — FAILURE
   - Deployer: broling
   - Commit: 3a52ae56db4f
   - Environment: us-fresh-mint
   - Alert violations: 4
     - [3] Metric query deviated from the baseline for at least 5 minutes on 'Error rate' (opened: 2026-05-15 21:43:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1163 (opened: 2026-05-15 21:37:00)
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1163 (opened: 2026-05-15 21:33:00)

6. **release-1162** (2026-05-15 13:12:06) — FAILURE
   - Deployer: ckunze
   - Commit: 3a52ae56db4f
   - Environment: us-fresh-mint
   - Alert violations: 1
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1162 (opened: 2026-05-15 13:13:00)

7. **release-1162** (2026-05-15 03:17:07) — SUCCESS
   - Deployer: ckunze
   - Commit: 3a52ae56db4f
   - Environment: us-that-paul
   - Alert violations: 1
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1162 (opened: 2026-05-15 03:18:00)

8. **release-1161** (2026-05-14 00:19:48) — SUCCESS
   - Deployer: broling
   - Commit: 92a84039b02a
   - Environment: us-that-paul
   - Alert violations: 1
     - [2] Silent SRE agent - Change Event detected: MTA4ODg2MjN8QVBNfEFQUExJQ0FUSU9OfDY5OTM0MzA3,production,release-1161 (opened: 2026-05-14 00:20:00)

### Clean deploys:
- release-1174 (2026-06-10 02:57:59) by gfuentes
- release-1171 (2026-06-03 03:10:21) by gfuentes
- release-1171 (2026-06-03 03:09:46) by gfuentes
- release-1165 (2026-05-22 00:25:19) by mdiener
- release-1165 (2026-05-22 00:25:16) by mdiener
</historical_deployment_outcomes>


<historical_code_changes_and_diffs>

### release-1164 (2026-05-20 15:26:50) — FAILURE
Tag: release-1164
Previous tag: release-1163
Commits: 1
Files: 13, Lines: +2 -3607
  - NR-563924: migrate Dirac query calls to authenticated internal-dirac endpoint (#1308)
Files:
  - build.gradle (+1 -1)
  - grandcentral.yml (+1 -1)
  - src/http_tests/standards/coverage/simple.http (+0 -87)
  - src/http_tests/standards/coverage/simple.log (+0 -462)
  - src/http_tests/template_matching/coverage/automatic_coverage_recording.http (+0 -128)
  - src/http_tests/template_matching/coverage/automatic_coverage_recording.log (+0 -731)
  - src/http_tests/template_matching/coverage/manual_coverage_recording.http (+0 -124)
  - src/http_tests/template_matching/coverage/manual_coverage_recording.log (+0 -360)
  - src/main/kotlin/com/newrelic/alert/conditions/standards/coverage/controller/CoverageController.kt (+0 -42)
  - src/main/kotlin/com/newrelic/alert/conditions/standards/coverage/service/ConditionEntityCoverageQueryService.kt (+0 -125)
```diff
// build.gradle
@@ -498,7 +498,7 @@ tasks.register('runStaging', JavaExec) {
         fetchVaultValue(environment, 'CORRELATION_FILTER_SERVICE_URL', 'discovery/staging/correlation-filter-service/endpoint')
         fetchVaultValue(environment, 'CSSP_SERVICE_URL', 'discovery/staging/internal-cssp-customer-impact-account-service/endpoint')
         fetchVaultValue(environment, 'THRESHOLD_RECOMMEND_URL', 'discovery/staging/threshold-recommend/endpoint')
-        fetchVaultValue(environment, 'DIRAC_QUERY_API_URL', 'discovery/staging/internal-dirac-unauthed/endpoint')
+        fetchVaultValue(environment, 'DIRAC_QUERY_API_URL', 'discovery/staging/internal-dirac/endpoint')
         fetchVaultValue(environment, 'SCHEDULER_PRIMITIVE_API_URL', 'discovery/staging/scheduler-primitive-api/endpoint')
 
         // Vault values
```
```diff
// grandcentral.yml
@@ -21,7 +21,7 @@ base_environment:
     BEYOND_SERVICE_URL: discovery_path:internal-integrations-api
     REGISTRATION_API_URL: discovery_path:condition-registration-api
     DAQS_1_API_RPC: discovery_path:daqs-query-registrar
-    DIRAC_QUERY_API_URL: discovery_path:internal-dirac-unauthed
+    DIRAC_QUERY_API_URL: discovery_path:internal-dirac
     CORRELATION_FILTER_SERVICE_URL: discovery_path:correlation-filter-service
     RW_DATABASE_URL: discovery_path:ace-condition-db
     RO_DATABASE_URL: discovery_path:ace-condition-db-ro
```
[... truncated]

### release-1164 (2026-05-20 15:26:36) — FAILURE
Tag: release-1164
Previous tag: release-1163
Commits: 1
Files: 13, Lines: +2 -3607
  - NR-563924: migrate Dirac query calls to authenticated internal-dirac endpoint (#1308)
Files:
  - build.gradle (+1 -1)
  - grandcentral.yml (+1 -1)
  - src/http_tests/standards/coverage/simple.http (+0 -87)
  - src/http_tests/standards/coverage/simple.log (+0 -462)
  - src/http_tests/template_matching/coverage/automatic_coverage_recording.http (+0 -128)
  - src/http_tests/template_matching/coverage/automatic_coverage_recording.log (+0 -731)
  - src/http_tests/template_matching/coverage/manual_coverage_recording.http (+0 -124)
  - src/http_tests/template_matching/coverage/manual_coverage_recording.log (+0 -360)
  - src/main/kotlin/com/newrelic/alert/conditions/standards/coverage/controller/CoverageController.kt (+0 -42)
  - src/main/kotlin/com/newrelic/alert/conditions/standards/coverage/service/ConditionEntityCoverageQueryService.kt (+0 -125)
```diff
// build.gradle
@@ -498,7 +498,7 @@ tasks.register('runStaging', JavaExec) {
         fetchVaultValue(environment, 'CORRELATION_FILTER_SERVICE_URL', 'discovery/staging/correlation-filter-service/endpoint')
         fetchVaultValue(environment, 'CSSP_SERVICE_URL', 'discovery/staging/internal-cssp-customer-impact-account-service/endpoint')
         fetchVaultValue(environment, 'THRESHOLD_RECOMMEND_URL', 'discovery/staging/threshold-recommend/endpoint')
-        fetchVaultValue(environment, 'DIRAC_QUERY_API_URL', 'discovery/staging/internal-dirac-unauthed/endpoint')
+        fetchVaultValue(environment, 'DIRAC_QUERY_API_URL', 'discovery/staging/internal-dirac/endpoint')
         fetchVaultValue(environment, 'SCHEDULER_PRIMITIVE_API_URL', 'discovery/staging/scheduler-primitive-api/endpoint')
 
         // Vault values
```
```diff
// grandcentral.yml
@@ -21,7 +21,7 @@ base_environment:
     BEYOND_SERVICE_URL: discovery_path:internal-integrations-api
     REGISTRATION_API_URL: discovery_path:condition-registration-api
     DAQS_1_API_RPC: discovery_path:daqs-query-registrar
-    DIRAC_QUERY_API_URL: discovery_path:internal-dirac-unauthed
+    DIRAC_QUERY_API_URL: discovery_path:internal-dirac
     CORRELATION_FILTER_SERVICE_URL: discovery_path:correlation-filter-service
     RW_DATABASE_URL: discovery_path:ace-condition-db
     RO_DATABASE_URL: discovery_path:ace-condition-db-ro
```
[... truncated]

### release-1163 (2026-05-15 21:36:03) — SUCCESS
Tag: release-1163
Previous tag: release-1162
Commits: 2
Files: 24, Lines: +1860 -139
  - NR-561652: Add entity_count alongside alert_events in threshold APIs (#1306)
  - Refresh dependency license manifest for BouncyCastle 1.80.2 (#1309)
Files:
  - dependency_license_manifest.yml (+3 -3)
  - gradle.properties (+1 -1)
  - src/http_tests/threshold_recommend_mock/mappings/faceted_by_appname_and_entityname.json (+32 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/user_defined_thresholds.log (+6 -6)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/with_alert_events.http (+9 -9)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/with_alert_events.log (+20 -18)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/user_defined_thresholds/validation_errors.log (+9 -9)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scope_invalid.http (+120 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scope_invalid.log (+172 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scoped.http (+155 -0)
```diff
// dependency_license_manifest.yml
@@ -934,7 +934,7 @@ dependencies:
     internal: true
     project_url: https://source.datanerd.us
 
-  com.newrelic.ace:ace-condition:4.18.0:
+  com.newrelic.ace:ace-condition:4.19.0:
     internal: true
     project_url: https://source.datanerd.us
 
@@ -2172,12 +2172,12 @@ dependencies:
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
 
-  org.bouncycastle:bcprov-jdk18on:1.80:
+  org.bouncycastle:bcprov-jdk18on:1.80.2:
     license: MIT
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
 
-  org.bouncycastle:bcutil-jdk18on:1.80:
+  org.bouncycastle:bcutil-jdk18on:1.80.2:
     license: MIT
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
```
```diff
// gradle.properties
@@ -3,7 +3,7 @@
 #
 account-service-thrift.version=3.0.3
 account-user-service-thrift.version=3.0.4
-ace-condition.version=4.18.0
+ace-condition.version=4.19.0
 ace-core.version=11.4.0
 condition-standards-lib.version=1.0.2
 alert-integration-util.version=8.7.2
```
```diff
// src/http_tests/threshold_recommend_mock/mappings/faceted_by_appname_and_entityname.json
@@ -0,0 +1,32 @@
+{
+  "request": {
+    "method": "POST",
+    "url": "/v0/threshold/threshold_request_from_nrql",
+    "bodyPatterns": [
+      {
+        "contains": "SELECT count(*) from foo FACET appName, entityName"
+      }
+    ]
+  },
+  "response": {
+    "status": 200,
+    "jsonBody": {
+      "threshold_list": [
+        {
+          "facets": [
+            "my-app",
+            "host-a"
+          ],
+          "threshold": 80.0
+        },
+        {
+          "facets": [
+            "my-app",
+            "host-b"
+          ],
+          "threshold": 90.0
+        }
+      ]
+    }
+  }
+}
```
```diff
// src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/user_defined_thresholds.log
@@ -431,9 +431,9 @@ Content-Type: application/json
   "title" : "Validation error(s) occurred in your request.",
   "detail" : "1 validation error(s)",
   "errors" : [ {
-    "name" : "UserDefinedThresholdExtraFacets",
-    "reason" : "User-defined threshold must not include facets not in threshold scope but includes: appName",
-    "type" : "UserDefinedThresholdExtraFacets"
+    "name" : "ThresholdExtraFacets",
+    "reason" : "Threshold must not include facets not in threshold scope but includes: appName",
+    "type" : "ThresholdExtraFacets"
   } ]
 }
 
@@ -492,9 +492,9 @@ Content-Type: application/json
   "title" : "Validation error(s) occurred in your request.",
   "detail" : "1 validation error(s)",
   "errors" : [ {
-    "name" : "UserDefinedThresholdMissingNrqlFacets",
-    "reason" : "User-defined threshold must include all facets from threshold scope but is missing: appName",
-    "type" : "UserDefinedThresholdMissingNrqlFacets"
+    "name" : "ThresholdMissingFacets",
+    "reason" : "Threshold must include all facets from threshold scope but is missing: appName",
+    "type" : "ThresholdMissingFacets"
   } ]
 }
 
```
[... truncated]

### release-1163 (2026-05-15 21:32:27) — SUCCESS
Tag: release-1163
Previous tag: release-1162
Commits: 2
Files: 24, Lines: +1860 -139
  - NR-561652: Add entity_count alongside alert_events in threshold APIs (#1306)
  - Refresh dependency license manifest for BouncyCastle 1.80.2 (#1309)
Files:
  - dependency_license_manifest.yml (+3 -3)
  - gradle.properties (+1 -1)
  - src/http_tests/threshold_recommend_mock/mappings/faceted_by_appname_and_entityname.json (+32 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/user_defined_thresholds.log (+6 -6)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/with_alert_events.http (+9 -9)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/with_alert_events.log (+20 -18)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/user_defined_thresholds/validation_errors.log (+9 -9)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scope_invalid.http (+120 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scope_invalid.log (+172 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/with_alert_events/explicit_thresholds/scoped.http (+155 -0)
```diff
// dependency_license_manifest.yml
@@ -934,7 +934,7 @@ dependencies:
     internal: true
     project_url: https://source.datanerd.us
 
-  com.newrelic.ace:ace-condition:4.18.0:
+  com.newrelic.ace:ace-condition:4.19.0:
     internal: true
     project_url: https://source.datanerd.us
 
@@ -2172,12 +2172,12 @@ dependencies:
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
 
-  org.bouncycastle:bcprov-jdk18on:1.80:
+  org.bouncycastle:bcprov-jdk18on:1.80.2:
     license: MIT
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
 
-  org.bouncycastle:bcutil-jdk18on:1.80:
+  org.bouncycastle:bcutil-jdk18on:1.80.2:
     license: MIT
     license_url: https://www.bouncycastle.org/license.html
     project_url: https://www.bouncycastle.org/index.html
```
```diff
// gradle.properties
@@ -3,7 +3,7 @@
 #
 account-service-thrift.version=3.0.3
 account-user-service-thrift.version=3.0.4
-ace-condition.version=4.18.0
+ace-condition.version=4.19.0
 ace-core.version=11.4.0
 condition-standards-lib.version=1.0.2
 alert-integration-util.version=8.7.2
```
```diff
// src/http_tests/threshold_recommend_mock/mappings/faceted_by_appname_and_entityname.json
@@ -0,0 +1,32 @@
+{
+  "request": {
+    "method": "POST",
+    "url": "/v0/threshold/threshold_request_from_nrql",
+    "bodyPatterns": [
+      {
+        "contains": "SELECT count(*) from foo FACET appName, entityName"
+      }
+    ]
+  },
+  "response": {
+    "status": 200,
+    "jsonBody": {
+      "threshold_list": [
+        {
+          "facets": [
+            "my-app",
+            "host-a"
+          ],
+          "threshold": 80.0
+        },
+        {
+          "facets": [
+            "my-app",
+            "host-b"
+          ],
+          "threshold": 90.0
+        }
+      ]
+    }
+  }
+}
```
```diff
// src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/user_defined_thresholds.log
@@ -431,9 +431,9 @@ Content-Type: application/json
   "title" : "Validation error(s) occurred in your request.",
   "detail" : "1 validation error(s)",
   "errors" : [ {
-    "name" : "UserDefinedThresholdExtraFacets",
-    "reason" : "User-defined threshold must not include facets not in threshold scope but includes: appName",
-    "type" : "UserDefinedThresholdExtraFacets"
+    "name" : "ThresholdExtraFacets",
+    "reason" : "Threshold must not include facets not in threshold scope but includes: appName",
+    "type" : "ThresholdExtraFacets"
   } ]
 }
 
@@ -492,9 +492,9 @@ Content-Type: application/json
   "title" : "Validation error(s) occurred in your request.",
   "detail" : "1 validation error(s)",
   "errors" : [ {
-    "name" : "UserDefinedThresholdMissingNrqlFacets",
-    "reason" : "User-defined threshold must include all facets from threshold scope but is missing: appName",
-    "type" : "UserDefinedThresholdMissingNrqlFacets"
+    "name" : "ThresholdMissingFacets",
+    "reason" : "Threshold must include all facets from threshold scope but is missing: appName",
+    "type" : "ThresholdMissingFacets"
   } ]
 }
 
```
[... truncated]

### release-1162 (2026-05-15 19:50:59) — FAILURE
Tag: release-1162
Previous tag: release-1161
Commits: 1
Files: 19, Lines: +2939 -138
  - [NR-552270] Null value threshold scopes (#1303)
Files:
  - README.md (+5 -0)
  - build.gradle (+1 -1)
  - dependency_license_manifest.yml (+1 -1)
  - gradle.properties (+1 -1)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/missing_facets_with_nulls.http (+158 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/missing_facets_with_nulls.log (+423 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/multi_field_scope_with_nulls.http (+106 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/multi_field_scope_with_nulls.log (+367 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/null_facet_values.http (+87 -0)
  - src/http_tests/v2_nrql_conditions/threshold_suggestions/threshold_scope/null_facet_values.log (+273 -0)
```diff
// README.md
@@ -73,6 +73,11 @@ Perform the following to run the http tests locally.
 make mock-db
 ```
 
+**Only run `make mock-db` before HTTP tests — do NOT run `make mock-apis` or `make setup-mocks`.** Running the API mocks causes strange behavior with stubs (they won't clear correctly or behave properly).
+- `make setup-mocks` — starts both the database AND API mocks (incorrect for HTTP tests)
+- `make mock-db` — starts only the database (correct for HTTP tests)
+- `make mock-apis` — starts only the API mocks (do not use for HTTP tests)
+
 2. Setup a test run config template.
    
 - `Run -> Edit Configurations -> Edit Configuration Templates -> Junit`
```
```diff
// build.gradle
@@ -578,4 +578,4 @@ String maskSecret(String value) {
     if (value == null) return "null"
     if (value.length() <= 4) return "****"
     return value.substring(0, 2) + "****" + value.substring(value.length() - 2)
-}
\ No newline at end of file
+}
```
```diff
// dependency_license_manifest.yml
@@ -934,7 +934,7 @@ dependencies:
     internal: true
     project_url: https://source.datanerd.us
 
-  com.newrelic.ace:ace-condition:4.17.5:
+  com.newrelic.ace:ace-condition:4.18.0:
     internal: true
     project_url: https://source.datanerd.us
 
```
```diff
// gradle.properties
@@ -3,7 +3,7 @@
 #
 account-service-thrift.version=3.0.3
 account-user-service-thrift.version=3.0.4
-ace-condition.version=4.17.5
+ace-condition.version=4.18.0
 ace-core.version=11.4.0
 condition-standards-lib.version=1.0.2
 alert-integration-util.version=8.7.2
```
[... truncated]
</historical_code_changes_and_diffs>


Please process the provided information and generate a comprehensive assessment structured strictly around the following sections:

### 1. Current Deployment Analysis
Analyze `release-1174` across: Files Changed, Code Diff Size, Semantic/Contextual Analysis, Time of Deployment, Blast Radius.

### 2. Historical Failure Analysis
Analyze (release-1164, release-1164, release-1163, release-1163, release-1162) collectively. Identify systemic patterns, correlations, recurring alerts.

### 3. Dimension Comparison & Risk Matrix
| Dimension | Current Deployment Details | Historical Pattern Correlation | Risk Rating | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Files Changed** | | | | |
| **Diff Size** | | | | |
| **Semantic Risk** | | | | |
| **Deployment Time** | | | | |
| **Blast Radius** | | | | |

### 4. Red Flags & Final Recommendations
- **Risk-Prone Lines & Code Points**
- **Evidence-Based Flags (Pure History)**
- **Go/No-Go Recommendation** (Proceed / Postpone / Canary-with-Targeted-Tracing / Rollback-Strategy-Verification)

