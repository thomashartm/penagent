import os
import json
from datetime import datetime, timezone
from src.agent.langgraph_agent import LangGraphAgent
from src.agent.ollama_llm import OllamaLLM
from src.tools.python_repl_tool import PythonREPLTool
from src.tools.web_browser_tool import WebBrowserTool
from src.tools.web_search_tool import WebSearchTool
from src.tools.rag_tool import RAGTool
from src.tools.kali_container_tool import KaliContainerTool

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def log_event(f, event_type, content):
    event = {'type': event_type, 'content': content, 'timestamp': utc_now()}
    f.write(json.dumps(event) + '\n')
    f.flush()

def run_agent_job(user_input, output_dir, session_id):
    os.makedirs(output_dir, exist_ok=True)
    event_log_path = os.path.join(output_dir, 'events.jsonl')
    tools = [
        PythonREPLTool(),
        WebBrowserTool(output_dir=output_dir),
        WebSearchTool(),
        RAGTool(),
        KaliContainerTool()
    ]
    llm = OllamaLLM()
    agent = LangGraphAgent(tools=tools, llm=llm, output_dir=output_dir)
    try:
        with open(event_log_path, 'a') as f:
            log_event(f, 'USER', user_input)
            log_event(f, 'STARTED', f'Agent job started for session {session_id}')
            for event in agent.run(user_input):
                log_event(f, event.get('type', 'UNKNOWN'), event.get('content'))
            log_event(f, 'DONE', 'Agent job finished')
    except Exception as e:
        with open(event_log_path, 'a') as f:
            log_event(f, 'ERROR', f'Agent error: {str(e)}') 