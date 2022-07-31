import matplotlib.pyplot as plt
import optuna

import fastcontour


def objective(trial):
    x = trial.suggest_float("x", -100, 100)
    y = trial.suggest_categorical("y", [-1, 0, 1])
    return x**2 + y


if __name__ == "__main__":
    sampler = optuna.samplers.TPESampler(seed=10)
    study = optuna.create_study(sampler=sampler)
    study.optimize(objective, n_trials=30)
    fastcontour.plot_contour(study, params=["x", "y"])
    plt.show()
