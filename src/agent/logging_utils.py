import json
from datetime import datetime
import os

LOG_FILE = 'process_logs.json'
DEBUG_LOG_FILE = 'agent_debug.log'

def set_log_paths(log_file, debug_log_file):
    global LOG_FILE, DEBUG_LOG_FILE
    LOG_FILE = log_file
    DEBUG_LOG_FILE = debug_log_file

def log_event(event_type, content):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': event_type,
        'content': content
    }
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        log_debug(f"[LOGGING ERROR] {e}")
    log_debug(f"{event_type}: {content}")

def log_thought(thought):
    log_event('Thought', thought)

def log_action(action):
    log_event('Action', action)

def log_observation(observation):
    log_event('Observation', observation)

def log_debug(message):
    try:
        with open(DEBUG_LOG_FILE, 'a') as f:
            f.write(f"{datetime.utcnow().isoformat()} {message}\n")
    except Exception as e:
        print(f"[DEBUG LOGGING ERROR] {e}") 