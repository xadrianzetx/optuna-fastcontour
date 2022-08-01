# optuna-fastcontour

A drop-in replacement for `optuna.visualization.matplotlib.plot_contour`, build mostly because I wanted to check out Cython. Still, this implementation about 35% faster than Optuna's master, which itself is fast enough. Algorithm is an adaptation of the one [used by Plotly](https://github.com/plotly/plotly.js/blob/master/src/traces/heatmap/interp2d.js).

## Installation

```
git clone https://github.com/xadrianzetx/optuna-fastcontour
cd fastcontour && make install
```

## Usage

```python
import fastcontour
import optuna

def objective(trial):
    x = trial.suggest_float("x", -100, 100)
    y = trial.suggest_categorical("y", [-1, 0, 1])
    return x ** 2 + y

sampler = optuna.samplers.TPESampler(seed=10)
study = optuna.create_study(sampler=sampler)
study.optimize(objective, n_trials=30)
fastcontour.plot_contour(study, params=["x", "y"])
```
