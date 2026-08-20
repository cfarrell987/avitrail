# AviTrail - Flight Logging App
AviTrail is a flight logging web application that allows users to track their flights and store flight history. It also enables them to visualize their journeys on an interactive map.
The application consists of a Django backend and a Vue 3 frontend.

## Features

- User authentication: Secure login with token-based authentication
- Flight Logging: Add, edit, and delete flights
- Flight History: View and search through flight history
- Interactive Map: Visualize flight paths on an interactive map - _To be implemented_
- REST API: Built using Django REST framework for easy data retrieval and manipulation allowing for future integrations

## Tech Stack

### Backend
- Django: Web framework for building the backend
- Django REST framework: Toolkit for building Web APIs
- PostgreSQL: Database for storing flight data
- Docker: Containerization for easy deployment

### Frontend
- Vue 3: JavaScript framework for building the frontend
- Axios: Promise-based HTTP client for making API requests
- Vite: Build tool for modern web development

## Setup Instructions

### Quick start (Docker)
1. Clone the repository
2. `docker compose up -d` — brings up Postgres, the Django backend (migrations run automatically on boot), and the frontend (built and served via nginx)
3. Navigate to `http://localhost:8080` in your browser
4. *Optional* Create a superuser: `docker compose exec web python manage.py createsuperuser`

### Frontend (local dev)
For active frontend development, run it outside Docker so you get Vite's dev server (hot reload, etc.) instead of a static nginx build:
1. Bring up just the backend: `docker compose up -d db web`
2. Navigate to the `frontend` directory
3. Install dependencies: `pnpm install`
4. Start the dev server: `pnpm run dev`
5. Navigate to `http://localhost:5173` in your browser

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.


## Acknowledgements
- Airport data provided by [mwgg/Airports](https://github.com/mwgg/Airports)
- Airline data provided by [npow/airline-codes](https://github.com/npow/airline-codes/)
