# Uplift Service

The MVP exposes a two-model uplift baseline interface. If scikit-learn is installed, callers can plug in estimators; otherwise the included baseline computes segment-level treatment/control deltas.

Future adapters:

- EconML
- CausalML
- uplift random forests
- AUUC and Qini evaluation reports
