from numpy import absolute, full, integer, isnan, median, nan, where
from sklearn.manifold import MDS

from .array import get_not_nan_unique, normalize
from .CONSTANT import RANDOM_SEED
from .dictionary import merge
from .geometry import convex_hull, triangulation
from .plot import (
    CATEGORICAL_COLORSCALE,
    COLORBAR,
    CONTINUOUS_COLORSCALE,
    get_color,
    make_colorscale,
    plot_plotly,
)


def map_point(pxpd, n, random_seed=RANDOM_SEED, **k_):

    pxd = MDS(
        n_components=n, random_state=random_seed, dissimilarity="precomputed", **k_
    ).fit_transform(pxpd)

    for i in range(n):

        pxd[:, i] = normalize(pxd[:, i], "0-1")

    return pxd


def pull_point(nxd, pxn):

    nd = nxd.shape[1]

    np = pxn.shape[0]

    pxd = full([np, nd], nan)

    for pi in range(np):

        p_ = pxn[pi, :]

        for di in range(nd):

            pxd[pi, di] = (p_ * nxd[:, di]).sum() / p_.sum()

    return pxd


def plot_node_point(
    node_name,
    node_,
    nxd,
    npame,
    point_,
    pxd,
    show_node_text=True,
    node_trace=None,
    point_trace=None,
    group_=None,
    group_colorscale=CATEGORICAL_COLORSCALE,
    _1d_grid=None,
    nd_probability_vector=None,
    nd_group_vector=None,
    score_name=None,
    score_=None,
    score_colorscale=CONTINUOUS_COLORSCALE,
    score_opacity=0.8,
    score_nan_opacity=0.08,
    point_highlight_=(),
    file_path=None,
):

    title = "{} {} and {} {}".format(node_.size, node_name, point_.size, npame)

    if score_name is not None:

        title = "{}<br>{}".format(title, score_name)

    axis = {
        "showgrid": False,
        "showline": False,
        "zeroline": False,
        "showticklabels": False,
    }

    layout = {
        "height": 880,
        "width": 880,
        "title": {
            "x": 0.5,
            "text": "<b>{}</b>".format(title),
            "font": {
                "size": 24,
                "color": "#4e40d8",
                "family": "Times New Roman, sans-serif",
            },
        },
        "yaxis": axis,
        "xaxis": axis,
        "annotations": [],
    }

    data = []

    (a_0, a_1) = triangulation(nxd)

    (b_0, b_1) = convex_hull(nxd)

    data.append(
        {
            "legendgroup": "Node",
            "name": "Line",
            "y": a_0 + b_0,
            "x": a_1 + b_1,
            "mode": "lines",
            "line": {"color": "#171412"},
        }
    )

    base = {
        "legendgroup": "Node",
        "name": node_name,
        "y": nxd[:, 0],
        "x": nxd[:, 1],
        "text": node_,
        "mode": "markers",
        "marker": {
            "size": 20,
            "color": "#23191e",
            "line": {"width": 1, "color": "#ebf6f7"},
        },
        "hoverinfo": "text",
    }

    if node_trace is not None:

        base = merge(base, node_trace)

    data.append(base)

    if show_node_text:

        arrowwidth = 1.6

        arrowcolor = "#ebf6f7"

        layout["annotations"] += [
            {
                "y": axis_0_coordinate,
                "x": axis_1_coordinate,
                "text": "<b>{}</b>".format(node),
                "font": {
                    "size": 16,
                    "color": "#23191e",
                    "family": "Gravitas One, monospace",
                },
                "borderpad": 2,
                "borderwidth": arrowwidth,
                "bordercolor": arrowcolor,
                "bgcolor": "#ffffff",
                "arrowwidth": arrowwidth,
                "arrowcolor": arrowcolor,
            }
            for node, (axis_0_coordinate, axis_1_coordinate) in zip(node_, nxd)
        ]

    if nd_group_vector is not None:

        data.append(
            {
                "type": "contour",
                "showlegend": False,
                "z": nd_probability_vector,
                "y": _1d_grid,
                "x": _1d_grid,
                "autocontour": False,
                "ncontours": 24,
                "contours": {"coloring": "none"},
            }
        )

        group_n = int(get_not_nan_unique(nd_group_vector).max() + 1)

        group_to_color = {
            group: get_color(group_colorscale, group / max(1, group_n - 1))
            for group in range(group_n)
        }

        for group in range(group_n):

            nd_group_probability_vector = nd_probability_vector.copy()

            nd_group_probability_vector[nd_group_vector != group] = nan

            data.append(
                {
                    "type": "heatmap",
                    "z": nd_group_probability_vector,
                    "y": _1d_grid,
                    "x": _1d_grid,
                    "colorscale": make_colorscale(
                        ("rgb(255, 255, 255)", group_to_color[group])
                    ),
                    "showscale": False,
                    "hoverinfo": "none",
                }
            )

    base = {
        "name": npame,
        "mode": "markers",
        "marker": {
            "size": 16,
            "color": "#20d9ba",
            "line": {"width": 0.8, "color": "#000000"},
        },
        "hoverinfo": "text",
    }

    if point_trace is not None:

        base = merge(base, point_trace)

    if score_ is not None:

        sort_index_ = absolute(score_).argsort()

        score_ = score_[sort_index_]

        point_ = point_[sort_index_]

        pxd = pxd[sort_index_]

        score_not_nan_ = get_not_nan_unique(score_)

        if all(isinstance(score, integer) for score in score_not_nan_):

            tickvals = ticktext = score_not_nan_

        else:

            tickvals = (
                score_not_nan_.min(),
                median(score_not_nan_),
                score_not_nan_.mean(),
                score_not_nan_.max(),
            )

            ticktext = tuple("{:.2e}".format(number) for number in tickvals)

        data.append(
            merge(
                base,
                {
                    "y": pxd[:, 0],
                    "x": pxd[:, 1],
                    "text": point_,
                    "marker": {
                        "color": score_,
                        "colorscale": score_colorscale,
                        "colorbar": {
                            **COLORBAR,
                            "tickmode": "array",
                            "tickvals": tickvals,
                            "ticktext": ticktext,
                        },
                        "opacity": where(
                            isnan(score_), score_nan_opacity, score_opacity
                        ),
                    },
                },
            )
        )

    elif group_ is not None:

        for group in range(group_n):

            name = "Group {}".format(group)

            index_ = group_ == group

            data.append(
                merge(
                    base,
                    {
                        "legendgroup": name,
                        "name": name,
                        "y": pxd[index_, 0],
                        "x": pxd[index_, 1],
                        "text": point_[index_],
                        "marker": {"color": group_to_color[group]},
                    },
                )
            )

    else:

        data.append({**base, "y": pxd[:, 0], "x": pxd[:, 1], "text": point_})

    for point in point_highlight_:

        (axis_0_coordinate, axis_1_coordinate) = pxd[point_ == point][0]

        layout["annotations"].append(
            {
                "y": axis_0_coordinate,
                "x": axis_1_coordinate,
                "text": "<b>{}</b>".format(point),
                "arrowhead": 2,
                "arrowwidth": 2,
                "arrowcolor": "#c93756",
                "standoff": None,
                "clicktoshow": "onoff",
            }
        )

    plot_plotly({"data": data, "layout": layout}, file_path=file_path)
