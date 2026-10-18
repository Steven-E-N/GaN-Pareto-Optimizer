
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from pareto import apply_constraints, run_pareto

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
# 2. LOAD DESIGN DATA
# ==========================================

DATA_PATH = Path(__file__).resolve().parent / "data" / "designs.csv"

@st.cache_data
def load_designs():
    return pd.read_csv(DATA_PATH)

designs = load_designs()

objective_options = {
    "Power Loss": "min",
    "Footprint": "min",
    "Efficiency": "max",
    "Cost": "min",
    "Junction Temperature": "min"
}

objective_columns = {
    "Power Loss": "power_loss_w",
    "Footprint": "footprint_cm2",
    "Efficiency": "efficiency_percent",
    "Cost": "cost_usd",
    "Junction Temperature": "junction_temp_c"
}

# ==========================================
# 3. DASHBOARD STYLING
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
# 4. SIDEBAR NAVIGATION
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
# 5. MAIN DASHBOARD
# ==========================================

st.title("GaN Pareto Optimization")

st.caption(
    "Engineering dashboard for multi-objective "
    "GaN inverter design analysis"
)

st.divider()

# ==========================================
# 6. SUMMARY METRIC CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Designs", len(designs))

with col2:
    if "pareto_results" in st.session_state:
        results = st.session_state["pareto_results"]
        st.metric(
            "Pareto-Optimal",
            len(results["pareto_designs"])
        )
    else:
        st.metric("Pareto-Optimal", "—")

with col3:
    st.metric(
        "Minimum Power Loss",
        f"{designs['power_loss_w'].min():.2f} W"
    )

with col4:
    st.metric(
        "Best Efficiency",
        f"{designs['efficiency_percent'].max():.2f}%"
    )

st.write("")

# ==========================================
# 7. ENGINEERING INPUTS
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

st.caption(
    "Operating conditions are demonstration inputs. "
    "They are not yet connected to engineering simulations."
)

# ==========================================
# 8. OPTIMIZATION OBJECTIVES
# ==========================================

st.markdown("### Optimization Objectives")

st.caption(
    "Select the objectives used to compare "
    "different GaN inverter designs."
)

def clear_pareto_results():
    st.session_state.pop("pareto_results", None)


selected_objectives = st.multiselect(
    "Select Optimization Objectives",
    options=list(objective_options.keys()),
    default=["Power Loss", "Footprint"],
    on_change=clear_pareto_results
)

# ==========================================
# 9. RUN OPTIMIZATION
# ==========================================

st.divider()

if st.button(
    "Run Pareto Optimization",
    type="primary",
    use_container_width=True
):

    if len(selected_objectives) < 2:
        st.error(
            "Please select at least two optimization objectives."
        )

    else:
        try:
            # Apply engineering constraints
            constrained_designs = apply_constraints(designs)

            # Run Pareto optimization
            results = run_pareto(
                constrained_designs,
                selected_objectives,
                objective_columns,
                objective_options
            )

            # Store optimization results
            st.session_state["pareto_results"] = results

            st.success("Pareto optimization completed!")

        except ValueError as error:
            st.session_state.pop("pareto_results", None)
            st.error(f"Optimization failed: {error}")

# ==========================================
# 10. OPTIMIZATION RESULTS
# ==========================================

if "pareto_results" in st.session_state:

    results = st.session_state["pareto_results"]

    st.markdown("### Optimization Results")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Pareto-Optimal",
            len(results["pareto_designs"])
        )

    with col2:
        st.metric(
            "Dominated",
            len(results["dominated_designs"])
        )

    with col3:
        st.metric(
            "Infeasible",
            len(results["infeasible_designs"])
        )

    with col4:
        st.metric(
            "Invalid / Excluded",
            results["excluded_invalid_count"]
        )

    st.markdown("#### Pareto-Optimal Designs")

    st.dataframe(
        results["pareto_designs"],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "These designs are non-dominated among the feasible "
        "candidates for the selected objectives."
    )

# ==========================================
# 11. DESIGN DATA AND VISUALIZATION
# ==========================================

st.divider()

st.markdown("### GaN Design Visualization")

st.caption(
    "Explore candidate inverter designs and compare performance."
)

# Select visualization objectives
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

# Prepare visualization data
if "pareto_results" in st.session_state:

    results = st.session_state["pareto_results"]

    # Use the evaluated designs
    plot_designs = results["all_designs"].copy()

    # Identify dominated designs
    plot_designs["status"] = "Dominated"

    # Identify Pareto-optimal designs
    plot_designs.loc[
        plot_designs["pareto_optimal"], "status"
    ] = "Pareto-optimal"

    # Identify infeasible designs
    plot_designs.loc[
        ~plot_designs["feasible"], "status"
    ] = "Infeasible"

else:
    plot_designs = designs.copy()
    plot_designs["status"] = "Not evaluated"

# ==========================================
# 12. INTERACTIVE SCATTER PLOT
# ==========================================

if x_objective == y_objective:

    st.warning(
        "Please choose two different objectives."
    )

else:

    fig = px.scatter(
        plot_designs,
        x=objective_columns[x_objective],
        y=objective_columns[y_objective],
        hover_name="design_id",
        hover_data={
            "efficiency_percent": True,
            "cost_usd": True,
            "junction_temp_c": True
        },
        color="status",
        color_discrete_map={
            "Pareto-optimal": "#20c7b0",
            "Dominated": "#64748b",
            "Infeasible": "#ef4444",
            "Not evaluated": "#20c7b0"
        },
        title=f"{y_objective} vs {x_objective}"
    )

    fig.update_traces(
        marker=dict(
            size=13,
            line=dict(
                width=1,
                color="#ffffff"
            )
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
        legend_title_text="Design Classification",
        margin=dict(
            l=30,
            r=30,
            t=60,
            b=30
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    if "pareto_results" in st.session_state:
        st.caption(
            "Design classifications use all selected optimization "
            "objectives, which may differ from the two plotted axes."
        )

# ==========================================
# 13. DESIGN DATA TABLE
# ==========================================

with st.expander("View All GaN Designs"):

    st.dataframe(
        plot_designs,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Demonstration dataset. Pareto-optimal designs "
    "are identified using the selected optimization "
    "objectives and engineering constraints."
)
