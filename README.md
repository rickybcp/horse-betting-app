# 🏇 Lekours - Horse Racing Betting Application

A full-stack web application for horse racing betting with real-time race data scraping, user management, and scoring system.

## 📋 Table of Contents
- [System Architecture](#system-architecture)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [API Endpoints](#api-endpoints)
- [Scoring System](#scoring-system)
- [Web Scrapers](#web-scrapers)
- [Frontend Components](#frontend-components)
- [Installation & Setup](#installation--setup)
- [Deployment](#deployment)

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │◄──►│   (Flask)       │◄──►│   Websites      │
│                 │    │                 │    │                 │
│ - User Interface│    │ - API Server    │    │ - SMS Pariaz    │
│ - Betting UI    │    │ - Data Storage  │    │ - MTC Jockey    │
│ - Score Display │    │ - Web Scrapers  │    │   Club          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   Data Storage  │
                       │   (JSON Files)  │
                       │                 │
                       │ - users.json    │
                       │ - races.json    │
                       │ - bets.json     │
                       │ - bankers.json  │
                       └─────────────────┘
```

## 🎯 Core Features

### 1. **User Management**
- Add new users to the betting system
- Track individual user scores and performance
- Persistent user data storage

### 2. **Race Data Management**
- **Real-time race scraping** from SMS Pariaz and MTC Jockey Club websites
- **Manual race result entry** for completed races
- **Automatic result simulation** for testing purposes
- Race status tracking (upcoming/completed)

### 3. **Betting System**
- **Individual race betting** - Users select horses for each race
- **Banker betting** - Users select one "banker" race for double points
- Real-time bet tracking and validation

### 4. **Scoring System**
- **Points-based scoring** based on horse odds:
  - 1 point: Odds < 5.0
  - 2 points: Odds 5.0 - 10.0
  - 3 points: Odds > 10.0
- **Banker bonus**: 2x multiplier if user wins their banker race
- **Cumulative scoring** across multiple race days

### 5. **Daily Reset Functionality**
- Calculate and apply daily scores to user totals
- Reset race data, bets, and bankers for new race day
- Maintain historical user scores

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask (Python)
- **CORS**: Flask-CORS for cross-origin requests
- **Web Scraping**: Selenium WebDriver + BeautifulSoup
- **Data Storage**: JSON files (users.json, races.json, bets.json, bankers.json)
- **Deployment**: Gunicorn server

### Frontend
- **Framework**: React 19.1.1
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Build Tool**: Create React App

### Infrastructure
- **Deployment**: Render.com (configured via render.yaml)
- **Environment**: Python 3.9+, Node.js

## 📁 Project Structure

```
Lekours/
├── 📁 horse-betting-frontend/          # React frontend application
│   ├── 📁 src/
│   │   ├── App.js                      # Main React component
│   │   ├── index.js                    # React entry point
│   │   └── index.css                   # Tailwind CSS styles
│   ├── 📁 public/                      # Static assets
│   └── package.json                    # Frontend dependencies
│
├── 📁 utils/                           # Scraper modules
│   ├── __init__.py                     # Package init
│   ├── smspariaz_scraper.py           # SMS Pariaz race scraper
│   └── mtc_scraper.py                 # MTC Jockey Club scraper
│
├── 📁 data/                           # JSON data storage
│   ├── users.json                     # User profiles and scores
│   ├── races.json                     # Race data and horses
│   ├── bets.json                      # User betting choices
│   └── bankers.json                   # User banker selections
│
├── server.py                          # Main Flask backend server
├── requirements.txt                   # Python dependencies
├── render.yaml                        # Deployment configuration
├── start-local.bat                    # Windows startup script
├── start-local.ps1                    # PowerShell startup script
├── test_smspariaz_scraper.py         # Scraper testing utility
└── racecard_scraper.py               # Reference scraper implementation
```

## 🔄 Data Flow

### 1. **Race Data Acquisition**
```
External Website → Web Scraper → JSON Processing → races.json
                                                 ↓
                                              Frontend Display
```

### 2. **User Betting Flow**
```
User Selection → Frontend → API Request → Validation → bets.json/bankers.json
```

### 3. **Score Calculation Flow**
```
Race Results → Points Calculation → Banker Multiplier → User Score Update
```

## 🔌 API Endpoints

### User Management
- `GET /api/users` - Retrieve all users
- `POST /api/users` - Add new user (requires: `{name: string}`)

### Race Management
- `GET /api/races` - Get current race data
- `POST /api/races/scrape` - Scrape SMS Pariaz races

- `POST /api/races/results` - Auto-simulate race results
- `POST /api/races/<race_id>/result` - Set manual race result (requires: `{winner: number}`)

### Betting System
- `GET /api/bets` - Get all user bets
- `POST /api/bets` - Place bet (requires: `{userId, raceId, horseNumber}`)
- `GET /api/bankers` - Get user banker selections
- `POST /api/bankers` - Set banker race (requires: `{userId, raceId}`)

### System Management
- `POST /api/reset` - Calculate scores and reset for new day

## 🏆 Scoring System

### Base Points Calculation
```javascript
// Points awarded based on winning horse odds
if (odds > 10.0) points = 3;
else if (odds > 5.0) points = 2;
else points = 1;
```

### Banker Bonus System
```javascript
// If user wins their banker race, multiply daily total by 2
if (userWonBankerRace) {
    dailyScore = dailyScore * 2;
}
totalScore += dailyScore;
```

### Score Categories
- **Daily Score**: Points earned in current race day
- **Total Score**: Cumulative score across all race days
- **Banker Multiplier**: Applied only if banker race is won

## 🕷️ Web Scrapers

### SMS Pariaz Scraper (`utils/smspariaz_scraper.py`)
- **Target**: https://www.smspariaz.com/local/
- **Method**: Selenium WebDriver + BeautifulSoup
- **Data Extracted**:
  - Race times and titles
  - Horse names and numbers
  - Win odds (converted from "310" → 3.10 format)
- **Features**:
  - Anti-detection measures (user agent spoofing, human-like behavior)
  - Robust error handling
  - Returns empty array on failure (no dummy data)

### MTC Jockey Club Scraper (`utils/mtc_scraper.py`)
- **Target**: https://www.mtcjockeyclub.com/form-guide/fixtures
- **Method**: Selenium WebDriver
- **Process**:
  1. Navigate to fixtures page
  2. Optional month selection
  3. Click "View Race Card" link
  4. Extract race tabs and horse data
- **Data Extracted**:
  - Race names and times
  - Horse entries (odds may not be available)

## 🎨 Frontend Components

### Main App Component (`App.js`)
- **State Management**: Users, races, bets, bankers
- **UI Sections**:
  - Header with app title
  - User management panel
  - Race data controls (scraping buttons)
  - Betting interface
  - Score display and reset functionality

### Key Features
- **Responsive Design**: Tailwind CSS for mobile-friendly UI
- **Real-time Updates**: Automatic refresh after API calls
- **User Feedback**: Success/error notifications
- **Bet Validation**: Prevents duplicate bets, validates selections

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js and npm
- Google Chrome (for web scraping)

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python server.py
# Server runs on http://localhost:5000
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd horse-betting-frontend

# Install Node dependencies
npm install

# Start React development server
npm start
# Frontend runs on http://localhost:3000
```

### Quick Start (Windows)
```bash
# Option 1: Batch file
start-local.bat

# Option 2: PowerShell script
./start-local.ps1
```

## 🌐 Deployment

### Render.com Configuration (render.yaml)
```yaml
services:
  - type: web
    name: horse-betting-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

### Environment Variables
- `PORT`: Server port (default: 5000)
- Production deployment uses Gunicorn WSGI server

## 📊 Data Schemas

### User Object
```json
{
  "id": "1",
  "name": "John Doe",
  "totalScore": 25
}
```

### Race Object
```json
{
  "id": "smspariaz_R1_20250809",
  "name": "FASHION HEIGHTS - MIA BIJOUX CUP",
  "time": "12:45",
  "horses": [
    {
      "number": 1,
      "name": "CAPTAIN'S CONCORT",
      "odds": 3.10,
      "points": 1
    }
  ],
  "winner": null,
  "status": "upcoming"
}
```

### Bet Storage
```json
{
  "userId": {
    "raceId": horseNumber
  }
}
```

### Banker Storage
```json
{
  "userId": "raceId"
}
```

## 🔧 Key Implementation Notes

1. **Data Persistence**: All data stored in JSON files in `/data` directory
2. **Error Handling**: Graceful fallbacks for scraping failures
3. **Race ID Format**: `source_raceNumber_date` (e.g., "smspariaz_R1_20250809")
4. **CORS Configuration**: Allows all origins for development flexibility
5. **Headless Browser**: Scrapers run in headless mode for server deployment
6. **Automatic Data Initialization**: Creates empty data files on server startup

## 🎯 Future Enhancement Areas

- Database integration (PostgreSQL/MongoDB)
- User authentication and sessions
- Historical race data archive
- Advanced analytics and statistics
- Mobile app development
- Real-time websocket updates
- Multi-track betting support

---

This README provides a comprehensive overview of the Lekours horse betting application architecture, making it easy for any developer or LLM to understand the system and implement modifications effectively.
