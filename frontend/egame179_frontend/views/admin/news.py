from streamlit.components import v1 as components

html_code = """
    <marquee behavior="scroll" direction="up" scrollamount="20" height="1000" width="500">
        <p> Here is some scrolling text... going up! </p>
        <p> Here is BREAKING NEWS! </p>
    </marquee>
"""

components.html(html_code, height=1000)
