# polar_grid_code.py
import matplotlib.pyplot as plt
import numpy as np
import argparse
from fractions import Fraction
from typing import List, Optional
import os

# Default configuration values
DEFAULT_ASPECT: str = "16:9"
DEFAULT_COLOR_SCHEME: str = "white-on-black"
DEFAULT_TRANSPARENT: bool = False
DEFAULT_ANGLE_ORIGIN: str = "E"
DEFAULT_RADIAL_LINES: int = 24
DEFAULT_EDGE_THICKNESS: float = 5
DEFAULT_GRIDLINE_THICKNESS: float = 2
DEFAULT_RADIUS_SCALE: str = "inverse"
DEFAULT_RING_THICKNESS: float = 5
DEFAULT_RING_ALPHA: float = 0.9
DEFAULT_ANGLE_MODE: str = "angular"  # 'angular' or 'arc'
DEFAULT_DIRECTION: str = "counterclockwise"  # 'clockwise' or 'counterclockwise'


def format_radian_labels(num_lines: int) -> List[str]:
    labels: List[str] = []
    for angle in np.linspace(0, 2 * np.pi, num_lines, endpoint=False):
        frac = Fraction(angle / np.pi).limit_denominator()
        if frac.numerator == 0:
            labels.append("0")
        elif frac == 1:
            labels.append("π")
        elif frac.denominator == 1:
            labels.append(f"{frac.numerator}π")
        elif frac.numerator == 1:
            labels.append(f"π/{frac.denominator}")
        else:
            labels.append(f"{frac.numerator}π/{frac.denominator}")
    return labels


def scale_radii(num_rings: int, scale_type: str = "linear") -> np.ndarray:
    x = np.linspace(0.1, 1, num_rings)
    if scale_type == "linear":
        return x
    elif scale_type == "log":
        return np.logspace(np.log10(0.1), 0, num_rings)
    elif scale_type == "sqrt":
        return np.sqrt(np.linspace(0, 1, num_rings))
    elif scale_type == "inverse":
        return 1 - np.logspace(-2, 0, num_rings)
    elif scale_type == "exp":
        return (np.exp(np.linspace(0, 1, num_rings)) - 1) / (np.e - 1)
    else:
        return x


def plot_polar_grid(
    output_aspect: str = DEFAULT_ASPECT,
    color_scheme: str = DEFAULT_COLOR_SCHEME,
    angle_marker: Optional[float] = None,
    transparent: bool = DEFAULT_TRANSPARENT,
    angle_origin: str = DEFAULT_ANGLE_ORIGIN,
    radial_lines: int = DEFAULT_RADIAL_LINES,
    filename: Optional[str] = None,
    edge_thickness: float = DEFAULT_EDGE_THICKNESS,
    gridline_thickness: float = DEFAULT_GRIDLINE_THICKNESS,
    radius_scale: str = DEFAULT_RADIUS_SCALE,
    angle_mode: str = DEFAULT_ANGLE_MODE,
    direction: str = DEFAULT_DIRECTION,
) -> None:
    fig_aspect_ratios: dict[str, tuple[float, float]] = {
        "1:1": (6, 6),
        "4:3": (8, 6),
        "16:9": (12, 6.75),
    }
    fig_size = fig_aspect_ratios.get(output_aspect, (12, 6.75))

    if color_scheme == "white-on-black":
        bg_color = "black"
        fg_color = "white"
    else:
        bg_color = "white"
        fg_color = "black"

    fig = plt.figure(figsize=fig_size, facecolor="none" if transparent else bg_color)
    ax = fig.add_subplot(111, polar=True, facecolor="none" if transparent else bg_color)

    ax.set_theta_zero_location(angle_origin)
    ax.set_theta_direction(-1 if direction == "clockwise" else 1)
    ax.set_rlabel_position(0)

    # Determine tick locations
    if angle_mode == "arc":
        ticks = np.array([i % (2 * np.pi) for i in range(radial_lines + 1)])
        labels = [str(i) for i in range(radial_lines + 1)]
    else:
        ticks = np.linspace(0, 2 * np.pi, radial_lines, endpoint=False)
        labels = format_radian_labels(radial_lines)

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    ax.grid(True, color=fg_color, linestyle="--", linewidth=gridline_thickness)
    ax.tick_params(colors=fg_color)
    ax.xaxis.label.set_color(fg_color)
    ax.yaxis.label.set_color(fg_color)

    for r in scale_radii(5, radius_scale):
        circle = plt.Circle(
            (0, 0),
            r,
            transform=ax.transData._b,
            color="gray",
            fill=False,
            linewidth=DEFAULT_RING_THICKNESS,
            alpha=DEFAULT_RING_ALPHA,
        )
        ax.add_artist(circle)

    edge_circle = plt.Circle(
        (0, 0),
        1,
        transform=ax.transData._b,
        color="gray",
        fill=False,
        linewidth=edge_thickness,
    )
    ax.add_artist(edge_circle)

    # Plot magenta line if angle_marker is provided
    if angle_marker is not None:
        ax.plot([angle_marker, angle_marker], [0, 1], color="magenta", linewidth=2)

    if filename and os.path.exists(os.path.dirname(filename) or "."):
        plt.savefig(filename, transparent=transparent, facecolor=fig.get_facecolor())
        print(f"Saved to {filename}")
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot a generic polar grid.")
    parser.add_argument(
        "--aspect",
        choices=["1:1", "4:3", "16:9"],
        default=DEFAULT_ASPECT,
        help="Output aspect ratio.",
    )
    parser.add_argument(
        "--color",
        choices=["white-on-black", "black-on-white"],
        default=DEFAULT_COLOR_SCHEME,
        help="Color scheme.",
    )
    parser.add_argument(
        "--transparent",
        action="store_true",
        default=DEFAULT_TRANSPARENT,
        help="Transparent background.",
    )
    parser.add_argument(
        "--origin",
        choices=["N", "E", "S", "W", "NW", "NE", "SW", "SE"],
        default=DEFAULT_ANGLE_ORIGIN,
        help="Angle origin (e.g. N for top, E for right).",
    )
    parser.add_argument(
        "--radials",
        type=int,
        default=DEFAULT_RADIAL_LINES,
        help="Number of radial lines.",
    )
    parser.add_argument(
        "--output", type=str, help="Filename to save the plot if the path exists."
    )
    parser.add_argument(
        "--scale",
        choices=["linear", "log", "sqrt", "inverse", "exp"],
        default=DEFAULT_RADIUS_SCALE,
        help="Scaling of radial rings.",
    )
    parser.add_argument(
        "--angle-mode",
        choices=["angular", "arc"],
        default=DEFAULT_ANGLE_MODE,
        help="Mode for radial ticks: angular (fractions of π) or arc (ticks at radians).",
    )
    parser.add_argument(
        "--direction",
        choices=["clockwise", "counterclockwise"],
        default=DEFAULT_DIRECTION,
        help="Direction of increasing angle.",
    )
    parser.add_argument(
        "--angle-marker",
        type=float,
        help="Angle in radians to draw a magenta line from center to edge.",
    )
    args = parser.parse_args()

    plot_polar_grid(
        output_aspect=args.aspect,
        color_scheme=args.color,
        transparent=args.transparent,
        angle_origin=args.origin,
        radial_lines=args.radials,
        filename=args.output,
        radius_scale=args.scale,
        angle_mode=args.angle_mode,
        direction=args.direction,
        angle_marker=args.angle_marker,
    )
