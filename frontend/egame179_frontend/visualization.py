import altair as alt
import pandas as pd


def cycles_history_chart(
    df: pd.DataFrame,
    x_shorthand: str,
    y_shorthand: str,
    color_shorthand: str | None,
    max_x: int,
    max_y: float,
    width: int,
    height: int,
) -> alt.Chart:
    chart = alt.Chart(df)  # type: ignore
    alt_x = alt.X(
        x_shorthand,  # type: ignore
        scale=alt.Scale(domain=(0, max_x)),  # type: ignore
        axis=alt.Axis(tickMinStep=1),  # type: ignore
    )
    alt_y = alt.Y(y_shorthand, scale=alt.Scale(domain=(0, 1.05 * max_y)))  # type: ignore

    alt_line = chart.mark_line(point=True)  # type: ignore
    if color_shorthand is None:
        alt_line = alt_line.encode(x=alt_x, y=alt_y)
    else:
        alt_line = alt_line.encode(x=alt_x, y=alt_y, color=color_shorthand)

    nearest = alt.selection(
        type="single",  # type: ignore
        nearest=True,
        on="mouseover",
        fields=[x_shorthand.split(":")[0]],
        empty="none",
    )
    selectors = chart.mark_point().encode(x=x_shorthand, opacity=alt.value(0))
    selectors = selectors.add_selection(nearest)

    points = alt_line.mark_point().encode(
        opacity=alt.condition(
            predicate=nearest,
            if_true=alt.value(1),
            if_false=alt.value(0),
        ),
    )

    text = alt_line.mark_text(align="left", dx=5, dy=-5)
    text = text.encode(text=alt.condition(nearest, y_shorthand, alt.value(" ")))

    rules = chart.mark_rule(color="gray").encode(x=x_shorthand).transform_filter(nearest)  # type: ignore
    layer = alt.layer(alt_line, selectors, points, rules, text)
    return layer.properties(width=width, height=height).interactive()
