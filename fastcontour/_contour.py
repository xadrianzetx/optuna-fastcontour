from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from matplotlib.colors import Colormap
from matplotlib.contour import ContourSet
import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes
import numpy as np
from optuna.study import Study
from optuna.trial import FrozenTrial
from optuna.visualization._contour import _AxisInfo
from optuna.visualization._contour import _ContourInfo
from optuna.visualization._contour import _get_contour_info
from optuna.visualization._contour import _SubContourInfo

from fastcontour._interpolation import _interpolate


CONTOUR_POINT_NUM = 100


def plot_contour(
    study: Study,
    params: Optional[List[str]] = None,
    *,
    target: Optional[Callable[[FrozenTrial], float]] = None,
    target_name: str = "Objective Value",
) -> "Axes":
    """Plot the parameter relationship as contour plot in a study with Matplotlib.
    Note that, if a parameter contains missing values, a trial with missing values is not plotted.
    .. seealso::
        Please refer to :func:`optuna.visualization.plot_contour` for an example.
    Warnings:
        Output figures of this Matplotlib-based
        :func:`~optuna.visualization.matplotlib.plot_contour` function would be different from
        those of the Plotly-based :func:`~optuna.visualization.plot_contour`.
    Example:
        The following code snippet shows how to plot the parameter relationship as contour plot.
        .. plot::
            import optuna
            def objective(trial):
                x = trial.suggest_float("x", -100, 100)
                y = trial.suggest_categorical("y", [-1, 0, 1])
                return x ** 2 + y
            sampler = optuna.samplers.TPESampler(seed=10)
            study = optuna.create_study(sampler=sampler)
            study.optimize(objective, n_trials=30)
            optuna.visualization.matplotlib.plot_contour(study, params=["x", "y"])
    Args:
        study:
            A :class:`~optuna.study.Study` object whose trials are plotted for their target values.
        params:
            Parameter list to visualize. The default is all parameters.
        target:
            A function to specify the value to display. If it is :obj:`None` and ``study`` is being
            used for single-objective optimization, the objective values are plotted.
            .. note::
                Specify this argument if ``study`` is being used for multi-objective optimization.
        target_name:
            Target's name to display on the color bar.
    Returns:
        A :class:`matplotlib.axes.Axes` object.
    """

    info = _get_contour_info(study, params, target, target_name)
    return _get_contour_plot(info)


def _get_contour_plot(info: _ContourInfo) -> "Axes":

    sorted_params = info.sorted_params
    sub_plot_infos = info.sub_plot_infos
    reverse_scale = info.reverse_scale
    target_name = info.target_name

    if len(sorted_params) <= 1:
        _, ax = plt.subplots()
        return ax
    n_params = len(sorted_params)

    plt.style.use("ggplot")  # Use ggplot style sheet for similar outputs to plotly.
    if n_params == 2:
        # Set up the graph style.
        fig, axs = plt.subplots()
        axs.set_title("Contour Plot")
        cmap = _set_cmap(reverse_scale)

        cs = _generate_contour_subplot(sub_plot_infos[0][0], axs, cmap)
        if isinstance(cs, ContourSet):
            axcb = fig.colorbar(cs)
            axcb.set_label(target_name)
    else:
        # Set up the graph style.
        fig, axs = plt.subplots(n_params, n_params)
        fig.suptitle("Contour Plot")
        cmap = _set_cmap(reverse_scale)

        # Prepare data and draw contour plots.
        cs_list = []
        for x_i in range(len(sorted_params)):
            for y_i in range(len(sorted_params)):
                ax = axs[y_i, x_i]
                cs = _generate_contour_subplot(sub_plot_infos[y_i][x_i], ax, cmap)
                if isinstance(cs, ContourSet):
                    cs_list.append(cs)
        if cs_list:
            axcb = fig.colorbar(cs_list[0], ax=axs)
            axcb.set_label(target_name)

    return axs


def _set_cmap(reverse_scale: bool) -> "Colormap":
    cmap = "Blues_r" if not reverse_scale else "Blues"
    return plt.get_cmap(cmap)


class _LabelEncoder:
    def __init__(self) -> None:
        self.labels: List[str] = []

    def fit(self, labels: List[str]) -> "_LabelEncoder":
        self.labels = sorted(set(labels))
        return self

    def transform(self, labels: List[str]) -> List[int]:
        return [self.labels.index(label) for label in labels]

    def fit_transform(self, labels: List[str]) -> List[int]:
        return self.fit(labels).transform(labels)

    def get_labels(self) -> List[str]:
        return self.labels

    def get_indices(self) -> List[int]:
        return list(range(len(self.labels)))


def _calculate_griddata(
    xaxis: _AxisInfo,
    yaxis: _AxisInfo,
    z_values_dict: Dict[Tuple[int, int], float],
) -> Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    List[int],
    List[str],
    List[int],
    List[str],
    np.ndarray,
    np.ndarray,
]:

    x_values = []
    y_values = []
    z_values = []
    for x_value, y_value in zip(xaxis.values, yaxis.values):
        if x_value is not None and y_value is not None:
            x_values.append(x_value)
            y_values.append(y_value)
            x_i = xaxis.indices.index(x_value)
            y_i = yaxis.indices.index(y_value)
            z_values.append(z_values_dict[(x_i, y_i)])

    # FIXME Avoid unnecessary copies.
    z_values = np.array(z_values, dtype=np.float64)  # type: ignore
    # Return empty values when x or y has no value.
    if len(x_values) == 0 or len(y_values) == 0:
        # FIXME Complexity here is a bit too much.
        return np.array([]), np.array([]), np.array([]), [], [], [], [], np.array([]), np.array([])

    def _calculate_axis_data(
        axis: _AxisInfo,
        values: Sequence[Union[str, float]],
    ) -> Tuple[np.ndarray, List[str], List[int], np.ndarray]:

        # Convert categorical values to int.
        cat_param_labels = []  # type: List[str]
        cat_param_pos = []  # type: List[int]
        if axis.is_cat:
            enc = _LabelEncoder()
            returned_values = np.array(enc.fit_transform(list(map(str, values))), dtype=np.float64)
            cat_param_labels = enc.get_labels()
            cat_param_pos = enc.get_indices()
        else:
            returned_values = np.array(values, dtype=np.float64)

        # For x and y, create 1-D array of evenly spaced coordinates on linear or log scale.
        if axis.is_log:
            ci = np.logspace(
                np.log10(axis.range[0]),
                np.log10(axis.range[1]),
                CONTOUR_POINT_NUM,
                dtype=np.float64,
            )
        else:
            ci = np.linspace(axis.range[0], axis.range[1], CONTOUR_POINT_NUM, dtype=np.float64)

        return ci, cat_param_labels, cat_param_pos, returned_values

    xi, cat_param_labels_x, cat_param_pos_x, transformed_x_values = _calculate_axis_data(
        xaxis,
        x_values,
    )
    yi, cat_param_labels_y, cat_param_pos_y, transformed_y_values = _calculate_axis_data(
        yaxis,
        y_values,
    )

    # Calculate grid data points.
    zi: np.ndarray = np.array([], dtype=np.float64)
    # Create irregularly spaced map of trial values
    # and interpolate it with Plotly's interpolation formulation.
    if xaxis.name != yaxis.name:
        zi = _interpolate(
            transformed_x_values, transformed_y_values, z_values, xi, yi, CONTOUR_POINT_NUM
        ).reshape(CONTOUR_POINT_NUM, CONTOUR_POINT_NUM)

    return (
        xi,
        yi,
        zi,
        cat_param_pos_x,
        cat_param_labels_x,
        cat_param_pos_y,
        cat_param_labels_y,
        transformed_x_values,
        transformed_y_values,
    )


def _generate_contour_subplot(info: _SubContourInfo, ax: "Axes", cmap: "Colormap") -> "ContourSet":

    if len(info.xaxis.indices) < 2 or len(info.yaxis.indices) < 2:
        ax.label_outer()
        return ax

    ax.set(xlabel=info.xaxis.name, ylabel=info.yaxis.name)
    ax.set_xlim(info.xaxis.range[0], info.xaxis.range[1])
    ax.set_ylim(info.yaxis.range[0], info.yaxis.range[1])

    if info.xaxis.name == info.yaxis.name:
        ax.label_outer()
        return ax

    (
        xi,
        yi,
        zi,
        x_cat_param_pos,
        x_cat_param_label,
        y_cat_param_pos,
        y_cat_param_label,
        x_values,
        y_values,
    ) = _calculate_griddata(info.xaxis, info.yaxis, info.z_values)
    cs = None
    if len(zi) > 0:
        if info.xaxis.is_log:
            ax.set_xscale("log")
        if info.yaxis.is_log:
            ax.set_yscale("log")
        if info.xaxis.name != info.yaxis.name:
            # Contour the gridded data.
            ax.contour(xi, yi, zi, 15, linewidths=0.5, colors="k")
            cs = ax.contourf(xi, yi, zi, 15, cmap=cmap.reversed())
            # Plot data points.
            ax.scatter(
                x_values,
                y_values,
                marker="o",
                c="black",
                s=20,
                edgecolors="grey",
                linewidth=2.0,
            )
    if info.xaxis.is_cat:
        ax.set_xticks(x_cat_param_pos)
        ax.set_xticklabels(x_cat_param_label)
    if info.yaxis.is_cat:
        ax.set_yticks(y_cat_param_pos)
        ax.set_yticklabels(y_cat_param_label)
    ax.label_outer()
    return cs
