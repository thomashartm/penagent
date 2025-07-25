class ShortTermMemory:
    """Short-term memory for storing actions and results within a session."""
    def __init__(self):
        self.history = []
    def add(self, event):
        """Add an event (thought, action, observation) to memory."""
        self.history.append(event)
    def get_history(self):
        """Return the session history."""
        return self.history 