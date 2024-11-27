# Order and Customer Number Generator

## Overview
A Flask web application that generates auto-incrementing order and customer numbers with a year-based prefix using Neon PostgreSQL. Now includes user authentication.

## Features
- User registration and login
- Generate unique customer numbers
- Generate unique order numbers
- Numbers prefixed with last two digits of the current year
- Secure authentication with password hashing

## Prerequisites
- Python 3.8+
- Neon PostgreSQL database
- Vercel account for deployment

## Local Development Setup
1. Clone the repository
2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r src/requirements.txt
   ```
4. Set environment variables:
   - `POSTGRES_URL`: PostgreSQL database connection string
   - `FLASK_SECRET_KEY`: Secret key for Flask sessions

## Authentication
- Register a new account at `/register`
- Login at `/login`
- Number generation is only accessible to authenticated users

## Deployment
### Vercel Deployment
1. Install Vercel CLI: `npm i -g vercel`
2. Login to Vercel: `vercel login`
3. Deploy: `vercel`
4. Set environment variables in Vercel project settings

## Database Schema
- Users table: Stores user credentials
- Customers table: Stores generated customer numbers
- Orders table: Stores generated order numbers

## Number Generation Logic
- Numbers start with last two digits of the year
- Followed by a 4-digit sequential number
- Example: 230001 (first number in 2023)

## Security
- Passwords are hashed using Werkzeug security
- Login required for number generation
- Unique username constraint
