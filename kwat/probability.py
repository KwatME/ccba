from numpy import absolute, apply_along_axis, isnan, log2, nan, product, s_, unique

from .density import get_density
from .grid import get_1d_grid, get_1d_grid_resolution, plot as grid_plot
from .plot import plot_plotly


def get_probability(nu_po_di, ba_=(), co__=(), pl=True, di_=()):

    co_po_di, de_ = get_density(nu_po_di, ba_=ba_, co__=co__, pl=pl, di_=di_)

    pr_ = de_ / (
        de_.sum() * product([get_1d_grid_resolution(co_) for co_ in co_po_di.T])
    )

    if pl:

        grid_plot(co_po_di, pr_, di_=di_, nu="Probability")

    return co_po_di, pr_


def _get_probability(ar):

    return ar / ar.sum()


def get_posterior_probability(nu_po_di, ta=nan, ba_=(), co__=(), pl=True, di_=()):

    co_po_di, pr_ = get_probability(nu_po_di, ba_=ba_, co__=co__, pl=pl, di_=di_)

    ta_ = co_po_di[:, -1]

    pr___ = pr_.reshape([co_.size for co_ in get_1d_grid(co_po_di)])

    po___ = apply_along_axis(_get_probability, -1, pr___) * get_1d_grid_resolution(ta_)

    po_ = po___.reshape(co_po_di.shape[0])

    if pl:

        grid_plot(co_po_di, po_, di_=di_, nu="Posterior Probability")

    if isnan(ta):

        return co_po_di, po_

    else:

        taco_ = unique(ta_)

        ie = absolute(taco_ - ta).argmin()

        ie_ = s_[ie :: taco_.size]

        co_po_dino = co_po_di[ie_, :-1]

        pono_ = po_[ie_]

        if pl:

            grid_plot(
                co_po_dino,
                pono_,
                di_=di_[:-1],
                nu="P({} = {:.2e} (~{}) | {})".format(
                    di_[-1], taco_[ie], ta, *di_[:-1]
                ),
            )

        return co_po_dino, pono_


def plot_nomogram(pr1, pr2, na_, TODO1, TODO2, pa=""):

    n_da = len(na_)

    layout = {
        "title": {
            "text": "Nomogram",
        },
        "xaxis": {
            "title": {
                "text": "Log Odd Ratio",
            },
        },
        "yaxis": {
            "title": {
                "text": "Evidence",
            },
            "tickvals": list(range(1 + n_da)),
            "ticktext": ["Prior", *na_],
        },
    }

    trace = {
        "showlegend": False,
    }

    data = [
        {
            "x": [0, log2(pr2 / pr1)],
            "y": [0] * 2,
            "marker": {
                "color": "#080808",
            },
            **trace,
        }
    ]

    for ie in range(n_da):

        po1_ = TODO1[ie]

        po2_ = TODO2[ie]

        ra_ = log2((po2_ / po1_) / (pr2 / pr1))

        plot_plotly(
            {
                "data": [
                    {
                        "name": "P(Target = 0)",
                        "y": po1_,
                    },
                    {
                        "name": "P(Target = 1)",
                        "y": po2_,
                    },
                    {
                        "name": "Log Odd Ratio",
                        "y": ra_,
                    },
                ],
                "layout": {
                    "title": {
                        "text": na_[ie],
                    },
                },
            }
        )

        data.append(
            {
                "x": [ra_.min(), ra_.max()],
                "y": [1 + ie] * 2,
                **trace,
            }
        )

    plot_plotly(
        {
            "data": data,
            "layout": layout,
        },
        pa=pa,
    )
