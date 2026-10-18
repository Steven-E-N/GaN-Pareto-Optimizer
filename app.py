
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="GaN Pareto Optimizer",
    page_icon="⚡",
    layout="wide"
)

# Dashboard styling
st.markdown("""
<style>
.stApp {
    background-color: #0b1424;
    color: #e8eef7;
}

[data-testid="stSidebar"] {
    background-color: #152438;
}

[data-testid="stMetric"] {
    background-color: #182a40;
    padding: 18px;
    border-radius: 10px;
    border: 1px solid #293d55;
}

[data-testid="stMetricLabel"] * {
    color: #aebfd3 !important;
}

[data-testid="stMetricValue"] * {
    color: white !important;
}

.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label {
    color: #e8eef7;
}

div.stButton > button[kind="primary"] {
    background-color: #148f83;
    color: white;
    border: none;
    border-radius: 8px;
}

div.stButton > button[kind="primary"]:hover {
    background-color: #19aa9b;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# Load the candidate designs
try:
    designs = pd.read_csv("data/designs.csv")
except FileNotFoundError:
    st.error("The file data/designs.csv was not found.")
    st.stop()

objectives = {
    "Power Loss": ("power_loss_w", "min"),
    "Footprint": ("footprint_cm2", "min"),
    "Efficiency": ("efficiency_percent", "max"),
    "Cost": ("cost_usd", "min"),
    "Junction Temperature": ("junction_temp_c", "min")
}


# Sidebar
with st.sidebar:
    st.title("⚡ GaN Optimizer")
    st.caption("Multi-Objective Optimization")

    st.divider()
    st.write(f"Available designs: {len(designs)}")
    st.caption("Data source: designs.csv")


# Main page
st.title("GaN Pareto Optimization")
st.write("Explore GaN inverter designs and analyze trade-offs between different objectives.")

st.divider()

st.subheader("Design Requirements")
st.caption("Enter the desired operating conditions.")

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

st.caption("Operating requirements will be connected to design filtering later.")

st.divider()

st.subheader("Optimization Objectives")
st.write("Choose the parameters you want to optimize.")

selected = st.multiselect(
    "Select objectives",
    options=list(objectives.keys()),
    default=["Power Loss", "Footprint"]
)

for name in selected:
    direction = objectives[name][1]
    st.caption(f"{name}: {direction.upper()}")

st.write("")

run = st.button(
    "Run Pareto Optimization",
    type="primary",
    use_container_width=True
)


if run:
    if len(selected) < 2:
        st.error("Please select at least two objectives.")
    else:
        try:
            #from pareto import run_pareto (waiting for nazha's part)

            chosen_objectives = {
                objectives[name][0]: objectives[name][1]
                for name in selected
            }

            results = run_pareto(designs, chosen_objectives) #(waiting for nazha)

            st.session_state["results"] = results
            st.session_state["last_objectives"] = selected.copy()

            st.success("Optimization completed successfully!")

        except ImportError:
            st.warning("The Pareto algorithm has not been connected yet.")

        except Exception as error:
            st.error(f"Optimization failed: {error}")


st.divider()

# Results overview
st.subheader("Design Overview")

results = st.session_state.get("results")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Designs", len(designs))

with col2:
    if results is not None:
        st.metric("Pareto-Optimal", int(results["pareto_optimal"].sum()))
    else:
        st.metric("Pareto-Optimal", "—")

with col3:
    st.metric("Minimum Power Loss", f"{designs['power_loss_w'].min()} W")

with col4:
    st.metric("Best Efficiency", f"{designs['efficiency_percent'].max()} %")


# Interactive graph
st.divider()
st.subheader("Design Visualization")
st.caption("Compare designs by selecting the parameters for each axis.")

col1, col2 = st.columns(2)

with col1:
    x_axis = st.selectbox(
        "X-Axis",
        options=list(objectives.keys()),
        index=1
    )

with col2:
    y_axis = st.selectbox(
        "Y-Axis",
        options=list(objectives.keys()),
        index=0
    )

if x_axis == y_axis:
    st.warning("Please select two different objectives.")
else:
    x_column = objectives[x_axis][0]
    y_column = objectives[y_axis][0]

    plot_data = designs.copy()

    if results is not None:
        plot_data = results.copy()
        plot_data["Status"] = plot_data["pareto_optimal"].map({
            True: "Pareto-Optimal",
            False: "Dominated"
        })

        fig = px.scatter(
            plot_data,
            x=x_column,
            y=y_column,
            color="Status",
            hover_name="design_id",
            color_discrete_map={
                "Pareto-Optimal": "#20c7a5",
                "Dominated": "#5687bb"
            }
        )
    else:
        fig = px.scatter(
            plot_data,
            x=x_column,
            y=y_column,
            hover_name="design_id"
        )

        fig.update_traces(marker_color="#20c7a5")

    fig.update_traces(
        marker=dict(
            size=13,
            line=dict(width=1, color="white")
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1424",
        plot_bgcolor="#152438",
        font=dict(color="#e8eef7"),
        height=500,
        xaxis_title=x_axis,
        yaxis_title=y_axis
    )

    st.plotly_chart(fig, use_container_width=True)

    if results is None:
        st.info("Showing candidate designs. Run optimization once the algorithm is connected.")
    else:
        st.caption(
            "Pareto classification is based on: "
            + ", ".join(st.session_state["last_objectives"])
        )


# Pareto-optimal results
if results is not None:
    st.divider()
    st.subheader("Pareto-Optimal Designs")

    optimal_designs = results[results["pareto_optimal"]]

    st.dataframe(
        optimal_designs,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Pareto Results",
        data=results.to_csv(index=False),
        file_name="pareto_results.csv",
        mime="text/csv"
    )


# Design comparison
st.divider()
st.subheader("Design Comparison")

design_ids = designs["design_id"].tolist()

selected_designs = st.multiselect(
    "Select designs to compare",
    options=design_ids,
    default=design_ids[:2]
)

if selected_designs:
    comparison = designs[
        designs["design_id"].isin(selected_designs)
    ]

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


# Full dataset
with st.expander("View All Designs"):
    st.dataframe(
        designs,
        use_container_width=True,
        hide_index=True
    )
