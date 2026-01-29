class Task:
    def __init__(self, task_id, priority, capability):
        self.task_id = task_id
        self.priority = priority
        self.capability = capability
        self.assigned_agent = None
        self.status = "Pending"
        self.progress = 0
        self.age = 0
        self.waiting_time = 0
    
    def __repr__(self):
        return f"Task({self.task_id}, priority={self.priority}, capability={self.capability})"