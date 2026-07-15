# GCP Professional Data Engineer Study Set

This set contains real crawled ExamTopics Professional Data Engineer questions from 2024 to now. No generated questions are included.

| Group | Questions |
|---|---:|
| Professional Data Engineer dump (2024+) | 165 |

## Questions

| Ref | Keyword | Why keyword | Answer |
|---|---|---|---|
| 2024 / T1 Q15 | strong consistency | Streaming inserts are eventually consistent, so aggregations run immediately can miss in-flight rows. The trigger is needing stronger consistency after streaming inserts — wait about twice the typical availability latency before querying. | D |
| 2024 / T1 Q19 | minimize the storage cost | A like-for-like Dataproc move with huge Persistent Disk is expensive. When the goal is minimize storage cost, keep data in Cloud Storage and let Dataproc use it, instead of 50 TB PD per node. | A |
| 2024 / T1 Q44 | multiple values + ordered by | Datastore equality filters on multi-valued properties plus an inequality/order on another property need a composite index. Manually define that index for actor/tag + date_released style queries. | A |
| 2024 / T1 Q62 | late or out of order | Batch and stream events can arrive late. Dataflow handles that with event-time watermarks and timestamps, not just a single global window or naive sliding windows. | C |
| 2024 / T1 Q64 | do not want individual users to authenticate | The app must query BigQuery without end-user Google identities on the dataset. Use a service account with dataset access and its key from the app. | C |
| 2024 / T1 Q73 | transactions that scale horizontally + range queries | Need horizontal transactional scale plus range queries on non-key columns. That is Spanner with secondary indexes, not Cloud SQL. | C |
| 2024 / T1 Q74 | financial time-series + Apache Hadoop | Frequent updates/streaming time-series plus migrating Hadoop-style workloads points to Bigtable as the storage engine. | A |
| 2024 / T1 Q75 | expose aggregates + analysis cost for other projects | Share only aggregates, keep user-level data private, and push query cost to consumers. An authorized view over aggregates does that without duplicating storage. | A |
| 2024 / T1 Q77 | increase the training speed | Training is slow because of training-set size/complexity. Subsample the training data to speed training; test-set size does not drive training time. | B |
| 2024 / T1 Q79 | maximize transfer speeds | Hybrid ingest is bottlenecked getting data into GCP. Raising datacenter→GCP network bandwidth is the lever, not disk or VPC→GCS bandwidth alone. | C |
| 2024 / T1 Q82 | tracking_table + fine-grained analysis of each day's events | One big tracking_table with streaming ingest and cheap per-day analysis means a partitioned BigQuery table using a TIMESTAMP partition column, not YYYYMMDD shards. | B |
| 2024 / T1 Q85 | avoid introducing new projects | On-demand 2K slots/project is starving queries and you cannot add projects. Switch to flat-rate/reservations and set hierarchical priorities. | C |
| 2024 / T1 Q105 | multiple dependencies + every day | Daily multi-step Dataproc/Dataflow pipeline with dependencies needs a managed orchestrator → Cloud Composer (Airflow). | B |
| 2024 / T1 Q142 | monitor slot usage | Teams need slot usage visibility in their projects. Monitor BigQuery slots/allocated_for_project (slots/allocated) style metrics, not scanned_bytes. | B |
| 2024 / T1 Q152 | 40 TB + GeoJSON | Huge multi-source analytics with GeoJSON telemetry and dashboards fits BigQuery, not OLTP stores like Cloud SQL/Datastore. | A |
| 2024 / T1 Q166 | package-tracking + query performance | Ingest-date partitioning is not how analysts filter packages. Cluster on package-tracking ID to speed lifecycle/geospatial package queries. | B |
| 2024 / T1 Q167 | peak usage + fluctuate | On-prem Spark/Hive/HDFS sized for peaks but batchy/variable. Lift to Dataproc with Cloud Storage first, modernize later — cheapest lift with elastic storage. | B |
| 2024 / T1 Q174 | 70% of customer requests + 10 intents | Automate the small intent set covering most volume first so agents focus on the long-tail complicated 30%. | A |
| 2024 / T1 Q179 | referential integrity + PII | Mask PII but keep joinability on names/emails. Use DLP cryptographic format-preserving tokens/pseudonyms, not irreversible redaction. | D |
| 2024 / T1 Q180 | author information is kept in a separate table | BigQuery schema guidance for 1:many attributes is nesting (author RECORD/ARRAY), not forced relational joins. | C |
| 2024 / T1 Q196 | POSIX-compliant + weekly | Recurring secure transfer from on-prem POSIX with limited public bandwidth → Storage Transfer Service for on-premises on a weekly schedule. | C |
| 2024 / T1 Q204 | invalid values + near-real time | Multi-vendor streaming into BigQuery ML/Vertex needs cleansing. Pub/Sub + Dataflow sanitize, then stream to BigQuery. | D |
| 2024 / T1 Q206 | longtail and outlier + near-real time | Cleanse outliers in near real time before AI. Programmatic Dataflow cleansing into BigQuery is the fit. | B |
| 2024 / T1 Q207 | location_id and device_version | Queries filter recent data by location_id and device_version. Partition by date, cluster by those filter columns. | B |
| 2024 / T1 Q208 | partial results + count the votes exactly once | Live votes need real-time partials plus exact-once final count cheaply. Pub/Sub → Dataflow into Bigtable (live) and BigQuery (final analytics). | D |
| 2024 / T1 Q210 | each team can access only the assets | Data mesh with isolated products: one Dataplex lake per product with landing/raw/curated zones and team-scoped access. | D |
| 2024 / T1 Q211 | less than 24 hours + keeping costs to a minimum | Protect a frequently updated multi-region sales table with <24h RPO cheaply: daily export to a dual/multi-region Cloud Storage bucket. | A |
| 2024 / T1 Q212 | network tags + communicate with one another | Dataflow workers must talk on TCP 12345/12346. With tag-based firewalls, allow those ports for the Dataflow network tag. | B |
| 2024 / T1 Q214 | simulate a Redis instance failover + no impact on production data | Practice failover without touching prod data: use a non-prod Standard Tier instance and force-data-loss manual failover. | B |
| 2024 / T1 Q215 | partner organization + CMEK | Partner lacks your CMEK. Copy needed tables to a non-CMEK dataset and share via Analytics Hub listing. | C |
| 2024 / T1 Q216 | does not have a public IP address + connection failure | Dataflow in Project A must reach private Cloud SQL in Project B. Peer VPCs and use a private proxy VM in B on the peered subnet. | D |
| 2024 / T1 Q217 | must not be able to access the sensitive data | Column security via policy tags: analytics team must not have Fine-Grained Reader on sensitive tags while still reading non-sensitive columns. | B |
| 2024 / T1 Q218 | same database capacity + promoting a read replica | After promoting Region2 replica, recreate capacity: two new replicas from the new primary (Region3 + another region). | C |
| 2024 / T1 Q219 | task does not succeed | Composer/Airflow task failure notifications use on_failure_callback on the operator, not retry/SLA callbacks. | C |
| 2024 / T1 Q220 | does not go through the public internet | On-prem MySQL with no public IP into BigQuery privately: Datastream over Cloud Interconnect with private connectivity. | B |
| 2024 / T1 Q221 | as little movement of data as possible | Query US BigQuery plus US Azure/AWS object data in place → BigQuery Omni / BigLake, not bulk copying everything in. | D |
| 2024 / T1 Q222 | low code + cleanse and explore | Data science needs low-code prep/validation on Cloud Storage files → Dataprep. | D |
| 2024 / T1 Q223 | uniqueness and null value checks + Dataform | ELT quality checks inside Dataform pipelines belong as Dataform assertions in code. | C |
| 2024 / T1 Q225 | minimizing ETL data processing changes | Move Spark+Parquet with managed services and minimal pipeline rewrites: Cloud Storage + Dataproc Metastore, run Spark on Dataproc; BigQuery later. | A |
| 2024 / T1 Q226 | any future project cannot access | Lock a confidential Pub/Sub topic to project A only, including future projects → VPC Service Controls perimeter around project A. | B |
| 2024 / T1 Q227 | few hundred + read-only clients + Basic Tier | Many read-only clients need Standard Tier Redis with read replicas. | B |
| 2024 / T1 Q228 | reprocesses the previous two days of delivered Pub/Sub messages | Need already-acked history for replay → retain-acked-messages (plus snapshot/new sub as second control). | D |
| 2024 / T1 Q229 | outer joins and analytic functions + no less than 4 hours old | Non-incremental materialized views with max_staleness 4h speed viz SQL. | A |
| 2024 / T1 Q230 | minimal changes + Hadoop + Airflow | Lift Hadoop to Dataproc + GCS for HDFS; keep orchestration on Cloud Composer. | B |
| 2024 / T1 Q231 | worker pod evictions + workers memory usage | Composer OOM/evictions: raise max workers and lower concurrency (and/or worker memory). | C |
| 2024 / T1 Q232 | only the europe-west3 region | Org-wide location lock → resourceLocations constraint to europe-west3. | A |
| 2024 / T1 Q233 | job queuing or slot contention | Admin resource charts + INFORMATION_SCHEMA to diagnose slot/queue slowdowns. | C |
| 2024 / T1 Q234 | 10 PB of historical + 1000 queries per second | Huge history in BigQuery; hot last-state API in Cloud SQL. | D |
| 2024 / T1 Q235 | no fixed schedule + different for every table | Event-driven sequential Dataproc/BQ transforms per table → Composer DAGs + GCS trigger. | D |
| 2024 / T1 Q236 | regional outage + several readers from various geographic regions | HA Cloud SQL + cross-region HA replica, cascade readers, promote on failover. | C |
| 2024 / T1 Q237 | stream or batch-load + mask some sensitive data + programmatic | One Beam pipeline covering stream/batch + DLP into BQ is cost-efficient. | C |
| 2024 / T1 Q238 | per-user crypto-deletion | Native per-user crypto-shredding in BQ → AEAD functions. | A |
| 2024 / T1 Q239 | quota errors + 1500 queries + non time-sensitive | Slot contention: run pipelines as batch jobs; keep ad-hoc interactive. | B |
| 2024 / T1 Q240 | Data engineers + Analytic users | Lake: dataOwner for engineers; curated zone: dataReader for analysts. | A |
| 2024 / T1 Q241 | regional failure + minimize the recovery point objective (RPO) | Pipeline buckets surviving regional failure with low RPO → dual-region + turbo replication. | C |
| 2024 / T1 Q242 | RPO of 15 minutes + regional outage | Dual-region turbo GCS + seek subscription back + restart Dataflow in secondary region. | D |
| 2024 / T1 Q243 | replace the nulls with zeros | For BQML features, replace null feature1 with 0 in the SELECT (IFNULL/COALESCE) feeding the model. | C |
| 2024 / T1 Q244 | full control of their collected data + exchange their data | Teams keep ownership and share read access → publish/subscribe via Analytics Hub. | C |
| 2024 / T1 Q245 | completed processing your data + model development lifecycle | After prep, next ML step is split train vs test data. | C |
| 2024 / T1 Q246 | street addresses | Find STREET_ADDRESS occurrences across a dataset → DLP deep inspection with that infoType. | B |
| 2024 / T1 Q247 | central data platform team is becoming a bottleneck + data mesh | Per-domain Dataplex lakes/zones owned by domain teams removes central bottleneck. | C |
| 2024 / T1 Q248 | fewer than 8 vCPU | Cheap recurring filter of nested VM inventory → view with filter + UNNEST. | A |
| 2024 / T1 Q249 | There should not be any charges for data retrieval | No retrieval fees, instant access, deletable old data → Autoclass. | A |
| 2024 / T1 Q250 | email field + personally identifiable information (PII) should not be accessible | Join on email without exposing PII → DLP FFX format-preserving encryption then load BQ. | B |
| 2024 / T1 Q251 | not deleted or modified | Legal hold immutability → retention policy and lock it. | A |
| 2024 / T1 Q252 | historical record of all data + easy-to-use | Monthly-updating dims with history for viz → denormalized append-only nested model + ingest time. | D |
| 2024 / T1 Q253 | only internal IP addresses and no external IP addresses | Org bans external IPs: Private Google Access + internal-IP Dataflow workers. | D |
| 2024 / T1 Q254 | autoscaler is not spinning up additional workers | Fusion hides parallelism so autoscaler stalls → Reshuffle to break fusion. | B |
| 2024 / T1 Q255 | Oracle + continuously synchronize + minimize the need to manage infrastructure | Managed Oracle→BQ continuous sync on private VPC → Datastream. | D |
| 2024 / T1 Q256 | no Internet access + reactive way every time a new file | Private Composer react to GCS object: GCS notify → CF via PSC to Airflow API. | C |
| 2024 / T1 Q258 | your own encryption keys + GUI-based solution | GUI ingest of Parquet/CSV into GCS with customer keys → Cloud Data Fusion. | B |
| 2024 / T1 Q259 | graphical user interfaces + spreadsheet | GUI prep then analyze in sheets → Dataprep to BQ + Connected Sheets. | A |
| 2024 / T1 Q260 | strict completion time SLAs + ad-hoc analytical queries | SLA project: Enterprise baseline 300 + autoscale 500; ad-hoc stays on-demand. | B |
| 2024 / T1 Q261 | local storage space on your existing data warehouse is limited | Teradata→BQ with little code and limited local disk → BQ Data Transfer JDBC FastExport. | A |
| 2024 / T1 Q262 | on-premises hardware security module (HSM) | Keys only on customer HSM for BQ → Cloud EKM linked from on-prem HSM. | B |
| 2024 / T1 Q263 | merged into one step + potential bottleneck | Fused Dataflow graph hides stage cost → Reshuffle between steps to inspect. | A |
| 2024 / T1 Q264 | predictable cost model + scan intensive | On-demand CDC merge scanning huge target → BigQuery reservation. | D |
| 2024 / T1 Q265 | past seven days + lowest RPO | Recover from recent table corruption cheaply → BigQuery time travel. | A |
| 2024 / T1 Q266 | more than 30 minutes + no data has been received for 15 minutes | Activity then 15-minute silence ends the window → session windows with 15-minute gap. | A |
| 2024 / T1 Q267 | tightly coupled immutable relationship + frequently joined | Header/line sales tables rarely change and always join → nest lines under header. | A |
| 2024 / T1 Q268 | without losing any data + more than 10 minutes | Replace streaming Dataflow safely: drain old pipeline, then start new. | C |
| 2024 / T1 Q269 | BigQuery, Pub/Sub, and a PostgreSQL + discoverability | Auto-catalog BQ/Pub/Sub in Data Catalog; manually catalog Postgres via API. | B |
| 2024 / T1 Q270 | every two hours + three consecutive failures | Scheduled BQ SQL every 2h with email after 3 failures: scheduled query → Pub/Sub → Cloud Functions. | D |
| 2024 / T1 Q271 | daily stored data increased by 50% + volumes of data in Pub/Sub remained the same | Same Pub/Sub volume but bigger BQ partitions → investigate duplicates and which Dataflow version wrote them. | C |
| 2024 / T1 Q272 | has_sensitive_data + Human Resources (HR) group | Public tag-template search for everyone; only HR gets dataViewer on sensitive tables. | C |
| 2024 / T1 Q273 | certain tag is pushed + development and another instance for production | Tag-based DAG deploy: Cloud Build to dev bucket then prod bucket after tests. | A |
| 2024 / T1 Q274 | Google-managed encryption key + Cloud KMS | Org requires CMEK: create CMEK table and migrate from Google-managed table. | B |
| 2024 / T1 Q275 | ORC + Hive partitioning + SQL on the Hive query engine | Explore ORC Hive-partitioned HDFS-like data: copy to GCS + BigQuery external tables. | D |
| 2024 / T1 Q276 | multiple zonal failures at job submission time | Batch Dataflow resilience at submit: set --region (regional workers). | C |
| 2024 / T1 Q277 | real-time dashboards + supply and demand | Ride-hail real-time aggregates for dashboards → hopping windows in Dataflow to Memorystore. | B |
| 2024 / T1 Q278 | business logic fails on a message + alerting | Failed DoFn elements → side output to a monitor Pub/Sub topic. | B |
| 2024 / T1 Q279 | readable but unmodifiable + individual workspaces | Shared dataset: Data Viewer; per-analyst datasets with Data Editor. | C |
| 2024 / T1 Q280 | late data + hopping windows | Late data not classified correctly → watermarks + allowed lateness. | A |
| 2024 / T1 Q281 | garbage collection policy + older than 30 days | GC is lazy; filter by timestamp range in queries so analysts never see >30-day data. | B |
| 2024 / T1 Q282 | exactly-once delivery semantics + 1.5 GB per second | Exactly-once into BQ at high rate → BigQuery Storage Write API (multiregional table). | B |
| 2024 / T1 Q283 | Hive partitioned + queries against this table are slow | Slow external Hive table: upgrade to BigLake + metadata caching. | C |
| 2024 / T1 Q284 | single-digit millisecond latency + complex analytic queries | Point lookups in ms → Bigtable row key; daily export to BigQuery for analytics. | B |
| 2024 / T1 Q285 | immutable for 3 years + one or two times a year | Rare SQL access + 3y immutability: export to Archive GCS, lock retention, external table. | D |
| 2024 / T1 Q286 | keep code changes to a minimum + managed services | Many Spark jobs off long-lived Hadoop: data to GCS, run on Dataproc. | D |
| 2024 / T1 Q287 | consistent BigQuery analytics spend each month | Predictable monthly spend → fixed baseline reservation (no autoscaling) and chargeback. | C |
| 2024 / T1 Q288 | Data lineage tracking + Data quality validation | Discovery + lineage + quality in one managed service → Dataplex. | D |
| 2024 / T1 Q289 | no coding + recurring job + normalize | No-code recurring normalize of BQ report fields → Data Fusion Wrangler. | A |
| 2024 / T1 Q290 | maximum of 10 retries + store the failed messages | Push reliability: exponential backoff + dead letter topic after 10 attempts. | D |
| 2024 / T1 Q291 | self-serving, low-maintenance + share the sales dataset | Org sharing of a BQ dataset with low ops → Analytics Hub private exchange. | A |
| 2024 / T1 Q292 | 100 times a day + Cloud SQL for MySQL + Cloud SQL for PostgreSQL | Frequent BQ campaigns joining GA + two Cloud SQL sources → Datastream replicate into BQ. | C |
| 2024 / T1 Q293 | data mesh + sales, product design, and marketing | Per-department lakes/zones in Dataplex over their own projects enables mesh sharing. | D |
| 2024 / T1 Q294 | new subscriber + last 30 days | Late joiners need historical messages → topic retention 30 days. | B |
| 2024 / T1 Q295 | Shared VPC network + Dataflow | Deploy Dataflow on Shared VPC: grant compute.networkUser to the pipeline SA. | B |
| 2024 / T1 Q297 | column level + data mesh | HDFS→GCS with Spark/SQL and column security → BigLake + policy tags. | B |
| 2024 / T1 Q298 | re- encrypt + CMEK-protected + compromised key | New KMS key, new default-CMEK bucket, copy objects, then retire old key. | D |
| 2024 / T1 Q299 | RPO=15 mins + minimal latency when reading | Dual-region GCS + turbo replication; read local region, failover Dataproc. | D |
| 2024 / T1 Q300 | without changing database management systems + transactional workloads and support analytics | Stay on PostgreSQL with HTAP: AlloyDB for PostgreSQL. | B |
| 2024 / T1 Q301 | ELT + SQL as code | SQL-first ELT with code management → Dataform. | A |
| 2024 / T1 Q302 | 500 MB + every 30 seconds + once a week | Small sensor dim table + high-frequency metrics: partition metrics by time, FK to sensors, append inserts. | C |
| 2024 / T1 Q303 | curated zone but the files are not being automatically discovered | JSON/CSV auto-discovery belongs in raw; move files from curated to raw zone. | A |
| 2024 / T1 Q304 | past year of data + always include the latest data | Materialized view over last-year partitions keeps fresh aggregates without scanning full history. | A |
| 2024 / T1 Q305 | Amazon Web Services’ (AWS) S3 | Query US GCS+S3 in place without bucket ACLs to users → BigQuery Omni/BigLake. | A |
| 2024 / T1 Q306 | data privacy requirements | Restricted GCS customer data → Dataflow + DLP mask, then BigQuery. | A |
| 2024 / T1 Q307 | dynamic public IP addresses + Cloud SQL public IP | Changing client IPs can’t use static authorized networks → Cloud SQL Auth proxy. | C |
| 2024 / T1 Q308 | signed URLs + HTTP 403 | Expired signed URLs mid-transfer: regenerate longer-lived URLs and split parallel STS jobs. | C |
| 2024 / T1 Q309 | only uses the last 30 days + minimize costs | Partition by weather date and expire partitions after 30 days. | B |
| 2024 / T1 Q310 | several petabytes + simple aggregations + up-to-date | Repeated filtered aggregations on huge table → materialized view. | D |
| 2024 / T1 Q311 | do not process orders twice + pull subscription | Pull subscription without double-processing → Pub/Sub exactly-once delivery. | C |
| 2024 / T1 Q313 | minimally change + 8 vCPU and 16 GB + minimize installation | Spark 3 batch with similar executor sizing and low ops → Dataproc Serverless. | D |
| 2024 / T1 Q314 | cost-effective and secure communication + Google APIs | Dataflow workers: no external IPs + Private Google Access to reach Google APIs. | A |
| 2024 / T1 Q316 | day and month levels + minimize maintenance | Repeated day/month aggregations on a huge fact table → materialized views. | C |
| 2024 / T1 Q317 | your own encryption keys + GUI-based solution | GUI move of mixed on-prem/cloud files into GCS with customer keys → Cloud Data Fusion. | D |
| 2024 / T1 Q319 | protecting certain sensitive data elements + retaining all of the data | Mask with Dataflow+DLP into BQ while keeping usable data for analysis. | C |
| 2025 / T1 Q209 | ingest-date partitioning + geospatial trends + package | Queries by package lifecycle not ingest day → cluster on package-tracking ID. | B |
| 2025 / T1 Q213 | country_name and username + 10 PB | Filter-heavy huge order table → cluster by country and username. | A |
| 2025 / T1 Q257 | ingested once + access patterns of individual objects will be random | One-write random-read cost optimization without app changes → Autoclass. | A |
| 2025 / T1 Q296 | Apache Kafka + interconnect + minimal latency | On-prem Kafka over interconnect into BQ with low latency → Dataflow. | C |
| 2025 / T1 Q312 | securely publish, discover, and subscribe + data freshness | Org-wide self-serve read-only sharing with freshness → Analytics Hub. | A |
| 2025 / T1 Q315 | Python's standard library + Workflows | When Workflows can’t run complex Python logic, call a Cloud Function then continue. | C |
| 2025 / T1 Q318 | recovery point objective (RPO) of less than 24 hours | Cheap regional-table protection: daily export to dual/multi-region GCS. | A |
| 2026 / T1 Q320 | Looker Studio + slow dashboard load times | Precompute with materialized views and/or accelerate with BI Engine for Looker Studio. | BD |
| 2026 / T1 Q321 | without physically moving or duplicating the data | Federated governance over GCS+BQ without copies is Dataplex lakes/zones + quality/policies. | B |
| 2026 / T1 Q322 | proprietary, vendor-specific format + batch migration | Unknown proprietary warehouse format: export CSV → GCS → load BigQuery. | B |
| 2026 / T1 Q323 | development, staging, and production + Google-recommended practices | Manage env IAM via Google Groups with roles per project, not per-user bindings. | D |
| 2026 / T1 Q324 | strict dependencies + notify you if not completed by 7:00 AM | Multi-step SFTP→decrypt→GCS→BQ with SLA/alerts and reruns is Cloud Composer (Airflow). | B |
| 2026 / T1 Q325 | Analyst dashboards + ETL jobs | Separate capacity: reserved/autoscaling slots for interactive dashboards vs separate/on-demand for ETL. | A |
| 2026 / T1 Q326 | Resources exceeded | On-demand resource failures on huge queries → move to slot reservations. | A |
| 2026 / T1 Q327 | Retrieval-Augmented Generation + embedding | RAG prep means embedding unstructured text into semantic vectors, not keyword indexes alone. | C |
| 2026 / T1 Q328 | compressed JSON + low-cost, programmatic | TB-scale daily JSON in GCS: external table then INSERT…SELECT is cheap and scalable. | A |
| 2026 / T1 Q329 | older than two years + seven years | Lifecycle: Archive after 2 years, delete at 7 years for rarely accessed historical objects. | B |
| 2026 / T1 Q330 | HiveQL queries directly against the data in Cloud Storage | Interactive HiveQL on Parquet in GCS with low ops → Dataproc with Hive enabled. | D |
| 2026 / T1 Q331 | millions of events each second + late-arriving data | High-rate clickstream with sessionization and late data is Pub/Sub + Dataflow + BigQuery. | C |
| 2026 / T1 Q332 | event date ranges + user ID UUID | Partition by event date and cluster by user ID optimizes time-range + user filters. | D |
| 2026 / T1 Q333 | validate email + generative AI sentiment + manual review | Dataflow ParDo validation + RunInference sentiment + side outputs for invalids matches the branching pipeline. | D |
| 2026 / T1 Q334 | lightweight, serverless orchestration + sequential | Sequential Dataflow→BQ→Vertex with minimal ops is Cloud Workflows, not heavy Composer. | D |
| 2026 / T1 Q335 | fully managed, no-code + 200 CSV files | Analyst no-code daily CSV→BQ load/transform fits BigQuery pipelines. | D |
| 2026 / T1 Q336 | resilient to zonal failures + us-central1 | Regional Dataflow (--region=us-central1) survives zonal outages better than a single zone. | A |
| 2026 / T1 Q337 | external partner companies + discoverable | Secure cross-org discoverable sharing of curated BQ datasets is Analytics Hub listings. | A |
| 2026 / T1 Q338 | unreadable whenever an employee leaves | Crypto-shredding: AEAD encrypt with per-employee keys and delete keys when they leave. | D |
| 2026 / T1 Q339 | execution plan + JOIN | To inspect JOIN bottlenecks fast, use Query History and the execution graph. | D |
| 2026 / T1 Q340 | recovery point objective (RPO) of 24 hours + recovery time objective (RTO) of 4 hours | Cross-region BigQuery dataset replication to us-east1 meets regional DR with low ops vs custom export. | C |
| 2026 / T1 Q341 | managed integration + incremental loads | Daily MySQL→BigQuery managed incremental ingest is BigQuery Data Transfer Service. | B |
| 2026 / T1 Q342 | consistently applied during both model training and prediction | BQML TRANSFORM in CREATE MODEL keeps feature SQL consistent for train and predict without manual dual pipelines. | C |
| 2026 / T1 Q343 | categorize these images + least amount of coding | Least-code image content analysis into structured BigQuery results points to Vertex AI Vision API. | C |
| 2026 / T1 Q344 | ACID compliance + high throughput + low-latency | Concurrent transactional ops with ACID on a managed service maps to Spanner. | D |
| 2026 / T1 Q345 | prevent training-serving skew | Preprocessing must match train and serve. Replicate the same pre-processing logic in the Vertex AI inference path. | B |
| 2026 / T1 Q346 | same aggregation + minimizes analytics spend | Repeated store-ID/sales aggregations should not recompute every query. A materialized view caches that aggregation cheaper and faster. | B |
| 2026 / T1 Q347 | clinical researchers + accounting team | Different teams need different columns from the same sensitive table. Separate datasets with authorized views expose only approved fields per team. | D |
| 2026 / T1 Q348 | consistently cataloged + data quality checks and transformations | Different formats need catalog discovery plus quality/transform before use. Dataplex Universal Catalog over GCS/BQ is the managed governance path. | C |
| 2026 / T1 Q349 | 30 minutes of inactivity | A visit ends after inactivity, which is a per-user gap — not a fixed clock window. Session windows with a 30-minute gap match that definition; tumbling/hopping windows do not. | D |
