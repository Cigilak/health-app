import duckdb
from dotenv import load_dotenv
import os

load_dotenv()
PARQUET_FILE = os.getenv("PARQUET_PATH")

con = duckdb.connect()

# Load Dataset

def load_data():

    query = f"""
    SELECT
        Rndrng_Prvdr_Type AS provider_type,
        Rndrng_Prvdr_State_Abrvtn AS state,
        Rndrng_Prvdr_RUCA_Desc as RucaDesc,
        HCPCS_Desc as HcpcsDesc,
        Tot_Benes AS total_beneficiaries,
        Tot_Srvcs AS total_services,
        Avg_Mdcr_Pymt_Amt AS avg_payment_amount,
        Avg_Mdcr_Stdzd_Amt AS avg_mdcr_stdzd_amount

    FROM read_parquet('{PARQUET_FILE}')
    """

    return con.execute(query).df()


# KPI Metrics

def get_kpis(df):

    return {
        "providers": len(df),
        "beneficiaries":
            int(df["total_beneficiaries"].sum()),

        "avg_payment":
            f"${df['avg_payment_amount'].mean():,.0f}",

        "services":
            int(df["total_services"].sum())
    }


# Provider Spend

def get_provider_spend():

    query = f"""
    SELECT
        Rndrng_Prvdr_Type AS provider_type,

        AVG(Avg_Mdcr_Pymt_Amt)
        AS avg_payment

    FROM read_parquet('{PARQUET_FILE}')

    GROUP BY provider_type

    ORDER BY avg_payment DESC

    LIMIT 10
    """

    return con.execute(query).df()


# State Cost

def get_state_cost():

    query = f"""
    SELECT
        Rndrng_Prvdr_State_Abrvtn AS state,

        AVG(Avg_Mdcr_Pymt_Amt)
        AS avg_payment

    FROM read_parquet('{PARQUET_FILE}')

    GROUP BY state
    """

    return con.execute(query).df()


# High Risk Providers

def get_high_risk(df):

    threshold = df[
        "avg_payment_amount"
    ].quantile(0.90)

    return df[
        df["avg_payment_amount"] > threshold
    ]

## Providers that overcharge per state, service, and HP Codes with > $5000 avg payments
## AIM
#### Steering: Redirecting out-of-network speciality referrals to preferred, in-network surgeons.
#### Reimbursement: Transitioning top-billing providers to value-based care contracts.
#### Contracting: Negotiating bundled payment models with high-volume providers (Ortho, Cardio, etc.)

def get_high_provider_cost():

    query = f"""
    SELECT Rndrng_Prvdr_State_Abrvtn AS state, Rndrng_Prvdr_RUCA_Desc, HCPCS_Desc,
    AVG(Avg_Mdcr_Pymt_Amt) as AVG_mdcr_payment,
    AVG(Tot_Bene_Day_Srvcs) as AVG_Distinct_Services_Rendered,
    AVG(Avg_Mdcr_Stdzd_Amt) as AVG_MDCR_Standardzed_Service

    FROM read_parquet('{PARQUET_FILE}')
    Where Avg_Mdcr_Pymt_Amt >= 5000
    Group By Rndrng_Prvdr_State_Abrvtn, Rndrng_Prvdr_RUCA_Desc, HCPCS_Desc
    ORDER BY AVG_mdcr_payment DESC
    
    LIMIT 50
    """

    return con.execute(query).df()

### State and Provider Type comparison to see how we can provider better care based on payments and patient behav.
def get_state_specialty_payments():
    query = f"""
    SELECT
        Rndrng_Prvdr_State_Abrvtn AS state,
        Rndrng_Prvdr_Type,
        SUM(Avg_Mdcr_Pymt_Amt * Tot_Benes) AS total_payments
    FROM read_parquet('{PARQUET_FILE}')
    WHERE Rndrng_Prvdr_State_Abrvtn IS NOT NULL
    GROUP BY Rndrng_Prvdr_State_Abrvtn, Rndrng_Prvdr_Type
    ORDER BY Rndrng_Prvdr_State_Abrvtn DESC, total_payments DESC 
    LIMIT 100
    """

    return duckdb.execute(query).df()