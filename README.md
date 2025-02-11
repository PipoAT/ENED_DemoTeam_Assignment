
# Team Station Assignment Application

This web application allows the dynamic assignment of teams to stations, managing a queue for teams waiting for available stations, and providing real-time updates for both team assignments and the queue.

## Features
- **Assign Teams to Stations**: Teams can be assigned to the highest available active station.
- **Queue Management**: Teams can be added to the queue when no stations are available.
- **Auto-remove**: Teams are automatically removed from stations after 5 minutes unless manually removed.
- **Real-time Updates**: The current team assignments and queue are updated in real-time every 5 seconds without requiring a page refresh.

## Requirements
To run this application, you need the following:
- Python 3.7 or higher
- Flask
- Additional Python libraries (`threading`, `time`)

## Installation and Setup

### Step 1: Clone the repository
Clone the repository to your local machine using Git:
```bash
git clone https://github.com/yourusername/team-station-assignment.git
cd team-station-assignment
```

### Step 2: Install dependencies
It’s recommended to use a virtual environment to avoid conflicts with other projects.

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install required dependencies**:
   ```bash
   pip install flask
   ```

### Step 3: Run the Application
To start the application, run the following command:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/` by default.

### Step 4: Access the Pages
- **Main page** (`/`): The home page where you can assign teams to stations and manage station statuses.
- **Assignments page** (`/assignments`): A separate page displaying the current station assignments and team queue. This page updates in real-time every 5 seconds.

### Real-time Updates
The `assignments` page uses **AJAX polling** to fetch the latest team assignments and queue every 5 seconds without requiring a page refresh. This ensures that all users see the most up-to-date data without needing to reload the page manually.

### API Endpoints

- **`/assign`**: Assign a team to the highest available active station. The team is added to the queue if no stations are available.
  - **Method**: `POST`
  - **Body**: JSON with the team name.
  - **Example Request**:
    ```json
    {
      "team": "Team A"
    }
    ```

- **`/remove`**: Remove a team from a station or queue.
  - **Method**: `POST`
  - **Body**: JSON with the team name.
  - **Example Request**:
    ```json
    {
      "team": "Team A"
    }
    ```

- **`/toggle_active`**: Toggle the active status of a station (activate or deactivate).
  - **Method**: `POST`
  - **Body**: JSON with the station number.
  - **Example Request**:
    ```json
    {
      "station": 1
    }
    ```

- **`/get_assignments`**: Retrieve the current team assignments and the team queue as JSON.
  - **Method**: `GET`
  - **Example Response**:
    ```json
    {
      "stations": {
        "1": "Team A",
        "2": null,
        "3": "Team B"
      },
      "active_status": {
        "1": true,
        "2": false,
        "3": true
      },
      "team_queue": ["Team C", "Team D"]
    }
    ```

## Deployment

To deploy this app to a cloud platform (e.g., **Vercel**, **Heroku**), follow these steps:

### Vercel
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Link your project:
   ```bash
   vercel
   ```

3. Follow the prompts to deploy.

4. After deployment, the app will be available at the URL provided by Vercel.

### Heroku
1. Install Heroku CLI:
   ```bash
   brew install heroku
   ```

2. Create a `Procfile` with the following content:
   ```
   web: python app.py
   ```

3. Log in to Heroku and create a new app:
   ```bash
   heroku login
   heroku create
   ```

4. Deploy your app to Heroku:
   ```bash
   git push heroku master
   ```

5. Open the deployed app:
   ```bash
   heroku open
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Any Questions?
Andrew T. Pipo

937-631-5036

atpipo2026@gmail.com

pipoat@mail.uc.edu

---

This README provides all necessary information to run, test, and deploy the application. For any issues or contributions, feel free to submit an issue or pull request.
