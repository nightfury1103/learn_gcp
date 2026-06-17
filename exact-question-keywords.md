# GCP PCA Exact Question Keywords - 2024 to Now

Rule: every keyword below is an exact phrase that appears in that question text.

| # | Exam ref | Exact keyword in question | Choose this answer pattern |
|---:|---|---|---|
| 1 | 2024 / T1 Q197 | approval documents | A: Create a retention policy on the bucket for the duration of 5 years. Create a lock on the retention policy. |
| 2 | 2024 / T1 Q198 | same SSL | D: Use separate backend pools for each API path behind the load balancer |
| 3 | 2024 / T1 Q199 | memory usage | C: Change the filter to metric.label.state = ‘used’. |
| 4 | 2025 / T1 Q200 | data exfiltration | B: Configure VPC Service Controls and configure Private Google Access for on-promises hosts. |
| 5 | 2025 / T1 Q201 | patch the operating systems | D: Set up VM Manager, and install the OS Config agent on each VM. Schedule a patch job to apply patches on each VM. |
| 6 | 2025 / T1 Q202 | connect, map | B: Leverage Application Integration to connect the services and transform the data. |
| 7 | 2025 / T1 Q203 | dynamic API content | A: Use an external Application Load Balancer to serve your application APIs. \| B: Use Cloud CDN to serve static assets of your application. |
| 8 | 2025 / T1 Q204 | manage costs | B: Configure labels and tags for the resources provisioned in Google Cloud. \| E: Adopt infrastructure as code (IaC) for the cloud resources. |
| 9 | 2025 / T1 Q205 | AlloyDB database | B: Enable Direct VPC egress for the Cloud Run service, and send traffic directly to a VPC. |
| 10 | 2025 / T1 Q206 | container images | A: Use Cloud Build to build container images, and then trigger Artifact Analysis on images pushed to Artifact Registry. |
| 11 | 2025 / T1 Q207 | private endpoint | C: Create a Cloud Build private pool that is peered with the same VPC network as your GKE cluster. Update the Cloud Deploy pipeline to use this private pool as its execution environment. |
| 12 | 2025 / T1 Q208 | SAP workloads | D: Gather data about your current environment, and leverage Google Cloud Migration Center to generate a cost estimate. |
| 13 | 2025 / T1 Q209 | using SQL | C: Enable log analytics and run queries in the linked log dataset in BigQuery. Visualize the data with Looker Studio dashboards. |
| 14 | 2025 / T1 Q210 | 30 days | D: Configure a Cloud Storage bucket with an Object Lifecycle Management policy to transition data from the Standard class to the Coldline class after 30 days. |
| 15 | 2025 / T1 Q211 | based in Qatar | B: Use Vertex AI Model Garden to select a Gemma model. Deploy this model to a Vertex AI Endpoint within a Google Cloud region located in Qatar. |
| 16 | 2025 / T1 Q212 | monolith | B: Implement a managed API facade with Apigee to handle all requests from dependent applications on behalf of the monolith’s backend. |
| 17 | 2025 / T1 Q213 | private CI/CD runners | A: Create a separate VPC in each of the four projects. Connect each environment's VPC to the shared services VPC through VPC Network Peering. |
| 18 | 2025 / T1 Q214 | Cloud Armor | C: Set the Cloud Run ingress to Allow internal traffic and Cloud Load Balancing, and use a serverless NEG backend on the load balancer |
| 19 | 2025 / T1 Q215 | production environments | A: At each production folder, apply a hierarchical firewall policy to deny all ingress except for HTTPS to tagged VMs. |
| 20 | 2025 / T1 Q216 | audit trail | C: Enable GKE Audit Logging to send Kubernetes API server logs to Cloud Logging, and ensure Cloud Audit Logs are enabled for the project. |
| 21 | 2025 / T1 Q217 | Spanner | C: Develop a total cost of ownership (TCO) analysis that includes operational overhead, and present it in a workshop to facilitate a decision. |
| 22 | 2025 / T1 Q218 | roll back | C: Separate CI/CD pipelines for database schema migrations from application deployments. When deploying a new Cloud Run revision, use gradual traffic split. |
| 23 | 2026 / T1 Q219 | encryption keys | D: Use customer-managed encryption keys (CMEK) for all Cloud Storage buckets storing sensitive media content. Implement fine-grained access control using IAM roles and groups to restrict access to sensitive buckets. |
| 24 | 2026 / T1 Q220 | occasional interruptions | B: Deploy spot VM instances. |
| 25 | 2026 / T1 Q221 | in isolation | A: Run unit testing. |
| 26 | 2026 / T1 Q222 | Java-based | B: Analyze the data via Cloud Profiler. |
| 27 | 2026 / T1 Q223 | DDoS attacks | C: Deploy Google Cloud Armor with pre-configured and custom rules for L3/L4 and L7 protection |
| 28 | 2026 / T1 Q224 | API calls | C: Configure Quota policies. |
| 29 | 2026 / T1 Q225 | multiple locations | D: Create a fleet of GKE clusters in different regions. Deploy the app on every cluster. Configure a multi-cluster Gateway. |
| 30 | 2026 / T1 Q226 | vehicle sensor data | C: Use the vehicle ID, event ID, and timestamp (in that order) as the row key. Create a column family per sensor category, and use a column qualifier for each individual sensor within its respective category. |
| 31 | 2026 / T1 Q227 | too much CPU | A: Configure resource requests per Deployment. Set resource requests slightly above the typical CPU usage observed during monitoring. |
| 32 | 2026 / T1 Q228 | two regions | D: Configure the Resource Location Restriction constraint organization policy at the organization level, and ensure only the allowed regions are listed. |
| 33 | 2026 / T1 Q229 | XML format | A: Create a Pub/Sub topic per supplier, and have HQ publish all changes related to the respective supplier in JSON format on that topic. Allow all plants to create Pub/Sub Pull subscription to receive messages for their suppliers and update their databases. |
| 34 | 2026 / T1 Q230 | personally identifiable information | A: Store the training data in BigQuery using column-level encryption. Train the model using Confidential GKE Nodes. |
| 35 | 2026 / T1 Q231 | guaranteed bandwidth | C: Create a Premium Ter VPand ensure a subnet is available in the region closest to a plant. Establish a Cloud Interconnect between each subnet and the local plant. |
| 36 | 2026 / T1 Q232 | modernize their landscape | B: Create a Shared Virtual Private Cloud (VPC). Migrate the VMs to Compute Engine in a new project. During modernization, deploy each modernized workload in a dedicated Google Cloud project using the Shared VPC. |
| 37 | 2026 / T1 Q233 | sandbox environment | A: Create a request form where engineers can request a sandbox environment for a specific technology. Automate the creation of a project with only the relevant APIs enabled and lower the default API quota. Grant IAM roles related to this scope to the requesting team. Ensure the project is automatically deleted after a predefined amount of time. |
| 38 | 2026 / T1 Q234 | customer behavior | B: Configure Model Monitoring, and select prediction drift detection. |
| 39 | 2026 / T1 Q235 | security posture | D: Create a service perimeter and include aiplatform.googleapis.com and notebooks.googleapis.com as protected services. |
| 40 | 2026 / T1 Q236 | overall duration | C: Measure the Latency of your requests. |
| 41 | 2026 / T1 Q237 | business continuity | A: Deploy active managed instance groups (MIGs) in both us-west1 and us-east1, fronted by a global external HTTP(S) Load Balancer. For the database, use a cross-region read replica in us-east1, and rely on load balancer health checks to automatically fail over all traffic during an outage. |
| 42 | 2026 / T1 Q238 | one-time migration | D: Order a Transfer Appliance, copy the data to the appliance using your high-speed local network, and ship it back to Google to upload the data into your Cloud Storage bucket. |
| 43 | 2026 / T1 Q239 | 9:00 AM | A: Schedule the virtual machines to start and stop to match your team’s work schedule. |
| 44 | 2026 / T1 Q240 | zonal outage | B: Deploy the application on a regional MIG to provide high availability across multiple zones in the primary region. |
| 45 | 2026 / T1 Q241 | fraud detection | B: Use Dataflow to process the streaming data. \| D: Use BigQuery for the batch analytics reports. |
| 46 | 2026 / T1 Q242 | 90 days | D: Use the Backup and Disaster Recovery (DR) service to create a backup plan. Configure the backup plan to take daily snapshots and store them in a backup vault with a 90-day retention policy. |
| 47 | 2026 / T1 Q243 | page load speed | B: Use Memorystore tor Redis. \| C: Implement CDN with the application's external HTTPS load balancer. |
| 48 | 2026 / T1 Q244 | write-heavy | B: Deploy the application to Cloud Run in multiple regions behind a global HTTPS load balancer. Use Spanner as the database. |
| 49 | 2026 / T1 Q245 | self-hosted Jupyter | C: Use Vertex AI for machine learning and machine learning operations (MLOps) for model deployment. |
| 50 | 2026 / T1 Q246 | monolithic Python | C: Propose a phased, event-driven migration to a microservices architecture. Use Pub/Sub for asynchronous communication and deploy the fraud models on Vertex AI endpoints. |
| 51 | 2026 / T1 Q247 | three-tier application | C: Use a combination of network tags and service accounts. Apply a unique network tag and a dedicated service account to the instances in each tier. Then create specific firewall rules that allow ingress traffic based on the source service account or tag of the upstream tier. |
| 52 | 2026 / T1 Q248 | 2 petabytes | B: Request Transfer Appliances from Google Cloud. Transfer the data using the appliances. |
| 53 | 2026 / T1 Q249 | trade confirmation | D: Enable Object Versioning on the bucket. Additionally, configure the bucket with a Bucket Lock and a retention policy of seven years. |
| 54 | 2026 / T1 Q250 | external auditors | A: Apply an IAM policy binding that grants the roles/storage.objectViewer role to the Google Group. Configure this binding with a time-based IAM Condition that automatically grants access from October 1 to November 1. |
| 55 | 2026 / T1 Q251 | pull request is merged | D: Connect your repository using the Cloud Build GitHub app. Create a trigger in Cloud Build. Once a pull request is merged, trigger Cloud Build to build and deploy the application to Cloud Run. |
| 56 | 2026 / T1 Q252 | Hardware Security | C: Create a new key in Cloud Key Management Service (Cloud KMS) with the HSM protection level. |
| 57 | 2026 / T1 Q253 | less than 10 minutes | C: Configure the Cloud SQL instance with a cross-region read replica. In a disaster, promote the read replica to a standalone, primary instance. |
| 58 | 2026 / T1 Q254 | static service account keys | B: Use service account impersonation in Cloud Build. Configure the pipeline to run terraform plan on pull requests, and require manual approval before running terraform apply. |
| 59 | 2026 / T1 Q255 | all your tests | A: 1. After the developers push the code to a central repository, trigger Cloud Build to run unit tests. If all unit tests are successful, build the application container and push it to a central registry. 2. Trigger Cloud Build to deploy the container to a testing environment and run integration tests and acceptance tests. 3. If all tests are successful, deploy the application to the production environment and run the smoke tests. |
| 60 | 2026 / T1 Q256 | infrastructure as code | C: Set up Config Controller, and use YAML manifests to define the desired state of your Google Cloud resources. Apply these YAML configurations to provision and manage the resources. |
| 61 | 2026 / T1 Q257 | static assets | B: Enable Cloud CDN for the backend service that serves the static assets, and configure it as part of a global external HTTP(S) Load Balancer. \| D: Deploy the application frontend service to Compute Engine managed instance groups in regions in Europe and Asia. Use a global external HTTP(S) Load Balancer to route user traffic to the nearest region. |
| 62 | 2026 / T1 Q258 | local file system | C: Use the gcsfuse command line tool to mount the Cloud Storage bucket as a local file system, and perform read/write operations in your bucket using standard file system semantics. |
| 63 | 2026 / T1 Q259 | can tolerate interruptions | B: Deploy spot VMs with attached persistent disks and implement checkpoint mechanisms. |
| 64 | 2026 / T1 Q260 | business units | A: Create a folder for each department under the root Organization node. Apply the resource location Organization Policy on the Finance folder. Within the Marketing folder, create separate projects for mktg-prod and mktg-dev. Grant the compliance team the roles/viewer role at the Organization level. |
| 65 | 2026 / T1 Q261 | new to Kubernetes | D: Assess application and dependencies for containerization. Develop a migration strategy for deployment to GKE in Autopilot mode. |
| 66 | 2026 / T1 Q262 | low-priority notifications | C: Implement an error budget policy based on the availability of the SLO. Create a "page” alert that triggers only when the rate of burn of the error budget predicts a full exhaustion within the next 24 hours. |
| 67 | 2026 / T1 Q263 | Prometheus Query Language | C: Enable Google Cloud Managed Service for Prometheus to monitor and alert on your workloads at scale. |
| 68 | 2026 / T1 Q264 | multiple cloud providers | D: Utilize Config Sync as part of GKE to synchronize configurations from a centralized repository, and utilize Policy Controller to enforce policies using OPA Gatekeeper. |
| 69 | 2026 / T1 Q265 | container image vulnerabilities | B: Incorporate vulnerability scanning before building container images, and use Google-maintained base images for your container deployments. \| C: Enable Artifact Analysis for the container images, and stop deployment if critical vulnerabilities are found. |
| 70 | 2026 / T1 Q266 | ISO/IEC 27001 | C: Review the Compliance Reports Manager for information about ISO/IEC 27001 compliance and related documentation on obtaining reports through your Google Cloud account. |
| 71 | 2026 / T1 Q267 | triage incidents | A: 1. Navigate the predefined dashboards in the Cloud Monitoring workspace. 2. Add metrics and create alert policies. |
| 72 | 2026 / T1 Q268 | new insurance providers | D: Utilize Infrastructure as Code (IaC) tools, such as Terraform, to define and manage infrastructure configurations. |
| 73 | 2026 / T1 Q269 | compromised credentials | C: Configure Workload Identity Federation with Active Directory to enable authentication and authorization for applications across both Kubernetes environments. |
| 74 | 2026 / T1 Q270 | legacy relational database | A: Use the Database Migration Service (DMS) to migrate the MySQL databases to Cloud SQL. |
| 75 | 2026 / T1 Q271 | more than 2 TB | B: Utilize Storage Transfer Service (STS) to migrate objects to the destination bucket in the target region. Once the transfer is complete, delete the original source bucket objects. |
| 76 | 2026 / T1 Q272 | interconnected virtual machines | B: Use the Google Cloud Migration Center to perform an automated discovery and assessment of the on-premises environment. |
| 77 | 2026 / T1 Q273 | similar dashboard | A: Export your dashboard to a JSON file and share it with the Ops team. |
| 78 | 2026 / T1 Q274 | tightly coupled dependencies | D: Use dependency mapping to group application components into waves, create a phased migration plan, and incorporate performance testing for each wave. |
| 79 | 2026 / T1 Q275 | flash sales | C: Deploy the application as a Cloud Run service. Configure request-based auto-scaling and use gradual rollouts by splitting traffic between revisions. |
| 80 | 2026 / T1 Q276 | not correlated | A: Implement Cloud Trace by ensuring the traceparent header is propagated between microservice calls to link logs to a single trace. |
| 81 | 2026 / T1 Q277 | GPU capacity | C: Create an owner project with shared reservations, and then configure the production project and development project as consumer projects to consume capacity. |
| 82 | 2026 / T1 Q278 | zone becomes unavailable | C: Create a single regional managed instance group (MIG) configured to span all three zones. Place a regional external Application Load Balancer in front of the MIG, and configure its backend service with a health check. |
| 83 | 2026 / T1 Q279 | Google Groups | B: Enable uniform bucket-level access on the buckets, and grant predefined Storage IAM roles to the Google Groups. |
| 84 | 2026 / T1 Q280 | shared file system | B: Create a Filestore Enterprise instance in the same region as the VMs. Mount the Filestore file share on each Compute Engine VM. |
| 85 | 2026 / T1 Q281 | pre-approved architectural patterns | B: Use Service Catalog to define, govern, and offer a portfolio of approved products. Include Terraform scripts into Service Catalog items. |
