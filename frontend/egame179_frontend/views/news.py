import streamlit as st
from streamlit.components import v1 as components

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import NewsState
from egame179_frontend.views.registry import AppView, appview

MARQUEE_TEMPLATE = """
    <marquee behavior="scroll" direction="up" scrollamount="3" height="800" width="800">
        {bulletins}
    </marquee>
"""


@appview
class BulletinsView(AppView):
    """Bulletins AppView."""

    idx = 9
    name = "Сводки новостей"
    icon = "graph-up"
    roles = (UserRoles.NEWS.value,)

    def render(self) -> None:
        """Render view."""
        state: NewsState = st.session_state.game
        st.markdown(f"#### Биржевые сводки (Цикл {state.cycle.id})")

        html = MARQUEE_TEMPLATE.format(
            bulletins="".join(
                [
                    f"<p><font size=10> [{bulletin['ts']}] {bulletin['text']} </font></p>"
                    for bulletin in state.bulletins
                ],
            ),
        )
        components.html(html, height=800)
