import streamlit as st

def load_css():

    st.markdown("""
    <style>

    .stApp {
        background:
        linear-gradient(
            180deg,
            #F8FAFC,
            #EEF4FF
        );
    }

    .navbar {

        background:
        linear-gradient(
            90deg,
            #0F172A,
            #1E3A8A
        );

        color: white;

        padding: 22px;

        border-radius: 18px;

        font-size: 32px;

        font-weight: 700;

        margin-bottom: 25px;
    }

    .kpi-card {

        background: white;

        border-radius: 20px;

        padding: 25px;

        box-shadow:
        0px 8px 24px rgba(0,0,0,0.08);

        margin-bottom: 20px;
    }

    .kpi-title {

        color: #64748B;

        font-size: 16px;
    }

    .kpi-value {

        color: #0F172A;

        font-size: 34px;

        font-weight: 700;
    }

    </style>
    """, unsafe_allow_html=True)


# -----------------------------------
# COLOR SYSTEM
# -----------------------------------

PRIMARY_BG = "#F7F9FC"
CARD_BG = "#FFFFFF"

TEXT_DARK = "#0F172A"
TEXT_MEDIUM = "#334155"

GRID = "#E2E8F0"

COLOR_SEQUENCE = [
    "#2563EB",
    "#14B8A6",
    "#F59E0B",
    "#8B5CF6",
    "#EF4444",
    "#06B6D4"
]

# -----------------------------------
# GLOBAL STREAMLIT CSS
# -----------------------------------

STREAMLIT_STYLE = """
<style>

.main {
    background-color: #F7F9FC;
}

div[data-testid="stPlotlyChart"] {
    background-color: white;
    padding: 1rem;
    border-radius: 18px;
    box-shadow: 0px 4px 18px rgba(15, 23, 42, 0.08);
    border: 1px solid #E2E8F0;
}

.section-title {
    font-size: 30px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 1rem;
}

</style>
"""

# -----------------------------------
# FIGURE STYLE FUNCTION
# -----------------------------------

def apply_figma_theme(fig, title=""):

    fig.update_layout(

        height=760,

        paper_bgcolor=PRIMARY_BG,
        plot_bgcolor=CARD_BG,

        font=dict(
            family="Inter, Arial",
            size=13,
            color=TEXT_DARK
        ),

        title=dict(
            text=title,
            x=0.5,
            xanchor="center",
            font=dict(
                size=24,
                color=TEXT_DARK
            )
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        margin=dict(
            l=30,
            r=30,
            t=90,
            b=30
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False
    )

    return fig
