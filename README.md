# Shava

A full-stack web application with Django backend and Next.js frontend.

## Project Structure

- `/backend` - Django REST API backend
- `/frontend` - Next.js frontend application with Tailwind CSS

## Frontend Setup

The frontend is a modern Next.js application with the following features:

- ✅ **Next.js 15** with App Router for file-based routing
- ✅ **Tailwind CSS** for rapid UI development and styling
- ✅ **TypeScript** support for type safety
- ✅ **ESLint** for code quality
- ✅ **Responsive design** out of the box

### Getting Started with Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Scripts

- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build the application for production
- `npm run start` - Start the production server
- `npm run lint` - Run ESLint to check code quality

### Routing Demo

The application includes three main routes to demonstrate Next.js routing:

- `/` - Home page with project overview
- `/about` - About page with project details
- `/contact` - Contact page with a sample form

Each page is styled with Tailwind CSS and includes navigation between routes.

## Backend Setup

See the backend directory for Django setup instructions.