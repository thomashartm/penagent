import streamlit as st
import os
import time
import json
import pandas as pd
import threading
from src.agent.agent_service import run_agent_job
from src.frontend.components import render_toolbar, render_chat, render_thinking, render_vuln_table, render_status

st.set_page_config(page_title="Pentest-Agent", layout="wide")

# --- Autorefresh capability check ---
HAS_AUTOREFRESH = hasattr(st, "autorefresh") or hasattr(st, "experimental_autorefresh")

# --- Small Tools Bar ---
tools = {
    "ShellTool": True,
    "PythonREPLTool": True,
    "WebBrowserTool": True,
    "WebSearchTool": True,
    "RAGTool": True,
            "KaliContainerTool": os.system("docker ps | grep mcp-kali > /dev/null") == 0,
    "Playwright": os.system("docker ps | grep pentest-playwright > /dev/null") == 0,
            "ZAP": os.system("docker ps | grep mcp-zap > /dev/null") == 0,
}
render_toolbar(tools)

# --- Chat State ---
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(int(time.time()))
if 'output_dir' not in st.session_state:
    st.session_state['output_dir'] = os.path.join('outputs', st.session_state['session_id'])
    os.makedirs(st.session_state['output_dir'], exist_ok=True)
if 'agent_running' not in st.session_state:
    st.session_state['agent_running'] = False
if 'last_user_input' not in st.session_state:
    st.session_state['last_user_input'] = None
if 'agent_thread' not in st.session_state:
    st.session_state['agent_thread'] = None
if 'last_agent_event' not in st.session_state:
    st.session_state['last_agent_event'] = None
if 'last_event_idx' not in st.session_state:
    st.session_state['last_event_idx'] = 0
if 'agent_start_time' not in st.session_state:
    st.session_state['agent_start_time'] = None

# --- Chat UI ---
render_chat(st.session_state['chat_history'], st.session_state['agent_running'])

# --- Agent Execution (Background Thread) ---
def agent_worker(user_input, output_dir, session_id):
    run_agent_job(user_input, output_dir, session_id)
    st.session_state['agent_running'] = False

# --- Main chat interaction logic ---
user_input = st.chat_input("Type your pentest goal, question, or follow-up and press Enter...")
if user_input:
    st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
    st.session_state['last_user_input'] = user_input
    st.session_state['agent_running'] = True
    st.session_state['last_agent_event'] = None
    st.session_state['agent_start_time'] = time.time()
    # Do NOT increment last_event_idx here
    # Start agent in background thread
    thread = threading.Thread(target=agent_worker, args=(user_input, st.session_state['output_dir'], st.session_state['session_id']))
    thread.start()
    st.session_state['agent_thread'] = thread
    # Force a rerun so UI updates immediately
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

# --- Poll for new agent events and update chat ---
event_log_path = os.path.join(st.session_state['output_dir'], 'events.jsonl')
status_message = None
if os.path.exists(event_log_path):
    if hasattr(st, 'autorefresh'):
        st.autorefresh(interval=1000, key="autorefresh")  # Poll every 1s
    elif hasattr(st, 'experimental_autorefresh'):
        st.experimental_autorefresh(interval=1000, key="autorefresh")
    # Read new events from the event log
    with open(event_log_path, 'r') as f:
        lines = f.readlines()
    new_events = lines[st.session_state['last_event_idx']:]
    for line in new_events:
        try:
            event = json.loads(line)
            t = event.get('type')
            c = event.get('content')
            if t == 'USER':
                if not st.session_state['chat_history'] or st.session_state['chat_history'][-1] != {'role': 'user', 'content': c}:
                    st.session_state['chat_history'].append({'role': 'user', 'content': c})
            elif t == 'STARTED':
                status_message = f"🤖 {c}"
            elif t == 'DONE':
                st.session_state['agent_running'] = False
                status_message = f"✅ {c}"
                # Force a rerun to process new events and update UI
                if hasattr(st, 'rerun'):
                    st.rerun()
                elif hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()
                break
            elif t == 'ERROR':
                st.session_state['agent_running'] = False
                status_message = f"❌ {c}"
                # Force a rerun to process new events and update UI
                if hasattr(st, 'rerun'):
                    st.rerun()
                elif hasattr(st, 'experimental_rerun'):
                    st.experimental_rerun()
                break
            elif t == 'PirateChat':
                msg = {'role': 'assistant', 'content': f"☠️ {c}"}
                if not st.session_state['chat_history'] or st.session_state['chat_history'][-1] != msg:
                    st.session_state['chat_history'].append(msg)
            elif t == 'Thought':
                msg = {'role': 'assistant', 'content': f"🧠 {c}"}
                if not st.session_state['chat_history'] or st.session_state['chat_history'][-1] != msg:
                    st.session_state['chat_history'].append(msg)
            elif t == 'Action':
                msg = {'role': 'assistant', 'content': f"⚡ {c}"}
                if not st.session_state['chat_history'] or st.session_state['chat_history'][-1] != msg:
                    st.session_state['chat_history'].append(msg)
            elif t == 'Observation':
                msg = {'role': 'assistant', 'content': f"🔎 {c}"}
                if not st.session_state['chat_history'] or st.session_state['chat_history'][-1] != msg:
                    st.session_state['chat_history'].append(msg)
            st.session_state['last_agent_event'] = event
        except Exception:
            continue
    st.session_state['last_event_idx'] += len(new_events)
    render_status(st.session_state['agent_running'], {'type': status_message, 'content': status_message} if status_message else st.session_state['last_agent_event'])
    # If agent is stuck for >60s, show an error
    if st.session_state['agent_running'] and st.session_state['agent_start_time'] and (time.time() - st.session_state['agent_start_time'] > 60):
        st.error("Agent appears to be stuck. Please try again or check the logs.")

# # --- Vulnerability Table ---
# st.markdown("---")
# log_path = os.path.join(st.session_state['output_dir'], 'process_logs.json')
# vulns_df = pd.DataFrame()
# if os.path.exists(log_path):
#     def load_vulns(log_path):
#         vulns = []
#         with open(log_path) as f:
#             for line in f:
#                 try:
#                     entry = json.loads(line)
#                     if entry.get('type') == 'Observation' and isinstance(entry.get('content'), dict):
#                         c = entry['content']
#                         if any(k in str(c).lower() for k in ['vuln', 'xss', 'sql', 'idor', 'cve', 'leak', 'exposure']):
#                             vulns.append({
#                                 'ID': len(vulns)+1,
#                                 'Description': str(c),
#                                 'Severity': 'TBD',
#                                 'Location': c.get('url', 'N/A'),
#                                 'Details': c
#                             })
#                 except Exception:
#                     continue
#         return pd.DataFrame(vulns)
#     vulns_df = load_vulns(log_path)
# render_vuln_table(vulns_df) 