# MakeMyTrip Customer Intelligence Platform

An AI-powered travel assistant built with React, FastAPI, PostgreSQL, and the Gemini API. The platform helps customers manage travel information, retrieve booking details, and interact with an AI assistant for trip planning and customer support.

## Features

- **Customer management:** Customer profiles and travel preferences.
- **Booking management:** Store and retrieve booking information.
- **AI travel assistant:** Natural-language conversations powered by Gemini.
- **Customer support:** Support cases and interaction history.
- **Persistent conversations:** Save chat sessions and messages so users can continue previous conversations.
- **AI insights:** Store customer insights to support personalized recommendations.

## Architecture

- **Frontend:** React, Vite
- **Backend:** FastAPI, Python, Pydantic
- **Database:** PostgreSQL or the configured development database
- **AI:** Gemini API with backend tool integration

The AI agent accesses authorized backend operations to retrieve customer and booking information. Database access, validation, and business logic remain on the backend.

## Project Structure

- `frontend/` — React application
- `backend/app/models/` — Database models
- `backend/app/schemas/` — Pydantic schemas
- `backend/app/routers/` — API endpoints
- `backend/app/services/` — Business logic
- `backend/tests/` — Automated tests

## Setup

### Backend

1. Create and activate a Python virtual environment.
2. Install dependencies from `backend/requirements.txt`.
3. Configure environment variables using `backend/.env.example`.
4. Start the FastAPI application using the appropriate Uvicorn command for your project.

### Frontend

1. Navigate to `frontend/`.
2. Run `npm install`.
3. Configure the frontend API URL.
4. Run `npm run dev`.

## Security

- API keys are configured through environment variables.
- Credentials and local database files must not be committed.
- Customer data access must be authenticated and authorized.

## Current Scope and Limitations

The availability of real flights, hotels, prices, bookings, cancellations, and refunds depends on integration with the relevant travel provider APIs. Any simulated results should be identified as mock data.

## Disclaimer

This is an independent portfolio project and is not an official MakeMyTrip product or an affiliated service.
