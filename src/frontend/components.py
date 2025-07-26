import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd

def render_toolbar(tools):
    st.markdown("---", unsafe_allow_html=True)
    cols = st.columns(len(tools))
    for i, (tool, online) in enumerate(tools.items()):
        color = '#52c41a' if online else '#f5222d'
        cols[i].markdown(f"<div style='display:flex;align-items:center;font-size:13px;'><div style='width:10px;height:10px;background:{color};border-radius:50%;margin-right:4px;'></div>{tool}</div>", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

def render_chat(chat_history, agent_running):
    st.markdown("## 💬 Pentest-Agent Chat", unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in chat_history:
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                st.chat_message("assistant").write(msg['content'])
        # Only show 'Agent is thinking...' if agent_running is True and the last message is from the user
        if agent_running and (not chat_history or chat_history[-1]['role'] == 'user'):
            st.chat_message("assistant").write("🧠 Agent is thinking...")

def render_thinking(agent_running):
    if agent_running:
        st.info("Agent is working on your request...")

def render_status(agent_running, last_event):
    if agent_running:
        if last_event:
            st.info(f"Agent status: {last_event['type']} — {last_event['content']}")
        else:
            st.info("Agent status: Working...")
    else:
        st.success("Agent status: Idle")

def render_vuln_table(vulns_df):
    st.markdown("### Findings / Vulnerabilities")
    if hasattr(vulns_df, 'empty') and vulns_df.empty:
        st.info("No vulnerabilities found yet.")
        return
    if not hasattr(vulns_df, 'empty') and not vulns_df:
        st.info("No vulnerabilities found yet.")
        return
    gb = GridOptionsBuilder.from_dataframe(vulns_df)
    gb.configure_pagination()
    gb.configure_default_column(editable=False, groupable=True)
    gridOptions = gb.build()
    AgGrid(vulns_df, gridOptions=gridOptions, height=250, fit_columns_on_grid_load=True) 