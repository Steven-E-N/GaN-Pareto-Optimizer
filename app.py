import pandas as pd
import plotly.express as px
import streamlit as st
from pareto import run_pareto

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="GaN Pareto Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DASHBOARD STYLING
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1424;
        color: #e8eef7;
    }

    [data-testid="stSidebar"] {
        background-color: #152438;
    }

    [data-testid="stSidebar"] * {
        color: #e8eef7 !important;
    }

    [data-testid="stMetric"] {
        background-color: #182a40;
        border: 1px solid #293d55;
        padding: 20px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] * {
        color: #aebfd3 !important;
    }

    [data-testid="stMetricValue"] * {
        color: #ffffff !important;
    }

    [data-testid="stWidgetLabel"] * {
        color: #c6d5e6 !important;
    }

    .stApp h1, .stApp h2, .stApp h3,
    .stApp p, .stApp label {
        color: #e8eef7;
    }

    [data-testid="stNumberInput"] input {
        background-color: #182a40;
        color: #ffffff;
    }

    div.stButton > button[kind="primary"] {
        background-color: #148f83;
        color: #ffffff;
        border: none;
        border-radius: 8px;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #19aa9b;
        color: #ffffff;
    }

    [data-testid="stSidebar"] hr {
        border-color: #34465e;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.title("⚡ GaN Optimizer")
    st.caption("Multi-Objective Design Platform")

    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Optimization", "Design History"],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("GaN Pareto Optimization • Prototype")

# ==========================================
# 4. MAIN DASHBOARD
# ==========================================

st.title("GaN Pareto Optimization")

st.caption(
    "Engineering dashboard for multi-objective "
    "GaN inverter design analysis"
)

st.divider()

# ==========================================
# 5. SUMMARY METRIC CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Designs", "—")

with col2:
    st.metric("Pareto-Optimal", "—")

with col3:
    st.metric("Minimum Power Loss", "—")

with col4:
    st.metric("Best Efficiency", "—")

st.write("")

# ==========================================
# 6. ENGINEERING INPUTS
# ==========================================

st.markdown("### Design Requirements")

st.caption(
    "Configure the operating conditions "
    "of the GaN inverter."
)

with st.container(border=True):

    col1, col2, col3 = st.columns(3)

    with col1:
        voltage = st.number_input(
            "Input Voltage (V)",
            min_value=0.0,
            value=400.0,
            step=10.0
        )

    with col2:
        current = st.number_input(
            "Output Current (A)",
            min_value=0.0,
            value=20.0,
            step=1.0
        )

    with col3:
        frequency = st.number_input(
            "Switching Frequency (kHz)",
            min_value=1.0,
            value=100.0,
            step=10.0
        )

# ==========================================
# 7. OPTIMIZATION OBJECTIVES
# ==========================================

st.markdown("### Optimization Objectives")

st.caption(
    "Select the objectives used to compare "
    "different GaN inverter designs."
)

objective_options = {
    "Power Loss": "min",
    "Footprint": "min",
    "Efficiency": "max",
    "Cost": "min",
    "Junction Temperature": "min"
}

selected_objectives = st.multiselect(
    "Select Optimization Objectives",
    options=list(objective_options.keys()),
    default=["Power Loss", "Footprint"]
)

# ==========================================
# 8. RUN OPTIMIZATION
# ==========================================

st.divider()

if st.button(
    "Run Pareto Optimization",
    type="primary",
    use_container_width=True
):

    if len(selected_objectives) < 2:
        st.error(
            "Please select at least two "
            "optimization objectives."
        )

    else:
        st.success(
            "Design requirements submitted successfully!"
        )

        st.markdown("### Selected Configuration")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Input Voltage", f"{voltage} V")

        with col2:
            st.metric("Output Current", f"{current} A")

        with col3:
            st.metric(
                "Switching Frequency",
                f"{frequency} kHz"
            )

        st.write(
            "**Selected Objectives:**",
            ", ".join(selected_objectives)
        )

        st.info(
            "The Pareto optimization engine "
            "will be connected in the next stage."
        )




# ==========================================
# 9. DESIGN DATA AND VISUALIZATION
# ==========================================

from pathlib import Path

st.divider()
st.markdown("### GaN Design Visualization")
st.caption("Explore candidate inverter designs and compare performance.")

# Load sample design data
data_path = Path(__file__).resolve().parent / "data" / "designs.csv"
designs = pd.read_csv(data_path)

# Connect the frontend objective names to CSV columns
objective_columns = {
    "Power Loss": "power_loss_w",
    "Footprint": "footprint_cm2",
    "Efficiency": "efficiency_percent",
    "Cost": "cost_usd",
    "Junction Temperature": "junction_temp_c"
}

# Select what to display on each axis
col1, col2 = st.columns(2)

with col1:
    x_objective = st.selectbox(
        "X-Axis",
        options=list(objective_columns.keys()),
        index=1
    )

with col2:
    y_objective = st.selectbox(
        "Y-Axis",
        options=list(objective_columns.keys()),
        index=0
    )

# Build the interactive scatter plot
if x_objective == y_objective:
    st.warning("Please choose two different objectives.")
else:
    fig = px.scatter(
        designs,
        x=objective_columns[x_objective],
        y=objective_columns[y_objective],
        hover_name="design_id",
        hover_data={
            "efficiency_percent": True,
            "cost_usd": True,
            "junction_temp_c": True
        },
        title=f"{y_objective} vs {x_objective}"
    )

    fig.update_traces(
        marker=dict(
            size=13,
            color="#20c7b0",
            line=dict(width=1, color="#ffffff")
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1424",
        plot_bgcolor="#152438",
        font=dict(color="#e8eef7"),
        height=520,
        xaxis_title=x_objective,
        yaxis_title=y_objective,
        margin=dict(l=30, r=30, t=60, b=30)
    )

    st.plotly_chart(fig, use_container_width=True)

# Display candidate design information
with st.expander("View All GaN Designs"):
    st.dataframe(designs, use_container_width=True, hide_index=True)

st.caption(
    "Demonstration dataset. The Pareto algorithm "
    "will identify non-dominated designs after integration."
)
