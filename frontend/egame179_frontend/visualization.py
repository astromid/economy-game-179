import altair as alt
import pandas as pd
import pyecharts
from pyecharts import options as opts

Y_MAX_SCALE = 1.05
MAX_THETA = 0.48


def stocks_chart(
    df: pd.DataFrame,
    x_shorthand: str,
    y_shorthand: str,
    color_shorthand: str | None,
    chart_size: dict[str, int],
) -> alt.Chart:
    """Line chart with relation between value and cycles.

    Args:
        df (pd.DataFrame): Dataframe with data in record format (after .melt()).
        x_shorthand (str): altair X shorthand.
        y_shorthand (str): altair Y shorthand.
        color_shorthand (str | None): shorthand for color differentiating column.
        chart_size (dict[str, int]): chart size in pixels (width, height).

    Returns:
        alt.Chart: rendered altair chart with interactivity.
    """
    x_field = x_shorthand.split(":")[0]
    y_field = y_shorthand.split(":")[0]

    chart = alt.Chart(df)  # type: ignore
    alt_x = alt.X(
        x_shorthand,  # type: ignore
        scale=alt.Scale(domain=(1, df[x_field].max() + 1)),  # type: ignore
        axis=alt.Axis(tickMinStep=1),  # type: ignore
    )
    alt_y = alt.Y(
        y_shorthand,  # type: ignore
        scale=alt.Scale(domain=(0, Y_MAX_SCALE * df[y_field].max())),  # type: ignore
    )

    alt_line = chart.mark_line(point=True)  # type: ignore
    if color_shorthand is None:
        alt_line = alt_line.encode(x=alt_x, y=alt_y)
    else:
        alt_line = alt_line.encode(x=alt_x, y=alt_y, color=color_shorthand)

    nearest = alt.selection(
        type="single",  # type: ignore
        nearest=True,
        on="mouseover",
        fields=[x_field],
        empty="none",
    )
    layer = alt.layer(
        alt_line,
        chart.mark_point().encode(x=x_shorthand, opacity=alt.value(0)).add_selection(nearest),  # selectors
        alt_line.mark_point().encode(  # points
            opacity=alt.condition(
                predicate=nearest,
                if_true=alt.value(1),
                if_false=alt.value(0),
            ),
        ),
        chart.mark_rule(color="gray").encode(x=x_shorthand).transform_filter(nearest),  # type: ignore # rules
        alt_line.mark_text(align="left", dx=5, dy=-5).encode(  # text
            text=alt.condition(nearest, y_shorthand, alt.value(" ")),
        ),
    )
    return layer.properties(**chart_size).interactive()


def radar_chart(thetas: dict[str, float]) -> pyecharts.charts.Radar:
    """Radar chart for theta visualization.

    Args:
        thetas (dict[str, float]): _description_

    Returns:
        pyecharts.charts.Radar: _description_
    """
    radar = pyecharts.charts.Radar()
    indicators = [opts.RadarIndicatorItem(name=market, max_=MAX_THETA) for market in thetas]
    radar.add_schema(schema=indicators)
    radar.add("", data=[{"name": "theta", "value": list(thetas.values())}])
    return radar
