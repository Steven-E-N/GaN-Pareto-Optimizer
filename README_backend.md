# My Pareto Backend

I created `pareto.py`, which contains the first simple version of the backend for our Pareto project.

It has two functions:

- `apply_constraints()` checks whether a design passes the example temperature and voltage-margin limits.
- `run_pareto()` compares designs based on the objectives we choose and separates them into Pareto-optimal, dominated, and infeasible designs.

I also included `data/designs.csv`, which contains example data so we can test the code before we receive real GaN data.

The data and constraint limits are only for testing. They are not real GaN measurements or confirmed engineering limits.

