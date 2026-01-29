import os
import json
import random
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from secrets import token_urlsafe

# Custom Module Imports (Ensure these files exist in your folder)
from task_model import Task
from agent import Agent
from scheduler import AutonomousScheduler

app = Flask(__name__)
app.secret_key = token_urlsafe(32)

# --- Flask-Login & Persistence Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

USER_DB = 'users.json'

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, 'r') as f:
        data = json.load(f)
        return {uid: User(uid, u['username'], u['pw_hash']) for uid, u in data.items()}

def save_users(user_dict):
    data = {uid: {'username': u.username, 'pw_hash': u.password_hash} for uid, u in user_dict.items()}
    with open(USER_DB, 'w') as f:
        json.dump(data, f)

users = load_users()

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# --- System State ---
class SystemState:
    def __init__(self):
        self.agents = [
            Agent("Alpha-01", ["Python", "Security"], 0.05),
            Agent("Beta-02", ["Data Analysis", "Python"], 0.12),
            Agent("Gamma-03", ["Security"], 0.02)
        ]
        self.tasks = []
        self.scheduler = AutonomousScheduler()
        self.logs = []
        self.cycle_count = 0

    def get_efficiency(self):
        total_success = sum(a.completed_tasks_count for a in self.agents)
        total_failures = sum(a.failure_count for a in self.agents)
        total_attempts = total_success + total_failures
        if total_attempts == 0:
            return 100
        return round((total_success / total_attempts) * 100, 1)

state = SystemState()

# --- Auth Routes ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if any(u.username == username for u in users.values()):
            flash("Username already exists.", "danger")
        else:
            u_id = str(len(users) + 1)
            new_user = User(u_id, username, generate_password_hash(password))
            users[u_id] = new_user
            save_users(users)
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = next((u for u in users.values() if u.username == username), None)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Simulation Routes ---

@app.route('/')
def index():
    efficiency = state.get_efficiency()
    return render_template('index.html', 
                           tasks=state.tasks, 
                           agents=state.agents, 
                           logs=state.logs, 
                           cycle=state.cycle_count,
                           efficiency=efficiency)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', tasks=state.tasks)

@app.route('/step')
def step():
    state.cycle_count += 1
    if random.random() < 0.4:
        new_id = f"T-{random.randint(1000, 9999)}"
        state.tasks.append(Task(new_id, random.randint(1, 5), random.choice(["Python", "Security", "Data Analysis"])))

    state.logs.extend(state.scheduler.assign_tasks(state.tasks, state.agents))
    
    pre_complete = [t.task_id for t in state.tasks if t.status == "Completed"]
    state.scheduler.complete_all_tasks(state.tasks, state.agents)
    post_complete = [t for t in state.tasks if t.status == "Completed" and t.task_id not in pre_complete]
    
    for t in post_complete:
        state.logs.append(f"🏆 SUCCESS: {t.assigned_agent} finished Task {t.task_id}!")
    return redirect(url_for('index'))

@app.route('/add_agent', methods=['POST'])
@login_required
def add_agent():
    name = request.form.get('agent_name')
    # Get multiple capabilities from checkboxes
    skills = request.form.getlist('capabilities')
    failure_input = request.form.get('failure_rate', 0) 
    risk = float(failure_input) / 100

    if name and skills:
        new_agent = Agent(name, skills, risk)
        state.agents.append(new_agent)
        state.logs.append(f"👨‍🚀 NEW HIRE ({current_user.username}): Agent {name} joined the fleet.")
        flash(f"Agent {name} recruited successfully!", "success")
    
    return redirect(url_for('admin'))

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    t_id = request.form.get('task_id')
    prio = int(request.form.get('priority'))
    cap = request.form.get('capability')
    state.tasks.append(Task(t_id, prio, cap))
    state.logs.append(f"🛠️ ADMIN ({current_user.username}): Task {t_id} injected.")
    return redirect(url_for('admin'))

@app.route('/remove_agent', methods=['POST'])
@login_required
def remove_agent():
    name = request.form.get('agent_name')
    # Filter the list to remove the specific agent
    state.agents = [a for a in state.agents if a.agent_id != name]
    state.logs.append(f"⚠️ DECOMMISSIONED ({current_user.username}): Agent {name} removed.")
    flash(f"Agent {name} has been taken offline.", "warning")
    return redirect(url_for('admin'))

@app.route('/clear_completed')
@login_required
def clear_completed():
    state.tasks = [t for t in state.tasks if t.status != "Completed"]
    state.logs.append("🧹 Queue cleaned.")
    return redirect(url_for('admin'))

@app.route('/reset')
@login_required
def reset():
    global state
    state = SystemState()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)