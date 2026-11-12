import streamlit as st

from widget import choice

st.title("Widget demo")

grain = choice(["Daily", "Weekly", "Monthly"], label="Grain", value=st.session_state.get("grain_pick"), key="grain")
if grain:
    st.session_state["grain_pick"] = grain
st.markdown(f"Picked: {grain or 'nothing yet'}")
