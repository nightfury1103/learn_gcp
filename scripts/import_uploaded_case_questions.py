#!/usr/bin/env python3
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = Path("/Users/huypham/Downloads/GCP cerf")
DATA_PATH = ROOT / "full-real-study-data.json"
REF_PATH = ROOT / "full-real-study-reference.md"
INDEX_PATH = ROOT / "index.html"
SW_PATH = ROOT / "sw.js"

FILES = [
    ("EHR Healthcare", UPLOAD_ROOT / "EHR_Healthcare.json"),
    ("Cymbal Retail", UPLOAD_ROOT / "Cymbal_Retail.json"),
    ("KnightMotives Automotive", UPLOAD_ROOT / "KnightMotives_Automotive(1).json"),
    ("Altostrat Media", UPLOAD_ROOT / "Altostrat_Media.json"),
]

CUES = {
    ("EHR Healthcare", 320): ("high throughput and strictly consistent latency", "This is not a best-effort VPN signal. Private, high-throughput, predictable latency between on-premises systems and Google Cloud points to Dedicated Interconnect."),
    ("EHR Healthcare", 321): ("centralized visibility into system performance", "The question asks to replace scattered open-source monitoring with one operational view and critical alerts across hybrid servers. Cloud Monitoring plus the Ops Agent fits that centralized monitoring requirement."),
    ("EHR Healthcare", 322): ("data must remain within EHR's control", "The decisive phrase is controlled medical note data. Vertex AI/Gemini with project-scoped prompt or tuning data supports generative summarization without training a public shared model on EHR data."),
    ("EHR Healthcare", 323): ("99.9% availability and reduce latency", "Availability plus global latency means use multiple regions and a global external load balancer so users reach a healthy nearby regional deployment."),
    ("EHR Healthcare", 324): ("single pane of glass", "Hybrid Kubernetes policy management needs one fleet-level control plane. GKE Enterprise with Config Management synchronizes cluster configuration and security policies across on-prem and Google Cloud."),
    ("EHR Healthcare", 325): ("mask the PII before the data is accessible", "Analysts need BigQuery access without raw identifiers. Sensitive Data Protection can inspect and de-identify PII during ingestion, reducing manual masking work."),
    ("EHR Healthcare", 326): ("thousands of internal PDF technical manuals", "The target is a quick internal chatbot over PDFs, not a custom search stack. Vertex AI Agent Builder indexes documents and provides RAG-style answers quickly."),
    ("EHR Healthcare", 327): ("without modifying the legacy applications", "File-based legacy integration with immediate cloud processing maps to Cloud Storage upload events and Cloud Functions or Pub/Sub notifications, avoiding application rewrites."),
    ("EHR Healthcare", 328): ("RTO must be under 30 minutes", "A regional database outage with a short RTO needs a ready replica elsewhere. A cross-region Cloud SQL read replica can be promoted much faster than restoring from backup."),
    ("EHR Healthcare", 329): ("only images that have passed security scans", "The requirement is deployment enforcement, not just image scanning. Binary Authorization gates GKE deploys based on signed or approved images."),
    ("EHR Healthcare", 330): ("private data is not used to train the base model", "The key is private medical-record tuning without changing the shared base model. Vertex AI Model Garden with adapter/supervised tuning keeps customer tuning data scoped to the project."),
    ("EHR Healthcare", 331): ("guarantees 99.99% availability", "Google's 99.99% Dedicated Interconnect pattern requires redundant circuits across two metros, and Global Dynamic Routing lets routes fail over across regions."),
    ("EHR Healthcare", 332): ("visualize the request flow", "Intermittent latency between microservices needs distributed tracing. Cloud Trace shows the request path and where the billing-to-patient call slows down."),
    ("EHR Healthcare", 333): ("accessed frequently during the first 30 days", "The storage access pattern cools after 30 days. Object Lifecycle Management can automatically move X-ray images to colder classes without separate buckets."),
    ("EHR Healthcare", 334): ("Prevent data from being copied", "The question has two controls: VPC Service Controls reduce BigQuery exfiltration, while policy tags/column-level security restrict the Social Security Number column."),
    ("EHR Healthcare", 335): ("natural language questions and get citations", "Unstructured PDFs plus cited natural-language answers is a buy-not-build search use case. Vertex AI Search is built for that document discovery pattern."),
    ("EHR Healthcare", 336): ("automatically reverted to the state defined in your Git repository", "Git-backed desired state across clusters is Config Sync, and Policy Controller enforces policy rules so manual drift is corrected or rejected."),
    ("EHR Healthcare", 337): ("Microsoft SQL Server database", "The migration target must preserve SQL Server compatibility and reduce admin work. Cloud SQL for SQL Server is the managed lift-and-shift database fit."),
    ("EHR Healthcare", 338): ("steady-state workload that runs 24/7", "The workloads have opposite pricing signals: steady 24/7 capacity benefits from CUDs, while interruptible nightly analytics fits Spot or preemptible VMs."),
    ("EHR Healthcare", 339): ("AI-powered coding assistant integrated into their IDE", "The need is developer productivity inside VS Code or IntelliJ for Java modernization. Gemini Code Assist is the Google Cloud IDE assistant."),

    ("Cymbal Retail", 251): ("personalized product recommendations", "Personalized ecommerce recommendations with minimal development effort maps directly to the managed Retail API Recommendations service."),
    ("Cymbal Retail", 252): ("unified view for analytics and ML", "Multiple on-prem data sources need continuous replication into an analytical warehouse. Datastream/Dataflow into BigQuery creates the unified cloud view."),
    ("Cymbal Retail", 253): ("text and images", "The catalog enrichment input is both supplier text and product images. Vertex AI Language extracts text attributes, while Vertex AI Vision identifies visual objects."),
    ("Cymbal Retail", 254): ("Human-in-the-Loop", "Human approval, editing, and auditability require an orchestrated workflow. Vertex AI Pipelines can coordinate AI generation, review, and publication steps."),
    ("Cymbal Retail", 255): ("generate different variations of product images", "Image variation, backgrounds, and promotional overlays are generative image-editing tasks. Images on Vertex AI is the matching service."),
    ("Cymbal Retail", 256): ("conversational commerce", "A shopping assistant needs both dialogue management and product discovery. Dialogflow CX handles conversations, and Vertex AI Search supports product retrieval."),
    ("Cymbal Retail", 257): ("event-driven, scalable, and decouples", "Replacing SFTP with decoupled processing points to Cloud Storage upload events plus Cloud Functions/Pub/Sub for downstream processing."),
    ("Cymbal Retail", 258): ("single control plane", "Managing on-prem Kubernetes and GKE together is the Anthos/GKE Enterprise pattern for centralized operations and policy enforcement."),
    ("Cymbal Retail", 259): ("stable, private connection endpoint", "The partner needs private access to one service without VPC access. Private Service Connect exposes a stable private endpoint for a privately hosted API."),
    ("Cymbal Retail", 260): ("unified view for dashboards, metrics, and alerting", "The operations problem is fragmented observability. Cloud Monitoring with agents brings on-prem and cloud metrics into one workspace."),
    ("Cymbal Retail", 261): ("protected from exfiltration", "Sensitive customer and virtual-agent data needs a perimeter, not just IAM. VPC Service Controls helps prevent data movement outside authorized services and networks."),
    ("Cymbal Retail", 262): ("prevented from viewing personally identifiable information", "The team can analyze aggregates but should not see PII columns. BigQuery column-level security restricts names and emails while preserving query access."),
    ("Cymbal Retail", 263): ("prevents the creation of public IP addresses", "This is a preventative organization-wide control. Organization Policy with the external IP constraint blocks new public VM IPs at scale."),
    ("Cymbal Retail", 264): ("scales rapidly from zero", "Unpredictable sales spikes and idle periods are Cloud Run's strength. It scales from zero and charges only when serving requests."),
    ("Cymbal Retail", 265): ("large batch files", "Large ongoing batch transfers need reliable high-bandwidth private connectivity. Dedicated Interconnect reduces reliance on internet paths and supports predictable throughput."),
    ("Cymbal Retail", 266): ("Kubernetes-style resource model", "They want to manage Google Cloud resources as Kubernetes custom resources. Config Connector provides that declarative Kubernetes-style IaC model."),
    ("Cymbal Retail", 267): ("manage, secure, and monitor these APIs", "Product, inventory, and order APIs need lifecycle management, security, analytics, and partner readiness. Apigee is the full API management platform."),
    ("Cymbal Retail", 268): ("minimize application changes", "SQL Server and MySQL migrations with low operational overhead and minimal changes point to managed Cloud SQL engines."),
    ("Cymbal Retail", 269): ("without storing them in code or Kubernetes Secrets", "Application credentials should be centrally stored and accessed by workload identity. Secret Manager plus scoped GKE service-account access avoids embedding secrets."),
    ("Cymbal Retail", 270): ("diagnose issues, optimize cluster configurations", "The team wants AI assistance for Kubernetes operations and security findings. Gemini in Google Cloud helps explain, troubleshoot, and optimize cloud resources."),
    ("Cymbal Retail", 271): ("migration planning", "Replacing legacy integrations requires understanding data formats, dependencies, and proving the new event-driven architecture before migration."),
    ("Cymbal Retail", 272): ("only trusted, verified container images", "Container supply-chain enforcement needs scanning plus a deployment gate. Artifact Registry/Analysis finds vulnerabilities and Binary Authorization blocks untrusted images."),
    ("Cymbal Retail", 273): ("Redis cache and MongoDB database", "The source technologies identify the targets: Memorystore for Redis and Firestore with MongoDB compatibility for MongoDB-style workloads."),
    ("Cymbal Retail", 274): ("measure the success", "The AI catalog and commerce goals are business outcomes. Faster product launches, higher conversion, and lower inquiry volume measure whether those goals are working."),
    ("Cymbal Retail", 275): ("simulate thousands of concurrent user conversations", "Peak conversational-agent traffic must be validated with load simulation against the API, not by reviewing architecture diagrams."),
    ("Cymbal Retail", 276): ("reduce costs associated with manual processes", "Manual catalog management is being replaced by automation. A new serverless workflow is the refactor path that removes manual operating cost."),
    ("Cymbal Retail", 277): ("without impacting the shared development environment", "The developer needs isolated local Pub/Sub testing at no cost. The Pub/Sub emulator gives local API-compatible behavior."),

    ("KnightMotives Automotive", 305): ("millions of telemetry data points per minute", "High-rate vehicle telemetry with real-time lookup is a Bigtable time-series fit, while BigQuery serves later analytical queries."),
    ("KnightMotives Automotive", 306): ("external partner companies via APIs", "Partners should access only controlled data through governed APIs. Apigee provides credentials, rate limits, and API mediation without internal-system access."),
    ("KnightMotives Automotive", 307): ("proficient in SQL", "The team has petabytes in BigQuery and SQL skills, not Python/TensorFlow. BigQuery ML lets them train regression models directly with SQL."),
    ("KnightMotives Automotive", 308): ("thousands of PDF Service Manuals", "A technician assistant over service manuals is a RAG search-and-conversation use case. Vertex AI Agent Builder indexes PDFs and answers in natural language."),
    ("KnightMotives Automotive", 309): ("unacceptable latency", "Immediate drowsiness detection with intermittent 3G cannot depend on cloud inference. On-device TensorFlow Lite keeps inference local and fast."),
    ("KnightMotives Automotive", 310): ("only return aggregated data", "Sensitive raw GPS must not leak to partners. An API layer such as Apigee can enforce auth, quotas, and masking/aggregation before data leaves the system."),
    ("KnightMotives Automotive", 311): ("rarely accessed thereafter", "BigQuery data hot for three months and cold later should be partitioned by date so old partitions qualify for long-term storage pricing automatically."),
    ("KnightMotives Automotive", 312): ("moving average of engine temperature within a 5-minute window", "Streaming sensor windows at millions of events per second need Dataflow windowing, with Pub/Sub alerts for anomaly outputs."),
    ("KnightMotives Automotive", 313): ("large GPU cluster", "On-demand multi-node GPU training for deep learning is Vertex AI Training with distributed GPU configuration and automatic job teardown."),
    ("KnightMotives Automotive", 314): ("obfuscate the exact location", "Geo-masking before warehouse load is a de-identification task. Sensitive Data Protection can generalize or round GPS coordinates while retaining regional analysis value."),
    ("KnightMotives Automotive", 315): ("automatically retrain the model", "The full MLOps chain needs orchestration from ingestion through training, evaluation, and deployment. Vertex AI Pipelines coordinates those steps."),
    ("KnightMotives Automotive", 316): ("weekly written review", "Turning driving behavior metrics into friendly text feedback is a generative-language task. Gemini on Vertex AI can produce the coaching narrative from structured input."),
    ("KnightMotives Automotive", 317): ("statistical distribution of input data", "Winter changes input distributions, causing prediction drift/skew. Vertex AI Model Monitoring compares live features against the training baseline."),
    ("KnightMotives Automotive", 318): ("not allowed to leave the EU region", "The legal constraint is raw EU trip data residency. Process aggregates inside the EU and transfer only nonpersonal aggregate totals centrally."),
    ("KnightMotives Automotive", 319): ("loss of network connectivity", "Voice commands must work in tunnels, so ASR/NLU cannot rely on cloud calls. A compact on-device model on the infotainment chip is the feasible design."),

    ("Altostrat Media", 278): ("metadata extraction and content moderation", "Uploaded media needs managed video analysis and moderation rather than custom ML. Video Intelligence/Sensitive moderation APIs extract metadata and detect unsafe content."),
    ("Altostrat Media", 279): ("upload large media files", "Daily large media transfers during migration need fast private hybrid connectivity. Dedicated Interconnect is the high-throughput secure transfer option."),
    ("Altostrat Media", 280): ("video and audio content", "Summarizing multimodal media into text needs a generative multimodal model rather than a single-purpose speech or video labeler."),
    ("Altostrat Media", 281): ("topics, entities, and sentiment", "The metadata request spans language signals and visual recognition. Natural Language handles topics/entities/sentiment, while Video Intelligence handles objects/logos."),
    ("Altostrat Media", 282): ("centrally manage configurations and policies", "GKE deployments plus current and future on-prem clusters need GKE Enterprise/Anthos for fleet management, CI/CD modernization, and policy control."),
    ("Altostrat Media", 283): ("detect and filter inappropriate content", "Brand safety requires scalable detection on upload and a review trigger. Automated video moderation feeding a review process matches that workflow."),
    ("Altostrat Media", 284): ("private, reliable, low-latency connection", "Large media ingestion from on-prem with private reliable low latency points to Dedicated Interconnect, not public internet transfer."),
    ("Altostrat Media", 285): ("single pane of glass for observability", "Unified Kubernetes management needs GKE Enterprise/Anthos plus fleet/Config Management style controls for consistent policy and observability."),
    ("Altostrat Media", 286): ("access drops significantly after 30 days", "Media access cools over time. Lifecycle rules can move objects to colder classes after 30 days and archive older content automatically."),
    ("Altostrat Media", 287): ("complex, multi-turn conversations", "Advanced 24/7 support with backend tasks needs a conversational agent platform. Dialogflow CX is designed for complex multi-turn virtual agents."),
    ("Altostrat Media", 288): ("which features are contributing", "Stakeholders want feature attribution for a specific model prediction. Vertex Explainable AI provides prediction explanations."),
    ("Altostrat Media", 289): ("third-party identity providers", "External authenticated users need access without Google identities. Workload Identity Federation lets trusted external identities access Google Cloud resources securely."),
    ("Altostrat Media", 290): ("centralized dashboard", "Organization-wide security posture, IAM risks, public assets, and vulnerabilities are Security Command Center's core dashboard and finding use case."),
    ("Altostrat Media", 291): ("without routing traffic over the public internet", "On-prem systems need private access to Google APIs. Private Google Access for on-prem through hybrid connectivity keeps API traffic off the public internet."),
    ("Altostrat Media", 292): ("reliability and cost management", "Reliability and cost for GKE are supported by autoscaling/right-sizing plus resilient deployment patterns that avoid overprovisioning while maintaining availability."),
    ("Altostrat Media", 293): ("retrieval time of several hours is acceptable", "Ten-year rarely accessed archives with hours of retrieval tolerance fit Archive Storage, the lowest-cost class for this pattern."),
    ("Altostrat Media", 294): ("developer portal, enforce rate limiting and quotas", "Those are full API lifecycle management requirements. Apigee provides portals, quotas, rate limits, and usage analytics."),
    ("Altostrat Media", 295): ("local development and integration testing", "The developer wants to test Spanner-dependent code without a provisioned instance. The Cloud Spanner emulator is built for local integration testing."),
    ("Altostrat Media", 296): ("logs, metrics, and recent deployment events", "The SRE wants faster root-cause analysis from operational signals. Gemini in Google Cloud can summarize and correlate logs, metrics, and deployment context."),
    ("Altostrat Media", 297): ("uncontrolled scaling of Cloud Run instances", "The risk is runaway instance count and cost during upload bursts. Setting maximum Cloud Run instances caps scaling."),
    ("Altostrat Media", 298): ("continue using Prometheus", "They want Prometheus compatibility and Cloud Monitoring consolidation. Managed Service for Prometheus preserves PromQL-style metrics while integrating with Cloud Monitoring."),
    ("Altostrat Media", 299): ("automate builds, tests, and deployments", "A Google-native CI/CD platform for GKE build-test-deploy pipelines is Cloud Build/Cloud Deploy style managed CI/CD."),
    ("Altostrat Media", 300): ("content ingestion workflows", "A migration plan for ingestion must address data formats, dependencies, transfer patterns, and validation before moving workflows to Google Cloud."),
    ("Altostrat Media", 301): ("secure their GKE clusters", "GKE hardening usually requires private/control-plane restrictions and workload/deployment security controls rather than relying only on project IAM."),
    ("Altostrat Media", 302): ("proficient in SQL", "The recommendation model data is in BigQuery and the team knows SQL. BigQuery ML is the direct SQL-based path to train and deploy a model."),
    ("Altostrat Media", 303): ("predictable pricing", "Mixed scheduled and ad-hoc BigQuery workloads with performance isolation point to capacity-based reservations/slots rather than pure on-demand pricing."),
    ("Altostrat Media", 304): ("declarative approach", "Automating GKE and networking resources declaratively is infrastructure as code. Terraform or Config Controller-style declarative provisioning fits the requirement."),
}


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value).replace("’ s", "'s")).strip()


def load_rows(path):
    raw = json.loads(path.read_text())
    return raw["questions"] if isinstance(raw, dict) else raw


def answer_letters(answer):
    if isinstance(answer, list):
        letters = []
        for item in answer:
            text = str(item).strip()
            match = re.match(r"^([A-E])\b\.?", text)
            if match:
                letters.append(match.group(1))
    else:
        text = str(answer).strip()
        letters = re.findall(r"\b([A-E])\s*\.", text)
        if not letters:
            letters = re.findall(r"\b([A-E])\b", text)
    return "".join(dict.fromkeys(letters))


def answer_pattern(options, letters):
    parts = []
    for letter in letters:
        option = options.get(letter, "").strip()
        parts.append(f"{letter}: {option}")
    return " | ".join(parts)


def md_escape(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_reference(data):
    counts = Counter(row.get("caseStudy") or "Non-case" for row in data)
    lines = [
        "# Full GCP PCA Study Set",
        "",
        "This set contains real crawled ExamTopics questions from 2024 to now, older real case-study questions from the 360-question crawl, and uploaded case-study JSON questions provided by the user. No generated questions are included.",
        "",
        "| Group | Questions |",
        "|---|---:|",
        f"| Altostrat Media | {counts['Altostrat Media']} |",
        f"| Cymbal Retail | {counts['Cymbal Retail']} |",
        f"| EHR Healthcare | {counts['EHR Healthcare']} |",
        f"| KnightMotives Automotive | {counts['KnightMotives Automotive']} |",
        f"| Non-case 2024-now dump | {counts['Non-case']} |",
        "",
        "## Questions",
        "",
        "| Ref | Case study | Source | Keyword | Why keyword | Answer |",
        "|---|---|---|---|---|---|",
    ]
    for row in data:
        lines.append(
            "| "
            + " | ".join(
                md_escape(x)
                for x in [
                    row["ref"],
                    row.get("caseStudy") or "Non-case",
                    row.get("sourceType", ""),
                    row["cue"],
                    row["cueWhy"],
                    row["answerLetters"],
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main():
    base = [row for row in json.loads(DATA_PATH.read_text()) if row.get("sourceType") != "Uploaded case JSON"]
    next_id = max(row["id"] for row in base) + 1
    seen = {normalize_text(row["questionText"]).lower() for row in base}
    uploaded = []
    duplicate_uploads = []

    for case, path in FILES:
        for raw in load_rows(path):
            qnum = int(raw["question_number"])
            question = normalize_text(raw["question"])
            key = question.lower()
            if key in seen:
                duplicate_uploads.append((case, qnum))
                continue
            seen.add(key)
            options = {str(k): normalize_text(v) for k, v in raw["options"].items()}
            letters = answer_letters(raw["answer"])
            if not letters:
                raise SystemExit(f"Could not parse answer letters for {case} Q{qnum}: {raw['answer']!r}")
            if (case, qnum) not in CUES:
                raise SystemExit(f"Missing cue for {case} Q{qnum}")
            trigger, why = CUES[(case, qnum)]
            uploaded.append(
                {
                    "id": next_id,
                    "year": 2026,
                    "topic": 9,
                    "questionNumber": qnum,
                    "ref": f"Uploaded / {case} Q{qnum}",
                    "cue": f"{case} + {trigger}",
                    "category": "Case Study",
                    "answerLetters": letters,
                    "answerPattern": answer_pattern(options, letters),
                    "questionText": question,
                    "options": [{"label": k, "text": options[k]} for k in sorted(options)],
                    "url": "",
                    "isNew": True,
                    "sourceType": "Uploaded case JSON",
                    "caseStudy": case,
                    "sortOrder": 202690000 + qnum,
                    "cueWhy": why,
                }
            )
            next_id += 1

    data = base + sorted(uploaded, key=lambda row: (row["caseStudy"], row["questionNumber"]))
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    REF_PATH.write_text(build_reference(data))

    index = INDEX_PATH.read_text()
    start = index.index("const DATA = ") + len("const DATA = ")
    end = index.index("];let mode=", start) + 1
    index = index[:start] + json.dumps(data, ensure_ascii=False) + index[end:]
    index = index.replace("GCP PCA Full Real Study", "GCP PCA Full Case Study")
    index = index.replace(
        "2024-now real questions plus older real case-study questions from the 360-question crawl. No generated questions.",
        "2024-now dump questions plus uploaded case-study JSON questions. No generated questions.",
    )
    index = re.sub(r'<strong id="totalCount">\d+</strong>', f'<strong id="totalCount">{len(data)}</strong>', index)
    index = re.sub(r'<strong id="matchCount">\d+</strong>', f'<strong id="matchCount">{len(data)}</strong>', index)
    index = index.replace(
        "$('sourceNote').textContent='Real crawled ExamTopics dump question. Case-study rows may come from older real questions in the 360-question crawl.';",
        "$('sourceNote').textContent=item.sourceType==='Uploaded case JSON'?'Uploaded case-study JSON provided by user. Not generated by the app.':'Real crawled ExamTopics dump question. Case-study rows may come from older real questions in the 360-question crawl.';",
    )
    index = index.replace(
        "<span>Non-case 2024-now dump</span><strong>${DATA.filter(x=>!x.caseStudy).length}</strong>",
        "<span>Non-case 2024-now dump</span><strong>${DATA.filter(x=>!x.caseStudy).length}</strong>",
    )
    INDEX_PATH.write_text(index)

    sw = SW_PATH.read_text()
    sw = re.sub(r'gcp-pca-study-v\d+', "gcp-pca-study-v11", sw, count=1)
    SW_PATH.write_text(sw)

    print(f"Imported {len(uploaded)} uploaded rows")
    if duplicate_uploads:
        print("Skipped duplicates:", duplicate_uploads)


if __name__ == "__main__":
    main()
