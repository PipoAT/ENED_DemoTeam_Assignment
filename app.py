from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import json
import os
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# File-based persistence to support multiple instances
STATE_FILE = 'app_state.json'
state_lock = threading.Lock()

def load_state():
    """Load state from file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading state: {e}")
    return {
        'stations': {str(i): None for i in range(1, 13)},
        'active_status': {str(i): False for i in range(1, 13)},
        'team_queue': [],
        'timer_start': {}
    }

def save_state(state):
    """Save state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_state():
    """Thread-safe state retrieval."""
    with state_lock:
        return load_state()

def update_state(update_func):
    """Thread-safe state update with a function."""
    with state_lock:
        state = load_state()
        update_func(state)
        save_state(state)
        return state

# Note: These were used in the old in-memory version but are no longer needed
# All state is now managed through file persistence

@app.route('/')
def index():
    state = get_state()
    stations = {int(k): v for k, v in state['stations'].items()}
    active_status = {int(k): v for k, v in state['active_status'].items()}
    team_queue = state['team_queue']
    timer_start = {int(k): v for k, v in state['timer_start'].items()}
    
    current_time = time.time()
    # Calculate remaining time for each station
    remaining_times = {s: max(300 - int(current_time - t), 0) if t else None for s, t in timer_start.items()}
    return render_template('index.html', stations=stations, active_status=active_status, team_queue=team_queue, remaining_times=remaining_times)

@app.route('/assign', methods=['POST'])
def assign_team():
    data = request.json
    team_name = data.get('team')
    
    # Input validation
    if not team_name or not isinstance(team_name, str) or len(team_name) > 50:
        return jsonify({'success': False, 'error': 'Invalid team name'})
    
    def do_assign(state):
        stations = state['stations']
        active_status = state['active_status']
        team_queue = state['team_queue']
        timer_start = state['timer_start']
        
        # Check if team is already assigned or in queue
        if team_name in stations.values() or team_name in team_queue:
            return False
        
        # Assign the team to the highest active station
        available_stations = [s for s in sorted(active_status.keys(), key=lambda x: int(x), reverse=True) 
                            if active_status[s] and stations[s] is None]
        if available_stations:
            station = available_stations[0]
            stations[station] = team_name
            timer_start[station] = time.time()
        else:
            team_queue.append(team_name)
        
        return True
    
    state = update_state(do_assign)
    
    # Emit update to all connected clients
    socketio.emit('update_assignments', {
        'stations': state['stations'],
        'active_status': state['active_status'],
        'team_queue': state['team_queue']
    }, namespace='/')
    
    return jsonify({'success': True})

@app.route('/remove', methods=['POST'])
def remove_team():
    data = request.json
    team_name = data.get('team')
    
    # Input validation
    if not team_name or not isinstance(team_name, str):
        return jsonify({'success': False, 'error': 'Invalid team name'})
    
    success = False
    
    def do_remove(state):
        nonlocal success
        stations = state['stations']
        timer_start = state['timer_start']
        team_queue = state['team_queue']
        
        # Remove team from a station if assigned
        for station, team in stations.items():
            if team == team_name:
                stations[station] = None
                timer_start.pop(station, None)
                assign_next_team_internal(state)
                success = True
                return
        
        # If team is in queue, remove from queue
        if team_name in team_queue:
            team_queue.remove(team_name)
            success = True
    
    state = update_state(do_remove)
    
    # Emit update to all connected clients
    socketio.emit('update_assignments', {
        'stations': state['stations'],
        'active_status': state['active_status'],
        'team_queue': state['team_queue']
    }, namespace='/')
    
    return jsonify({'success': success})

@app.route('/toggle_active', methods=['POST'])
def toggle_active():
    data = request.json
    station = data.get('station')
    
    # Input validation
    if not isinstance(station, int) or station < 1 or station > 12:
        return jsonify({'success': False, 'error': 'Invalid station number'})
    
    station = str(station)
    
    def do_toggle(state):
        stations = state['stations']
        active_status = state['active_status']
        timer_start = state['timer_start']
        
        if station not in active_status:
            return False
        
        active_status[station] = not active_status[station]
        if active_status[station]:
            assign_next_team_internal(state)
        else:
            if stations[station]:
                stations[station] = None
                timer_start.pop(station, None)
                assign_next_team_internal(state)
        
        return True
    
    state = update_state(do_toggle)
    
    # Emit update to all connected clients
    socketio.emit('update_assignments', {
        'stations': state['stations'],
        'active_status': state['active_status'],
        'team_queue': state['team_queue']
    }, namespace='/')
    
    return jsonify({'success': True})

@app.route('/assignments')
def assignments():
    """Render the assignments page."""
    state = get_state()
    team_queue = state['team_queue']
    stations = {int(k): v for k, v in state['stations'].items()}
    return render_template('assignments.html', team_queue=team_queue, stations=stations)

@app.route('/station')
def station():
    """Render the station page."""
    state = get_state()
    team_queue = state['team_queue']
    stations = {int(k): v for k, v in state['stations'].items()}
    return render_template('station.html', team_queue=team_queue, stations=stations)


@app.route('/get_assignments')
def get_assignments():
    """Return the latest station assignments as JSON."""
    state = get_state()
    return jsonify({
        'stations': state['stations'],
        'active_status': state['active_status'],
        'team_queue': state['team_queue']
    })


def assign_next_team_internal(state):
    """Assign the next team from the queue if a station is available (internal state version)."""
    stations = state['stations']
    active_status = state['active_status']
    team_queue = state['team_queue']
    timer_start = state['timer_start']
    
    if team_queue:
        available_stations = [s for s in sorted(active_status.keys(), key=lambda x: int(x), reverse=True) 
                            if active_status[s] and stations[s] is None]
        if available_stations:
            station = available_stations[0]
            team_name = team_queue.pop(0)
            stations[station] = team_name
            timer_start[station] = time.time()


def assign_next_team():
    """Assign the next team from the queue if a station is available."""
    state = update_state(assign_next_team_internal)
    
    # Emit update to all connected clients
    socketio.emit('update_assignments', {
        'stations': state['stations'],
        'active_status': state['active_status'],
        'team_queue': state['team_queue']
    }, namespace='/')

if __name__ == '__main__':
    # Note: allow_unsafe_werkzeug is only for development/testing
    # Do not use in production - use a proper WSGI server like gunicorn
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
