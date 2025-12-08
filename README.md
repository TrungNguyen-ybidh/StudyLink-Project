# 📚 StudyLink - Smart Study Planning System

**Team Name:** OurSQL  
**Product/Project Name:** StudyLink

**Team Members:**
- Trung Nguyen
- Tam Vu
- Bennett Franciosi
- Alastaire Balin
- Alex Zou

---

**StudyLink** is a data-driven study planning and management system designed to optimize student academic performance by integrating calendar data, sleep patterns, class workload, and academic metrics. The system provides role-based access for students, advisors, data analysts, and system administrators.

## Project Overview

StudyLink helps students manage their academic life more effectively by:
- **📅 Calendar Integration**: Sync with external calendars to track events and deadlines
- **😴 Sleep Tracking**: Monitor sleep patterns and their impact on academic performance
- **📊 Grade Analytics**: Track grades, assignments, and academic progress
- **⏱️ Time Tracking**: Monitor study hours and workload distribution
- **📈 Data-Driven Insights**: Provide analytics and reports for students and advisors

### Key Features

- **Student Portal**: View calendar, manage reminders, track grades, monitor courses, and analyze workload
- **Advisor Portal**: Access student reports, track student progress, and manage advisor-student relationships
- **Data Analyst Dashboard**: Analyze student engagement trends, manage datasets, and generate comprehensive reports
- **System Administration**: Manage course catalogs, calendar sync settings, and system quality reports

### User Roles

The application supports four distinct user personas:

1. **🎓 Student**: Access personal calendar, reminders, grades, courses, events, and workload analytics
2. **👨‍🏫 Advisor**: View assigned students, generate reports, and track student progress
3. **📊 Data Analyst**: Analyze student data, manage datasets, track engagement metrics, and generate reports
4. **⚙️ System Admin**: Manage system-wide settings, course catalogs, calendar connections, and operational reports

## Prerequisites

- A GitHub Account
- A terminal-based git client or GUI Git client such as GitHub Desktop or the Git plugin for VSCode.
- A distribution of Python running on your laptop. The distribution supported by the course is [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install).
  - Create a new Python 3.11 environment in `conda` named `db-proj` by running:  
     ```bash
     conda create -n db-proj python=3.11
     ```
  - Install the Python dependencies listed in `api/requirements.txt` and `app/src/requirements.txt` into your local Python environment. You can do this by running `pip install -r requirements.txt` in each respective directory.
     ```bash
     cd api
     pip install -r requirements.txt
     cd ../app
     pip install -r requirements.txt
     ```
     Note that the `..` means go to the parent folder of the folder you're currently in (which is `api/` after the first command)
- VSCode with the Python Plugin installed
  - You may use some other Python/code editor.  However, Course staff will only support VS Code. 


## Project Structure

This repository is organized into the following directories:

- **`./app`** - Streamlit frontend application
  - `./app/src` - Main application source code
  - `./app/src/pages` - Streamlit pages organized by user role
  - `./app/src/modules` - Shared modules (navigation, utilities)
- **`./api`** - Flask REST API backend
  - `./api/backend` - Backend source code
  - `./api/backend/studylink` - StudyLink-specific routes organized by persona
    - `data_analyst/` - Data analyst routes (dashboard, metrics, datasets)
    - `advisor/` - Advisor routes
    - `student/` - Student routes
    - `System_Admin/` - System administrator routes
- **`./database-files`** - SQL scripts to initialize the MySQL database
  - `studylink_db.sql` - Main database schema and initial data
- **`./datasets`** - CSV datasets for data import and testing

The project uses Docker Compose to orchestrate three containers:
- **Streamlit App** (port 8501) - Frontend web application
- **Flask API** (port 4000) - REST API backend
- **MySQL Database** (port 3200) - Database server 

## Quick Start Guide

### Starting the Docker Containers

1. **Set up environment variables**:
   - Navigate to the `api` folder
   - Copy `.env.template` to `.env` (if it doesn't exist)
   - Update the `.env` file with your database credentials

2. **Start all containers**:
   ```bash
   docker compose up -d
   ```
   This will start all three services (app, api, db) in the background.

3. **Access the application**:
   - **Streamlit App**: Open your browser and navigate to `http://localhost:8501`
   - **Flask API**: API endpoints are available at `http://localhost:4000`
   - **MySQL Database**: Connect using port `3200` (host: `localhost`)

4. **View container logs**:
   ```bash
   docker compose logs -f [service_name]
   ```
   Replace `[service_name]` with `app`, `api`, or `db` to view specific service logs.

5. **Stop containers**:
   ```bash
   docker compose stop        # Stop containers (keeps data)
   docker compose down        # Stop and remove containers
   docker compose down -v     # Stop, remove containers, and delete volumes
   ```

### Common Docker Commands

- **Start specific service**: `docker compose up [service_name] -d`
  - Example: `docker compose up db -d` (starts only the database)
- **Restart services**: `docker compose restart`
- **View running containers**: `docker compose ps`
- **Rebuild containers** (after code changes): `docker compose up --build -d`

### First-Time Setup

When the MySQL container is created for the first time, it automatically executes all `.sql` files in the `./database-files` folder in alphabetical order. The `studylink_db.sql` file will:
- Create the database schema
- Set up all tables with relationships
- Insert initial sample data

**Important**: If you modify SQL files, you must recreate the database container:
```bash
docker compose down db -v && docker compose up db -d
```

## Learning the Codebase

If you're new to web app development, here's a suggested learning path:

1. **Frontend (`./app`)**: Start with `app/src/Home.py` to understand the landing page and role selection. Then explore the pages in `app/src/pages/` organized by role (01-05: Data Analyst, 11-12: Advisor, 19-25: Student, 40-43: Admin).

2. **Backend (`./api`)**: Explore `api/backend/rest_entry.py` to see how the Flask app is initialized. Then check the route files in `api/backend/studylink/` organized by persona.

3. **Database (`./database-files`)**: Review `studylink_db.sql` to understand the database schema, table relationships, and sample data structure. 

## Setting Up the Repos
<details>
<summary>Setting Up a Personal Testing Repo (Optional)</summary>

### Setting Up A Personal Sandbox Repo (This is Optional)

**Before you start**: You need to have a GitHub account and a terminal-based git client or GUI Git client such as GitHub Desktop or the Git plugin for VSCode.

1. Clone this repo to your local machine.
   1. You can do this by clicking the green "Code" button on the top right of the repo page and copying the URL. Then, in your terminal, run `git clone <URL>`.
   1. Or, you can use the GitHub Desktop app to clone the repo. See [this page](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop) of the GitHub Desktop Docs for more info. 
1. Open the repository folder in VSCode.
1. Set up the `.env` file in the `api` folder based on the `.env.template` file.
   1. Make a copy of the `.env.template` file and name it `.env`. 
   1. Open the new `.env` file. 
   1. On the last line, delete the `<...>` placeholder text, and put a password. Don't reuse any passwords you use for any other services (email, etc.) 
1. For running the testing containers (for your personal repo), you will tell `docker compose` to use a different configuration file than the typical one.  The one you will use for testing is `sandbox.yaml`.
   1. `docker compose -f sandbox.yaml up -d` to start all the containers in the background
   1. `docker compose -f sandbox.yaml down` to shutdown and delete the containers
   1. `docker compose -f sandbox.yaml up db -d` only start the database container (replace db with api or app for the other two services as needed)
   1. `docker compose -f sandbox.yaml stop` to "turn off" the containers but not delete them.
</details>

### Setting Up Your Team's Repo

**Before you start**: As a team, one person needs to assume the role of _Team Project Repo Owner_.

1. The Team Project Repo Owner needs to **fork** this template repo into their own GitHub account **and give the repo a name consistent with your project's name**. If you're worried that the repo is public, don't. Every team is doing a different project.
1. In the newly forked team repo, the Team Project Repo Owner should go to the **Settings** tab, choose **Collaborators and Teams** on the left-side panel. Add each of your team members to the repository with Write access.

**Remaining Team Members**

1. Each of the other team members will receive an invitation to join.
1. Once you have accepted the invitation, you should clone the Team's Project Repo to your local machine.
1. Set up the `.env` file in the `api` folder based on the `.env.template` file.
1. For running the testing containers (for your team's repo):
   1. `docker compose up -d` to start all the containers in the background
   1. `docker compose down` to shutdown and delete the containers
   1. `docker compose up db -d` only start the database container (replace db with api or app for the other two services as needed)
   1. `docker compose stop` to "turn off" the containers but not delete them.

**Note:** You can also use the Docker Desktop GUI to start and stop the containers after the first initial run.

## Development Tips

### Hot Reloading

- **Streamlit App**: Changes to files in `./app/src` are automatically reloaded. If changes don't appear, click the **Always Rerun** button in the Streamlit browser interface.
- **Flask API**: Changes to files in `./api` are automatically reloaded. Check the API logs to confirm the server has restarted.

### Debugging

- **Container Logs**: Use `docker compose logs -f [service_name]` to view real-time logs
- **Database Logs**: Check MySQL container logs in Docker Desktop for SQL errors. Search for "Error" to quickly find issues.
- **API Logs**: Flask logs include request/response information and error traces
- **Streamlit Errors**: Errors appear in both the browser interface and container logs

### Database Management

- **Initial Setup**: The MySQL container executes all `.sql` files in `./database-files` in **alphabetical order** when first created.
- **Updating Schema**: If you modify SQL files, you **MUST** recreate the database container:
  ```bash
  docker compose down db -v && docker compose up db -d
  ```
  This deletes the old database volume and creates a fresh one with updated schema.
- **Data Persistence**: Database data persists in a Docker volume. Use `docker compose down -v` to completely remove all data.

### Troubleshooting

- **Containers won't start**: Check logs with `docker compose logs` to identify errors
- **Port conflicts**: Ensure ports 8501 (Streamlit), 4000 (API), and 3200 (MySQL) are not in use
- **Database connection errors**: Verify `.env` file exists in `./api` folder with correct credentials
- **Code changes not appearing**: Restart the specific container: `docker compose restart [service_name]` 

## Role-Based Access Control (RBAC)

StudyLink implements a simple RBAC system using Streamlit's session state. Users select their role on the home page, which determines what features and pages they can access.

### How RBAC Works in StudyLink

1. **Role Selection**: On the home page (`app/src/Home.py`), users click a button to select their role (Student, Advisor, Data Analyst, or System Admin).

2. **Session State**: The selected role, user name, and authentication status are stored in Streamlit's `session_state` object.

3. **Navigation**: The `SideBarLinks()` function in `app/src/modules/nav.py` reads the user's role from session state and displays only the relevant navigation links in the sidebar.

4. **Page Organization**: Pages are organized by role using numeric prefixes:
   - **01-05**: Data Analyst pages (Dashboard, Dataset Management, Data Quality Tools)
   - **11-12**: Advisor pages (Students, Reports)
   - **19-25**: Student pages (Home, Calendar, Reminders, Grades, Courses, Events, Workload)
   - **40-43**: System Admin pages (Home, Course Catalog, Calendar Sync, Quality Reports)

### Key Files for RBAC

- `app/src/Home.py` - Landing page with role selection
- `app/src/modules/nav.py` - Navigation logic based on user role
- `app/src/.streamlit/config.toml` - Streamlit configuration (sidebar customization)
- `app/src/pages/*.py` - Individual pages organized by role prefix


## API Endpoints

The Flask REST API provides endpoints organized by persona:

### Data Analyst Endpoints (`/analyst/*`)
- `GET /analyst/dashboard` - Dashboard summary with study time, sleep, and GPA data
- `GET /analyst/dashboard/summary` - Aggregate statistics across all students
- `GET /analyst/engagement` - Daily and weekly engagement trends
- `GET /analyst/students/<id>/report` - Comprehensive student report
- `GET /analyst/students/reports` - All student reports for export

### Metrics & Data Endpoints (`/data/*`)
- `GET /data/metrics` - Retrieve metrics with optional filtering
- `POST /data/metrics` - Create new metric entries
- `PUT /data/metrics/<id>` - Update/correct metric values
- `DELETE /data/metrics/<id>` - Remove erroneous metrics
- `GET /data/assignments` - Retrieve assignment data
- `GET /data/data-errors` - Retrieve data error logs

### Dataset Endpoints (`/datasets/*`)
- `GET /datasets` - List all datasets with metadata
- `POST /datasets` - Create new dataset record
- `PUT /datasets/<id>` - Update dataset metadata
- `PUT /datasets/<id>/archive` - Archive a dataset
- `DELETE /datasets/<id>` - Delete archived dataset

See the route files in `api/backend/studylink/` for complete endpoint documentation.

## Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Flask (Python REST API framework)
- **Database**: MySQL 9
- **Containerization**: Docker & Docker Compose
- **Data Visualization**: Plotly, Pandas

## Contributing

This is a course project repository. For development:
1. Create a feature branch
2. Make your changes
3. Test locally using Docker
4. Submit a pull request

## License

This project is part of CS 3200 coursework.