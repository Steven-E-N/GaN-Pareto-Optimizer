"""
Pareto backend for the GaN dashboard demo.

The included data is synthetic demonstration data, not measured GaN data.
Replace it with engineering-model or simulation results when available.
"""

import numpy as np
import pandas as pd


def apply_constraints(
    designs: pd.DataFrame,
    max_junction_temp_c: float = 125.0,
    min_vds_margin_x: float = 1.5,
) -> pd.DataFrame:
    """
    Check whether each design passes the example engineering constraints.

    This function does NOT calculate GaN physics. It checks values that are
    already present in the dataset and adds two columns:
      - feasible: True if the design passes the checks
      - constraint_violations: a text explanation if it fails
    """

    # Make a copy so the original dataset is not modified.
    result = designs.copy()

    # Create an empty list of failure reasons for every row/design.
    reasons = [[] for _ in range(len(result))]

    # Check junction temperature only if that column exists in the dataset.
    if "junction_temp_c" in result.columns:
        # Convert values to numbers. Invalid text becomes NaN.
        values = pd.to_numeric(
            result["junction_temp_c"], errors="coerce"
        ).to_numpy()

        # Check the temperature of each design.
        for i, value in enumerate(values):
            if not np.isfinite(value):
                # Missing, infinite, or invalid temperature cannot pass the check.
                reasons[i].append("Missing/invalid junction temperature")
            elif value > max_junction_temp_c:
                # Record a failure if temperature exceeds the configured limit.
                reasons[i].append(
                    f"Junction temperature > {max_junction_temp_c:g} °C"
                )

    # Check voltage margin only if that column exists in the dataset.
    if "vds_margin_x" in result.columns:
        # Convert values to numbers. Invalid text becomes NaN.
        values = pd.to_numeric(
            result["vds_margin_x"], errors="coerce"
        ).to_numpy()

        # Check the voltage margin of each design.
        for i, value in enumerate(values):
            if not np.isfinite(value):
                # Missing, infinite, or invalid margin cannot pass the check.
                reasons[i].append("Missing/invalid Vds margin")
            elif value < min_vds_margin_x:
                # Record a failure if the margin is below the configured minimum.
                reasons[i].append(
                    f"Vds margin < {min_vds_margin_x:g}×"
                )

    # A design is feasible if its list of failure reasons is empty.
    result["feasible"] = [not row for row in reasons]

    # Convert each list of failure reasons into readable text.
    # If there are no failures, store "None".
    result["constraint_violations"] = [
        "; ".join(row) if row else "None" for row in reasons
    ]

    # Return the copied dataset with the two new columns.
    return result


# Explanation of apply_constraints():
# This function labels designs as feasible or infeasible using the temperature
# and Vds-margin limits passed to it. The default values are demonstration
# placeholders only; the project's hardware team must confirm the real limits.


def run_pareto(
    designs: pd.DataFrame,
    selected_objectives: list[str],
    objective_columns: dict[str, str],
    objective_directions: dict[str, str],
    feasible_column: str = "feasible",
) -> dict:
    """
    Find Pareto-optimal designs among the feasible candidates.

    A design is dominated if another feasible design is at least as good in
    every selected objective and strictly better in at least one.

    The returned dictionary contains all valid designs, Pareto-optimal designs,
    dominated designs, infeasible designs, and a count of invalid rows excluded.
    """

    # Stop if the dataset was not provided or contains no rows.
    if designs is None or designs.empty:
        raise ValueError("The design dataset is empty.")

    # Pareto optimization needs at least two objectives to compare trade-offs.
    if len(selected_objectives) < 2:
        raise ValueError("Select at least two optimization objectives.")

    # Check that every selected objective has a column mapping and a direction.
    # Example: "Power Loss" -> "power_loss_w", direction -> "min".
    missing_config = [
        name
        for name in selected_objectives
        if name not in objective_columns or name not in objective_directions
    ]
    if missing_config:
        raise ValueError(
            "Missing objective configuration for: "
            + ", ".join(missing_config)
        )

    # Convert the selected objective labels into actual dataset column names.
    columns = [
        objective_columns[name] for name in selected_objectives
    ]

    # Make sure all required objective columns exist in the dataset.
    missing_columns = [
        column for column in columns if column not in designs.columns
    ]
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing_columns)
        )

    # Convert selected objective values to numeric values.
    # Invalid text or missing values become NaN.
    numeric = designs[columns].apply(pd.to_numeric, errors="coerce")
    values = numeric.to_numpy(dtype=float)

    # Keep rows where every selected objective is a finite number.
    valid_mask = np.isfinite(values).all(axis=1)

    # Count rows excluded because at least one selected objective was invalid.
    invalid_count = int((~valid_mask).sum())

    # Keep only valid rows and their objective values.
    valid = designs.loc[valid_mask].copy()
    values = values[valid_mask]

    # Stop if all designs were excluded due to invalid objective values.
    if valid.empty:
        raise ValueError(
            "No designs have valid values for the selected objectives."
        )

    # If constraints have not been checked, assume all rows are feasible.
    # This lets the Pareto function also be used without apply_constraints().
    if feasible_column not in valid.columns:
        valid[feasible_column] = True

        # Add a note so the frontend can tell constraints were not evaluated.
        if "constraint_violations" not in valid.columns:
            valid["constraint_violations"] = "Not evaluated"

    # Convert the feasibility column into a Boolean array.
    # Missing feasibility values are treated as False (infeasible).
    feasible_mask = (
        valid[feasible_column].fillna(False).astype(bool).to_numpy()
    )

    # Validate the direction for each objective.
    # "min" means lower values are better; "max" means higher values are better.
    directions = []
    for name in selected_objectives:
        direction = str(objective_directions[name]).lower()

        if direction not in ("min", "max"):
            raise ValueError(
                f"Direction for '{name}' must be 'min' or 'max'."
            )

        directions.append(direction)

    # Pareto comparisons should only be performed on feasible designs.
    scores = values[feasible_mask].copy()

    # Convert every "max" objective to a minimization objective by multiplying
    # its values by -1. This allows one comparison rule to handle both directions.
    for j, direction in enumerate(directions):
        if direction == "max":
            scores[:, j] *= -1

    # Initially assume every feasible design is Pareto-optimal.
    # A design will be marked False if another design dominates it.
    is_pareto = np.ones(len(scores), dtype=bool)

    # Compare every feasible design (i) against every other feasible design (j).
    for i in range(len(scores)):
        for j in range(len(scores)):

            # A design cannot dominate itself.
            if i == j:
                continue

            # Is design j as good as or better than design i on every objective?
            no_worse_everywhere = np.all(scores[j] <= scores[i])

            # Is design j strictly better than design i on at least one objective?
            strictly_better_somewhere = np.any(scores[j] < scores[i])

            # If both conditions are true, design j dominates design i.
            if no_worse_everywhere and strictly_better_somewhere:
                is_pareto[i] = False
                break  # No need to compare design i further once it is dominated.

    # Initially mark every valid design as not Pareto-optimal.
    valid["pareto_optimal"] = False

    # Get the original DataFrame index labels for feasible rows.
    # These labels let us assign the calculated results to the correct rows.
    valid_indices = valid.index[feasible_mask]

    # Assign the Pareto results to the feasible designs.
    valid.loc[valid_indices, "pareto_optimal"] = is_pareto

    # Return separate tables for the frontend to display.
    return {
        # Every valid design, with feasibility and Pareto labels.
        "all_designs": valid,

        # Feasible designs that are not dominated by another feasible design.
        "pareto_designs": valid.loc[
            valid["pareto_optimal"]
        ].copy(),

        # Feasible designs that are dominated by another feasible design.
        "dominated_designs": valid.loc[
            valid[feasible_column].astype(bool)
            & ~valid["pareto_optimal"]
        ].copy(),

        # Designs that failed the configured constraints.
        "infeasible_designs": valid.loc[
            ~valid[feasible_column].astype(bool)
        ].copy(),

        # Number of rows removed because objective values were invalid.
        "excluded_invalid_count": invalid_count,
    }


# Explanation of run_pareto():
# This is the main optimization function. It validates the input data, handles
# objectives to minimize or maximize, compares feasible candidates using Pareto
# dominance, and returns separate results for the frontend. It does not simulate
# the GaN inverter or calculate physical performance values by itself.
