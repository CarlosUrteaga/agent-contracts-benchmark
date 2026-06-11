# Change Protocol

## Strategy: `evolutionary`

Start from `T0` and apply changes in order:

`T0 -> C1 -> C2 -> C3 -> C4 -> C5 -> C6`

After each step:

1. implement only the current step
2. run the required tests
3. fix failures if necessary
4. record metrics and run ledger artifacts
5. update `IMPLEMENTATION_PLAN.md`
6. commit with a structured message
7. stop

No future change may be implemented early.

## Strategy: `final-spec`

Start from the corresponding arm baseline and implement the final `C6` system directly.

After the implementation:

1. run the required tests
2. fix failures if necessary
3. record metrics and run ledger artifacts
4. update `IMPLEMENTATION_PLAN.md`
5. commit with a structured message
6. stop

## Execution Mode

Ralph-loop is the default execution mechanism for benchmark trajectories. `codex` remains a valid executor value for controlled reruns or manual reproduction.

## Branch Creation Constraint

Experiment branches must be created only after `t0-common` and all arm baselines already exist. Protocol scaffold scripts do not create those prerequisite branches.
