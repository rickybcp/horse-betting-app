"""
Data Service for Horse Betting App
Centralized service for all data-related logic including file I/O,
user score calculations, and race day management.
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import CloudStorageManager from the utils directory
from utils.cloud_storage import get_storage_manager, init_cloud_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataService:
    """
    Manages all data operations for the application.
    """
    DATA_DIR = 'data'
    ALL_RACES_DIR = os.path.join(DATA_DIR, 'all_races')
    ALL_RACES_INDEX_FILE = os.path.join(ALL_RACES_DIR, 'index.json')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')

    def __init__(self):
        # Initialize the storage manager
        self.storage_manager = get_storage_manager()

    def init_cloud_storage_and_local_dirs(self):
        """
        Initializes cloud storage and creates local data directories.
        """
        # Create data directories if they don't exist
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.ALL_RACES_DIR, exist_ok=True)
        logger.info("✓ Data directories initialized.")
    
    def init_default_data(self):
        """
        Initializes default data files if they don't exist.
        This runs on app startup to ensure required files are present.
        """
        # Ensure the users.json file exists
        if not self.storage_manager.file_exists(self.USERS_FILE):
            self.save_users([])
            logger.info("✓ Created default users.json file.")

        # Ensure the all_races/index.json file exists
        if not self.storage_manager.file_exists(self.ALL_RACES_INDEX_FILE):
            self.save_race_day_index({"raceDays": []})
            logger.info("✓ Created default all_races/index.json file.")
    
    def get_current_race_day_data(self) -> Dict[str, Any]:
        """
        Gets the current active race day data from the storage.
        """
        index_data = self.get_race_day_index()
        current_day_record = next(
            (day for day in index_data.get("raceDays", []) if day.get("current")), None
        )
        
        if current_day_record:
            filepath = os.path.join(self.ALL_RACES_DIR, f"{current_day_record['date']}.json")
            data = self.storage_manager.load_file(filepath, {})
            # Ensure required fields are present
            data.setdefault('bets', {})
            data.setdefault('bankers', {})
            data.setdefault('userScores', [])
            return data
        
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "races": [],
            "status": "upcoming",
            "bets": {},
            "bankers": {},
            "userScores": []
        }

    def save_current_race_day_data(self, data: Dict[str, Any]) -> bool:
        """
        Saves the current race day data.
        """
        date_str = data.get("date")
        if not date_str:
            logger.error("❌ Cannot save race day data without a valid date.")
            return False
        
        filepath = os.path.join(self.ALL_RACES_DIR, f"{date_str}.json")
        return self.storage_manager.save_file(filepath, data)

    def get_race_day_index(self) -> Dict[str, Any]:
        """
        Loads the index of all race days from storage.
        """
        return self.storage_manager.load_file(self.ALL_RACES_INDEX_FILE, {"raceDays": []})

    def save_race_day_index(self, data: Dict[str, Any]) -> bool:
        """
        Saves the race day index to storage.
        """
        return self.storage_manager.save_file(self.ALL_RACES_INDEX_FILE, data)
        
    def get_race_day_data(self, date: str) -> Dict[str, Any]:
        """
        Gets a specific race day's data from storage.
        """
        filepath = os.path.join(self.ALL_RACES_DIR, f"{date}.json")
        data = self.storage_manager.load_file(filepath, {})
        data.setdefault('bets', {})
        data.setdefault('bankers', {})
        data.setdefault('userScores', [])
        return data
        
    def get_leaderboard_data(self) -> Dict[str, Any]:
        """
        Aggregates scores from all race days to create a leaderboard.
        """
        index_data = self.get_race_day_index()
        race_day_records = index_data.get("raceDays", [])
        
        all_user_scores = {}
        for record in race_day_records:
            date_str = record["date"]
            day_data = self.get_race_day_data(date_str)
            
            for user_score in day_data.get("userScores", []):
                user_id = user_score["userId"]
                score = user_score["score"]
                
                if user_id not in all_user_scores:
                    all_user_scores[user_id] = {
                        "userId": user_id,
                        "name": user_score["name"],
                        "totalScore": 0,
                        "rank": 0
                    }
                all_user_scores[user_id]["totalScore"] += score
        
        leaderboard = list(all_user_scores.values())
        leaderboard.sort(key=lambda x: x["totalScore"], reverse=True)
        
        for i, user in enumerate(leaderboard):
            user["rank"] = i + 1
            
        return {"users": leaderboard, "type": "total"}

    def update_user_scores(self, race_day_data: Dict[str, Any]) -> None:
        """
        Recalculates scores for all users for a given race day.
        """
        users = self.load_users()
        race_day_data["userScores"] = []

        for user in users:
            user_id = user['id']
            daily_score = self.calculate_user_score_for_race_day(race_day_data, user_id)
            race_day_data["userScores"].append({
                "userId": user_id,
                "name": user['name'],
                "score": daily_score
            })

        # Sort by score
        race_day_data["userScores"].sort(key=lambda x: x.get('score', 0), reverse=True)

        # Add rankings
        for i, user_score in enumerate(race_day_data["userScores"]):
            user_score['rank'] = i + 1
            
    def update_current_user_scores(self) -> None:
        """
        Recalculate scores for the current race day and save the data.
        """
        current_race_day_data = self.get_current_race_day_data()
        self.update_user_scores(current_race_day_data)
        self.save_current_race_day_data(current_race_day_data)
        
    def calculate_user_score_for_race_day(self, race_day_data: Dict[str, Any], user_id: str) -> int:
        """
        Calculates a single user's total score for a race day.
        """
        total_score = 0
        user_bets = race_day_data.get('bets', {}).get(user_id, {})
        user_bankers = race_day_data.get('bankers', {}).get(user_id, [])
        races = race_day_data.get('races', [])

        for race in races:
            race_id = race['id']
            winner = race.get('winner')
            if winner:
                # Check for correct bet on the race winner
                bet = user_bets.get(str(race_id))
                if bet and bet == winner:
                    is_banker = False
                    for banker_bet in user_bankers:
                        if banker_bet.get('raceId') == race_id and banker_bet.get('horseNumber') == winner:
                            is_banker = True
                            break
                    
                    if is_banker:
                        total_score += 5  # Banker bet
                    else:
                        total_score += 3  # Standard bet

        return total_score

    def load_users(self) -> List[Dict[str, Any]]:
        """
        Loads the list of all users.
        """
        users = self.storage_manager.load_file(self.USERS_FILE, [])
        # Ensure each user has a unique ID and a name
        for user in users:
            user.setdefault('id', 'temp_id')
            user.setdefault('name', 'Unknown User')
        return users
    
    def save_users(self, users: List[Dict[str, Any]]) -> bool:
        """
        Saves the list of users.
        """
        return self.storage_manager.save_file(self.USERS_FILE, users)
