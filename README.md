# GaN Pareto Optimizer

A Python-based interactive dashboard for multi-objective optimization of Gallium Nitride (GaN) inverter designs using the **Pareto dominance principle**.

The project identifies non-dominated designs by comparing engineering objectives such as power loss, footprint, efficiency, cost, and junction temperature.

## Features

- **Multi-Objective Optimization:** Select two or more objectives to minimize or maximize.
- **Pareto Analysis:** Identify Pareto-optimal, dominated, and infeasible designs.
- **Engineering Constraints:** Evaluate designs against junction temperature and voltage safety-margin limits.
- **Interactive Visualization:** Explore design trade-offs using Plotly scatter plots.
- **Streamlit Dashboard:** View optimization results, engineering metrics, and design datasets.

## Technologies Used

- **Python** — Core programming language
- **Streamlit** — Interactive web dashboard
- **pandas** — Dataset processing
- **NumPy** — Pareto dominance calculations
- **Plotly** — Interactive data visualization

## Project Structure

```text
GaN-Pareto-Optimizer/
│
├── app.py              # Streamlit dashboard
├── pareto.py           # Pareto optimization backend
├── data/
│   └── designs.csv     # Sample GaN inverter designs
└── README.md           # Project documentation
```

## How It Works

1. Load candidate GaN inverter designs from a CSV dataset.
2. Check engineering constraints to identify feasible designs.
3. Select the optimization objectives.
4. Compare feasible designs using the Pareto dominance principle.
5. Identify non-dominated designs and visualize the results.

A design is considered **Pareto-optimal** if no other feasible design is at least as good in every selected objective and strictly better in at least one.

## Installation and Usage

**1. Clone the repository**

```bash
git clone https://github.com/Steven-E-N/GaN-Pareto-Optimizer.git
cd GaN-Pareto-Optimizer
```

**2. Install dependencies**

```bash
python -m pip install streamlit pandas numpy plotly
```

**3. Run the application**

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Current Limitations

This project is a functional prototype using synthetic demonstration data. It does not currently simulate GaN inverter behavior, generate new designs, or calculate engineering performance directly from operating conditions.

## Future Improvements

- Integrate real GaN inverter simulation datasets.
- Connect operating parameters to engineering models.
- Add Pareto-front visualization and additional filtering.
- Integrate AHP or TOPSIS for selecting preferred designs from the Pareto-optimal set.

## Project Status

**Prototype — Pareto optimization backend and interactive dashboard implemented.**
