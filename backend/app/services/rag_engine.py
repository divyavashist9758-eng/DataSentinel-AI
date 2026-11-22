import os
import json
import math
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import settings
from app.core.logging import logger

DEFAULT_KNOWLEDGE_BASE = [
    {
        "id": "kb-dq-01",
        "category": "data_quality_rule",
        "title": "Missing Primary Keys and Critical Identifiers",
        "content": "Columns marked as identifiers or foreign keys must maintain zero null rates. Null spikes in customer_id or transaction_id usually indicate upstream ETL ingestion partition failures or partial API timeouts.",
        "recommended_action": "Investigate upstream webhook retry queues or apply partition re-ingestion."
    },
    {
        "id": "kb-dq-02",
        "category": "data_quality_rule",
        "title": "Duplicate Record Frequency Bounds",
        "content": "Duplicate rows exceeding 0.5% in transactional datasets typically stem from retry logic without idempotency keys in streaming ingestion.",
        "recommended_action": "Apply deduplication keeping latest timestamp and enforce idempotency keying."
    },
    {
        "id": "kb-inc-104",
        "category": "previous_incident",
        "title": "Payment Amount 100x Scale Outlier Incident",
        "content": "Incident-104: A currency conversion module failure caused currency values to be ingested in cents rather than dollars for foreign accounts, causing extreme Isolation Forest anomalies in amount column.",
        "recommended_action": "Apply unit normalization and clip extreme values using IQR fence bounds."
    },
    {
        "id": "kb-inc-108",
        "category": "previous_incident",
        "title": "Unexpected Category Injection from Partner API",
        "content": "Incident-108: Partner service updated their status enum to include 'PENDING_VERIFICATION' without publishing a schema change notice, breaking downstream strict enum validators.",
        "recommended_action": "Update schema enum contract and map unexpected categories to fallback 'OTHER' category."
    },
    {
        "id": "kb-drift-03",
        "category": "historical_investigation",
        "title": "Age Demographic PSI Drift Post Marketing Campaign",
        "content": "PSI score jumped to 0.42 on age and income columns due to a new TikTok acquisition campaign targeting younger demographics. Data was valid but model retraining was required.",
        "recommended_action": "Validate upstream cohort shift; mark drift as verified business change and trigger model recalibration."
    },
    {
        "id": "kb-rem-05",
        "category": "approved_remediation",
        "title": "Median Imputation for Skewed Numerical Features",
        "content": "Approved standard remediation for missing continuous data with skewness > 1.0: Replace missing entries with median rather than mean to preserve robust distribution properties.",
        "recommended_action": "Apply median imputation with audit tracking of modified cell count."
    }
]

class RAGEngine:
    _instance = None

    def __init__(self):
        self.knowledge_items = list(DEFAULT_KNOWLEDGE_BASE)
        self.store_file = os.path.join(settings.RAG_STORE_DIR, "knowledge_store.json")
        self._load_store()

    def _load_store(self):
        """Load persistent knowledge store from disk if exists."""
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.knowledge_items = data
            except Exception as e:
                logger.warning(f"Could not load RAG store from disk: {e}")
        else:
            self._save_store()

    def _save_store(self):
        """Save persistent knowledge store to disk."""
        try:
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_items, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist RAG store: {e}")

    def add_knowledge_entry(self, entry: Dict[str, Any]):
        """Index a new verified incident, investigation, or remediation rule."""
        if "id" not in entry:
            entry["id"] = f"kb-custom-{len(self.knowledge_items) + 1}"
        self.knowledge_items.append(entry)
        self._save_store()
        logger.info(f"Added knowledge entry '{entry['id']}' to RAG store.")

    def _tokenize(self, text: str) -> set:
        """Tokenize text for keyword and BM25-style semantic matching."""
        import re
        words = re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', text.lower())
        return set(words)

    def retrieve_relevant_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant historical incidents and rules with match scores and citations."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.knowledge_items[:top_k]

        scored_items = []
        for item in self.knowledge_items:
            if category and item.get("category") != category:
                continue

            item_text = f"{item.get('title', '')} {item.get('content', '')} {item.get('recommended_action', '')}"
            item_tokens = self._tokenize(item_text)

            intersection = query_tokens & item_tokens
            if not intersection:
                score = 0.0
            else:
                # Jaccard / Cosine term overlap similarity
                score = len(intersection) / math.sqrt(len(query_tokens) * len(item_tokens))

            scored_items.append((score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, item in scored_items[:top_k]:
            res = dict(item)
            res["relevance_score"] = round(float(score), 4)
            res["citation"] = f"Source: {item['id']} ({item.get('title', '')})"
            results.append(res)

        return results

rag_engine = RAGEngine()

