Autonomous Agent Orchestrator
The Autonomous Agent Orchestrator is a full-stack simulation tool that demonstrates how tasks can be automatically assigned to a fleet of specialized AI agents. It uses an intelligent matching algorithm to ensure that tasks—ranging from Python development to security audits—are handled by the most qualified and available resources.

 How It Works
The system runs on a "cycle" basis. In each cycle:

Task Discovery: The system identifies pending tasks in the queue.

Skill Matching: The scheduler scores available agents based on their specific capabilities and the task's priority.

Execution: Agents work on tasks, with their progress and success/failure rates tracked in real-time.

Monitoring: All actions are logged to a live terminal and visualized through a dashboard.

 Key Features
Dual-Dashboard System: A public Monitor to watch the fleet work and a private Admin Portal to control the simulation.

Dynamic Workforce: Admins can recruit new agents with custom skills or decommission underperforming ones on the fly.

Persistent Accounts: A secure login system that remembers admin credentials even if the server is turned off.

Real-Time Analytics: Live tracking of fleet efficiency and individual agent performance.

Responsive UI: Support for both Light and Dark modes using native Bootstrap styling.

 Technical Core
Backend: Python & Flask

Logic: Object-Oriented Task & Agent Modeling

Security: Flask-Login with Password Hashing

Frontend: Bootstrap 5.3 & JavaScript
