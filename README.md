# AviTrail - Flight Logging App
AviTrail is a flight logging web application that allows users to track their flights and store flight history. It also enables them to visualize their journeys on an interactive map.
The application consists of a Django backend and a Vue 3 frontend.

## Features

- User authentication: Secure login with token-based authentication
- Flight Logging: Add, edit, and delete flights
- Flight History: View and search through flight history
- Interactive Map: Visualize flight paths on an interactive map
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
- TypeScript: Superset of JavaScript for static typing
- Vite: Build tool for modern web development

## Setup Instructions

### Backend
1. Clone the repository

3. Use docker-compose to initialize the PostgreSQL database
   1. `docker compose up -d`
4. Run the Django migrations
   1. `docker compose exec web python /app/manage.py migrate`'
5. *Optional* Create a superuser
   1. `docker compose exec web python /app/manage.py createsuperuser`


### Frontend
1. Navigate to the `frontend` directory
2. Install dependencies
   1. `pnpm install`
2. Start the development server
   1. `pnpm run dev`
2. Navigate to `http://localhost:5173` in your browser

   > Note: frontend docker setup is in progress

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request.
