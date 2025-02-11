from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

stations = {i: None for i in range(1, 9)}
active_status = {i: False for i in range(1, 9)}
team_queue = []
timer_start = {}

@app.route('/')
def index():
    current_time = time.time()
    # Calculate remaining time for each station
    remaining_times = {s: max(300 - int(current_time - t), 0) if t else None for s, t in timer_start.items()}
    return render_template('index.html', stations=stations, active_status=active_status, team_queue=team_queue, remaining_times=remaining_times)

@app.route('/assign', methods=['POST'])
def assign_team():
    data = request.json
    team_name = data.get('team')

    # Check if team is already assigned or in queue
    if team_name in stations.values() or team_name in team_queue:
        return jsonify({'success': False})

    # Assign the team to the highest active station
    available_stations = [s for s in sorted(active_status.keys(), reverse=True) if active_status[s] and stations[s] is None]
    if available_stations:
        station = available_stations[0]
        stations[station] = team_name
        timer_start[station] = time.time()
    else:
        team_queue.append(team_name)

    return jsonify({'success': True})

@app.route('/remove', methods=['POST'])
def remove_team():
    data = request.json
    team_name = data.get('team')

    # Remove team from a station if assigned
    for station, team in stations.items():
        if team == team_name:
            stations[station] = None
            timer_start.pop(station, None)
            assign_next_team()
            return jsonify({'success': True})

    # If team is in queue, remove from queue
    if team_name in team_queue:
        team_queue.remove(team_name)
        return jsonify({'success': True})

    return jsonify({'success': False})

@app.route('/toggle_active', methods=['POST'])
def toggle_active():
    data = request.json
    station = data.get('station')

    if station not in active_status:
        return jsonify({'success': False})

    active_status[station] = not active_status[station]
    if active_status[station]:
        assign_next_team()
    else:
        if stations[station]:
            stations[station] = None
            timer_start.pop(station, None)
            assign_next_team()

    return jsonify({'success': True})

@app.route('/assignments')
def assignments():
    """Render the assignments page."""
    return render_template('assignments.html', team_queue=team_queue, stations=stations)


@app.route('/get_assignments')
def get_assignments():
    """Return the latest station assignments as JSON."""
    return jsonify({'stations': stations, 'active_status': active_status, 'team_queue': team_queue})


def assign_next_team():
    """Assign the next team from the queue if a station is available."""
    if team_queue:
        available_stations = [s for s in sorted(active_status.keys(), reverse=True) if active_status[s] and stations[s] is None]
        if available_stations:
            station = available_stations[0]
            team_name = team_queue.pop(0)
            stations[station] = team_name
            timer_start[station] = time.time()

if __name__ == '__main__':
    app.run(debug=True)
