# Project Overview

FastAPI application that displays Google Sheets data in a formatted table using Great Tables.

## Recent Changes (November 10, 2025)

### Fixed HTTP 401 Unauthorized Error
- **Issue**: App was failing with HTTP 401 error when trying to access Google Sheets
- **Root Cause**: The Google Sheet was not publicly accessible, and the app wasn't using proper authentication
- **Solution**: 
  1. Integrated Replit Google Sheets connector for OAuth authentication
  2. Updated `utils/google_sheets.py` to use OAuth credentials from Replit connector
  3. Changed `require_auth=True` in main.py to use authenticated access
  4. Changed server port from 8080 to 5000 for Replit webview compatibility

### Technical Implementation
- Using `google.oauth2.credentials.Credentials` for proper OAuth flow
- Fetching fresh credentials from Replit connector on each request (no caching)
- Proper error handling with descriptive messages
- Server now runs on port 5000 with webview output type

## Project Structure

- `main.py` - FastAPI application that serves the Google Sheets data as HTML table
- `utils/google_sheets.py` - Helper functions for Google Sheets integration with OAuth
- `requirements.txt` - Python dependencies

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- Great Tables - Table formatting library
- gspread - Google Sheets API client
- pandas - Data manipulation
- google-auth - Google authentication
- requests - HTTP client for connector API

## Configuration

- **Port**: 5000 (required for Replit webview)
- **Authentication**: Replit Google Sheets connector (OAuth)
- **Google Sheet URL**: Set in `WORKSHEET_URL` variable in main.py

## User Preferences

- None documented yet
