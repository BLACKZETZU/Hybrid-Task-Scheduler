class Agent:
    def __init__(self, agent_id, capabilities, failure_probability=0.1):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.failure_probability = failure_probability
        self.available = True
        self.completed_tasks_count = 0
        self.failure_count = 0
