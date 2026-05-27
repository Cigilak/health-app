import streamlit as st
from analytics import (
    load_data,
    get_kpis,
    get_provider_spend,
    get_state_cost,
    get_high_risk,
    get_high_provider_cost
)


from styles import (
    STREAMLIT_STYLE,
    apply_figma_theme,
    load_css
)

import plotly.express as px

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(
    page_title="Healthcare Analytics",
    layout="wide"
)

# -----------------------------------
# Load Executive Styling
# -----------------------------------
load_css()

# -----------------------------------
# Executive Navbar
# -----------------------------------
st.markdown("""
<div class="navbar">
 <center> Provider Network Leakage Intelligence </center>
</div>
""", unsafe_allow_html=True)

# -----------------------------------
# Load Dataset
# -----------------------------------
df = load_data()

# -----------------------------------
# TOP FILTER BAR
# -----------------------------------
st.markdown("""
<div class="filter-header">
Executive Filters
</div>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns([2,2,1])

# -----------------------------------
# State Filter
# -----------------------------------
states = sorted(
    df["state"]
    .dropna()
    .unique()
)

with f1:

    selected_state = st.selectbox(
        "Select State",
        ["All"] + states
    )

# -----------------------------------
# Provider Filter
# -----------------------------------
providers = sorted(
    df["provider_type"]
    .dropna()
    .unique()
)

with f2:

    selected_provider = st.selectbox(
        "Select Provider Type",
        ["All"] + providers
    )

# -----------------------------------
# Refresh Button
# -----------------------------------
with f3:

    st.markdown("<br>", unsafe_allow_html=True)

    refresh = st.button(
        "Refresh Dashboard"
    )

# -----------------------------------
# Apply Filters
# -----------------------------------
filtered_df = df.copy()

if selected_state != "All":

    filtered_df = filtered_df[
        filtered_df["state"] ==
        selected_state
    ]

if selected_provider != "All":

    filtered_df = filtered_df[
        filtered_df["provider_type"] ==
        selected_provider
    ]

# -----------------------------------
# KPI Section
# -----------------------------------
kpis = get_kpis(filtered_df)

st.markdown("""
<div class="section-title">
Executive KPIs
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

metrics = [
    ("Providers", f"{int(kpis['providers']):,}"),
    ("Beneficiaries", f"{int(kpis['beneficiaries']):,}"),
    
    (
        "Average Payment",
        f"${float(str(kpis['avg_payment']).replace('$', '').replace(',', '')):,.2f}"
    ),
    
    ("Services", f"{int(kpis['services']):,}")
]

for col, metric in zip(
    [c1,c2,c3,c4],
    metrics
):
    with col:

        st.markdown(f"""
        <div class="kpi-card">

        <div class="kpi-title">
        {metric[0]}
        </div>

        <div class="kpi-value">
        {metric[1]}
        </div>

        </div>
        """, unsafe_allow_html=True)

# -----------------------------------
# State Cost and Avg Service Comparison Analysis
# -----------------------------------

top_df = (
    filtered_df[
        [
            "state",
            "HcpcsDesc",
            "RucaDesc",
            "avg_payment_amount",
            "total_services"
        ]
    ]

    # Reduce memory usage
    .astype({
        "state": "category",
        "HcpcsDesc": "category",
        "RucaDesc": "category"
    })

    .groupby(
        ["state", "HcpcsDesc", "RucaDesc"],
        observed=True,
        sort=False
    )

    .agg(
        AVG_mdcr_payment=("avg_payment_amount", "mean"),
        Sum_total_services=("total_services", "sum")
    )

    .nlargest(
        25,
        columns="AVG_mdcr_payment"
    )

    .reset_index()
)

st.markdown(
    STREAMLIT_STYLE,
    unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "Service Volume",
    "Procedure Hierarchy"
])

with tab1:
    fig = px.scatter(
    top_df,
    x="Sum_total_services",
    y="AVG_mdcr_payment",
    size="Sum_total_services",
    color="RucaDesc",
    hover_name="HcpcsDesc",
    facet_col="state")
    fig.update_layout(
        height=700,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )   

with tab2:
    fig = px.treemap(
    top_df,
    path=["state", "RucaDesc", "HcpcsDesc"],
    values="AVG_mdcr_payment",
    color="Sum_total_services",
    color_continuous_scale="Blues",
    hover_name="HcpcsDesc",
    hover_data={
        "AVG_mdcr_payment": ":,.2f",
        "Sum_total_services": ":,"
    }
    )
    fig.update_layout(
        height=700,
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# -----------------------------------
# Provider Spend Analytics
# -----------------------------------
st.markdown("""
<div class="section-title">
Provider Cost Analytics
</div>
""", unsafe_allow_html=True)

provider_spend = (
    filtered_df
    .groupby("provider_type")[
        "avg_payment_amount"
    ]
    .mean()
    .reset_index()
    .sort_values(
        "avg_payment_amount",
        ascending=False
    )
    .head(10)
)

fig1 = px.bar(
    provider_spend,
    x="avg_payment_amount",
    y="provider_type",
    orientation="h",
    color="avg_payment_amount",
    color_continuous_scale="Blues"
)

fig1.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# -----------------------------------
# State Cost Analysis
# -----------------------------------
st.markdown("""
<div class="section-title">
Regional Cost Distribution
</div>
""", unsafe_allow_html=True)

state_cost = (
    filtered_df
    .groupby("state")[
        "avg_payment_amount"
    ]
    .mean()
    .reset_index()
)

fig2 = px.choropleth(
    state_cost,
    locations="state",
    locationmode="USA-states",
    color="avg_payment_amount",
    scope="usa",
    color_continuous_scale="Blues"
)

fig2.update_layout(
    paper_bgcolor="white",
    geo_bgcolor="white",
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------------
# High Risk Providers
# -----------------------------------
st.markdown("""
<div class="section-title">
Potential High Leakage Providers
</div>
""", unsafe_allow_html=True)

high_risk = get_high_risk(
    filtered_df
)

st.dataframe(
    high_risk,
    use_container_width=True,
    height=400
)


# -----------------------------------
# Footer
# -----------------------------------
st.markdown("""
<hr>

<center>

Healthcare Executive Intelligence Platform

<br>

Streamlit | Copy Right | Cigil Achenkunju

</center>
""", unsafe_allow_html=True)
