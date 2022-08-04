import networkx as nx
import numpy as np
import pyecharts as pe
import streamlit as st

TOOLTIP_JS_CODE = "".join(
    [
        "function(params){",
        "var bulletItem = (field, value) => ",
        "'<p>' + params.marker + ' ' + field + ' ' + '<b>' + value + '</b></p>';",
        "let tip = bulletItem('Цена производства', params.data.buy_price);",
        "tip += bulletItem('Цена продажи', params.data.sale_price);",
        "tip += bulletItem('Позиция', params.data.position);",
        "return tip;",
        "}",
    ],
)


def markets() -> None:
    st.markdown("## Граф рынков")

    with st.expander("Статус отдельных рынков"):
        st.text("TBD")


def make_markets_graph() -> pe.charts.Graph:
    pass


def get_node_size_px(demand: float, start_demand: float) -> float:
    return 30 * (np.log10(demand / start_demand) + 1)
