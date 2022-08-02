from dataclasses import dataclass

import numpy as np
import pytest

from fastcontour._interpolation import _interpolate


@dataclass
class _ContourAxes:
    x: np.ndarray
    y: np.ndarray


@dataclass
class _ContourValues:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


class _ContourDataBuilder:
    def get_values(self) -> _ContourValues:

        x = np.array([0.0, 9.0], dtype=np.float64)
        y = np.array([0.0, 9.0], dtype=np.float64)
        z = np.array([100.0, 100.0], dtype=np.float64)
        return _ContourValues(x, y, z)

    def get_axes(self, n_points: int) -> _ContourAxes:

        x = np.linspace(0, n_points - 1, n_points, dtype=np.float64)
        y = x = np.linspace(0, n_points - 1, n_points, dtype=np.float64)
        return _ContourAxes(x, y)


@pytest.fixture
def contour_data() -> _ContourDataBuilder:
    return _ContourDataBuilder()


def test_output_type(contour_data: _ContourDataBuilder) -> None:

    n_points = 10
    axes = contour_data.get_axes(n_points)
    values = contour_data.get_values()
    out = _interpolate(values.x, values.y, values.z, axes.x, axes.y, n_points)
    assert isinstance(out, np.ndarray)


def test_output_shape(contour_data: _ContourDataBuilder) -> None:

    n_points = 10
    axes = contour_data.get_axes(n_points)
    values = contour_data.get_values()
    out = _interpolate(values.x, values.y, values.z, axes.x, axes.y, n_points)
    assert out.ndim == 1
    assert out.shape[0] == n_points**2


def test_output_is_finite(contour_data: _ContourDataBuilder) -> None:

    n_points = 10
    axes = contour_data.get_axes(n_points)
    values = contour_data.get_values()
    out = _interpolate(values.x, values.y, values.z, axes.x, axes.y, n_points)
    assert all(np.isfinite(out))


def test_known_values_in_output(contour_data: _ContourDataBuilder) -> None:

    n_points = 10
    axes = contour_data.get_axes(n_points)
    values = contour_data.get_values()
    out = _interpolate(values.x, values.y, values.z, axes.x, axes.y, n_points)
    for x, y, z in zip(values.x, values.y, values.z):
        index = int(y * n_points + x)
        assert out[index] == z
