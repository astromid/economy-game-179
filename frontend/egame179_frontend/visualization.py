import altair as alt
import networkx as nx
import pandas as pd
import pyecharts
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode

from egame179_frontend.style import ThemeColors

Y_MAX_SCALE = 1.05
MAX_THETA = 0.48
NODE_SIZE_PX = 30
TOOLTIP_JS = "".join(
    [
        "function(params){",
        "var bulletItem = (field, value) => ",
        "'<p>' + params.marker + ' ' + field + ' ' + '<b>' + value + '</b></p>';",
        "let tip = bulletItem('Цена производства', params.data.buy);",
        "tip += bulletItem('Цена продажи', params.data.sell);",
        "tip += bulletItem('Фактор спроса', params.data.demand_factor);",
        "tip += bulletItem('Владелец', params.data.top1);",
        "tip += bulletItem('Конкурент', params.data.top2);",
        "return tip;}",
    ],
)


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
        thetas (dict[str, float]): player's thetas state.

    Returns:
        pyecharts.charts.Radar: radar chart for rendering.
    """
    radar = pyecharts.charts.Radar()
    indicators = [opts.RadarIndicatorItem(name=market, max_=MAX_THETA) for market in thetas]
    radar.add_schema(schema=indicators)
    radar.add("", data=[{"name": "Эффективность", "value": list(thetas.values())}])
    return radar


def markets_graph(nx_graph: nx.Graph, unlocked_markets: list[int]) -> pyecharts.charts.Graph:
    """Graph chart for markets visualization.

    Args:
        nx_graph (nx.Graph): markets graph with additional info.
        unlocked_markets (list[int]): unlocked markets for player.

    Returns:
        pyecharts.charts.Graph: graph chart for rendering.
    """
    nodes = [
        {
            "name": node["name"],
            "buy": node["buy"],
            "sell": node["sell"],
            "demand_factor": node["demand_factor"],
            "top1": node["top1"],
            "top2": node["top2"],
            "symbol": "circle",
            "symbolSize": NODE_SIZE_PX * node["demand_factor"],
            "itemStyle": {"color": get_graph_node_color(node_id, unlocked_markets)},
        }
        for node_id, node in nx_graph.nodes(data=True)
    ]
    links = [
        {
            "source": nx_graph.nodes[source]["name"],
            "target": nx_graph.nodes[target]["name"],
            # TODO: change edges color
            "lineStyle": {"color": ThemeColors.GRAY.value},
        }
        for source, target in nx_graph.edges
    ]
    graph = pyecharts.charts.Graph()
    graph.add(
        "Markets",
        repulsion=2000,
        edge_length=100,
        # gravity=1e6,
        edge_symbol=["arrow", "arrow"],
        edge_symbol_size=8,
        label_opts=opts.LabelOpts(position="inside"),
        tooltip_opts=opts.TooltipOpts(formatter=JsCode(TOOLTIP_JS), border_width=1),
        nodes=nodes,
        links=links,
        linestyle_opts=opts.LineStyleOpts(width=2, opacity=0.9, curve=0.2),
    )
    return graph


def get_graph_node_color(market_id: int, unlocked_markets: list[int]) -> str:
    """Get color of market node in graph.

    Args:
        market_id (int): current market id
        unlocked_markets (list[int]): list of unlocked market ids.

    Returns:
        str: node color.
    """
    if market_id == unlocked_markets[-1]:
        color = ThemeColors.BLUE.value  # home market
    elif market_id in unlocked_markets:
        color = ThemeColors.GREEN.value  # unlocked markets
    else:
        color = ThemeColors.GRAY.value
    return color
