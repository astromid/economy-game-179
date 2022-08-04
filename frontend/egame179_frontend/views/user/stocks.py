import altair as alt
import pandas as pd
import streamlit as st


def stocks() -> None:
    """Stocks game view."""
    st.markdown("### Биржевые котировки")
    stocks_df = pd.DataFrame([record.dict() for record in st.session_state.game_state.stocks])
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(
            "<p style='text-align: center;'> Выгрузка с биржи </p>",
            unsafe_allow_html=True,
        )
        st.dataframe(stocks_df.pivot(index="cycle", columns="ticket", values="price"))
    with col2:
        st.markdown(
            "<p style='text-align: center;'> График котировок акций </p>",
            unsafe_allow_html=True,
        )
        st.altair_chart(_stocks_chart(stocks_df, cycle=st.session_state.game_state.cycle, width=500, height=450))


def _stocks_chart(df: pd.DataFrame, cycle: int, width: int, height: int) -> alt.Chart:  # noqa: WPS210
    chart = alt.Chart(df)
    alt_x = alt.X("cycle:Q", scale=alt.Scale(domain=(0, cycle + 0.05)))
    alt_y = alt.Y(
        "price:Q",
        scale=alt.Scale(domain=(0, df["price"].max() + 0.05)),
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
