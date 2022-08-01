import altair as alt
import pandas as pd
import streamlit as st

from egame179_frontend.api.states import PlayerState


def stocks() -> None:
    """Stocks game view."""
    st.markdown("## Система корпоративного управления CP/20.22")
    st.title("NoName Corporation")
    st.markdown("### Биржевые котировки")
    state: PlayerState = st.session_state.player_state

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(
            "<p style='text-align: center;'> Выгрузка с биржи </p>",
            unsafe_allow_html=True,
        )
        st.dataframe(state.stocks.pivot(index="cycle", columns="ticket", values="price"))
    with col2:
        st.markdown(
            "<p style='text-align: center;'> График котировок акций </p>",
            unsafe_allow_html=True,
        )
        st.altair_chart(_stocks_chart(state.stocks, cycle=3, width=500, height=450))


def _stocks_chart(df: pd.DataFrame, cycle: int, width: int, height: int) -> alt.Chart:  # noqa: WPS210
    chart = alt.Chart(df)
    alt_x = alt.X("cycle:Q", scale=alt.Scale(domain=(0, cycle + 0.1)))
    alt_y = alt.Y(
        "price:Q",
        scale=alt.Scale(domain=(0, df["price"].max() + 0.1)),
    )

    alt_line = chart.mark_line(point=True)  # type: ignore
    alt_line = alt_line.encode(x=alt_x, y=alt_y, color="ticket:N", strokeDash="ticket")

    nearest = alt.selection(
        type="single",  # type: ignore
        nearest=True,
        on="mouseover",
        fields=["cycle"],
        empty="none",
    )
    selectors = chart.mark_point().encode(x="cycle:Q", opacity=alt.value(0))
    selectors = selectors.add_selection(nearest)

    points = alt_line.mark_point().encode(
        opacity=alt.condition(
            predicate=nearest,
            if_true=alt.value(1),
            if_false=alt.value(0),
        ),
    )

    text = alt_line.mark_text(align="left", dx=5, dy=-5)
    text = text.encode(text=alt.condition(nearest, "price:Q", alt.value(" ")))

    rules = chart.mark_rule(color="gray").encode(x="cycle:Q").transform_filter(nearest)  # type: ignore
    layer = alt.layer(alt_line, selectors, points, rules, text)
    return layer.properties(width=width, height=height).interactive()
