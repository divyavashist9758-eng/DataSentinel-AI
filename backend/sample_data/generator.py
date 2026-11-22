import os
import json
import numpy as np
import pandas as pd

def generate_sample_datasets():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    np.random.seed(42)

    # 1. Clean Baseline Dataset: customers_clean.csv (500 records)
    n = 500
    customer_ids = [f"CUST-{1000 + i}" for i in range(n)]
    ages = np.random.normal(loc=42, scale=10, size=n).astype(int)
    ages = np.clip(ages, 18, 75)
    incomes = np.random.normal(loc=68000, scale=18000, size=n).astype(int)
    incomes = np.clip(incomes, 20000, 160000)
    credit_scores = np.random.normal(loc=710, scale=45, size=n).astype(int)
    credit_scores = np.clip(credit_scores, 400, 850)
    states = np.random.choice(["CA", "NY", "TX", "FL", "IL", "WA"], size=n, p=[0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
    churn = np.random.choice([0, 1], size=n, p=[0.82, 0.18])

    clean_df = pd.DataFrame({
        "customer_id": customer_ids,
        "age": ages,
        "income": incomes,
        "credit_score": credit_scores,
        "state": states,
        "is_churned": churn
    })
    clean_csv_path = os.path.join(output_dir, "customers_clean.csv")
    clean_df.to_csv(clean_csv_path, index=False)
    print(f"Generated clean baseline: {clean_csv_path} ({len(clean_df)} rows)")

    # 2. Drifted & Mutated Dataset: customers_drifted.csv (550 records)
    # Introducing demographic drift (younger age cohort), nulls in income, added column 'loyalty_tier'
    n_drift = 550
    drift_ids = [f"CUST-{2000 + i}" for i in range(n_drift)]
    drift_ages = np.random.normal(loc=26, scale=6, size=n_drift).astype(int)  # Significant shift from 42 -> 26!
    drift_ages = np.clip(drift_ages, 18, 60)
    drift_incomes = np.random.normal(loc=44000, scale=12000, size=n_drift).astype(float)
    drift_incomes = np.clip(drift_incomes, 15000, 120000)
    
    # Inject missing null values in income (12% null rate)
    null_idx = np.random.choice(n_drift, size=int(n_drift * 0.12), replace=False)
    drift_incomes[null_idx] = np.nan

    drift_scores = np.random.normal(loc=650, scale=55, size=n_drift).astype(int)
    drift_scores = np.clip(drift_scores, 400, 850)
    drift_states = np.random.choice(["CA", "NY", "TX", "FL", "IL", "WA", "AZ"], size=n_drift)  # New category "AZ"!
    drift_churn = np.random.choice([0, 1], size=n_drift, p=[0.70, 0.30])
    loyalty_tier = np.random.choice(["BRONZE", "SILVER", "GOLD", "PLATINUM"], size=n_drift)  # Added column!

    drifted_df = pd.DataFrame({
        "customer_id": drift_ids,
        "age": drift_ages,
        "income": drift_incomes,
        "credit_score": drift_scores,
        "state": drift_states,
        "is_churned": drift_churn,
        "loyalty_tier": loyalty_tier
    })
    drift_csv_path = os.path.join(output_dir, "customers_drifted.csv")
    drifted_df.to_csv(drift_csv_path, index=False)
    print(f"Generated drifted dataset: {drift_csv_path} ({len(drifted_df)} rows)")

    # 3. Anomalous Transactions: transactions_anomalous.json (300 records)
    # Containing extreme currency outliers (100x decimal misplacement) and duplicates
    records = []
    merchants = ["Amazon", "Uber", "Starbucks", "Target", "Apple", "Walmart", "Delta Airlines"]
    for i in range(300):
        tx_id = f"TX-{5000 + i}"
        cust_id = f"CUST-{1000 + (i % 150)}"
        merchant = np.random.choice(merchants)
        amount = round(float(np.random.exponential(scale=45.0) + 5.0), 2)
        
        # Inject anomalies: extreme 100x scale currency errors
        if i in [14, 42, 88, 156, 212]:
            amount = round(amount * 100.0, 2)  # e.g. $4500 coffee
        elif i in [99, 101]:
            amount = -abs(amount)  # Invalid negative amount

        records.append({
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "merchant": merchant,
            "amount": amount,
            "timestamp": "2026-11-20T10:00:00Z"
        })

    # Duplicate 8 records
    records.extend(records[:8])

    json_path = os.path.join(output_dir, "transactions_anomalous.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Generated anomalous JSON dataset: {json_path} ({len(records)} records)")

if __name__ == "__main__":
    generate_sample_datasets()

