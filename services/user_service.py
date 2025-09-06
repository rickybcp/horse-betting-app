# services/user_service.py
import os
import json
from datetime import datetime

class UserService:
    def __init__(self, data_service, scoring_service):
        self.data_service = data_service
        self.scoring_service = scoring_service

    def get_users(self):
        """Retrieves all users."""
        return self.data_service.get_users()

    def add_user(self, new_user_name):
        """Adds a new user to the system."""
        users = self.data_service.get_users()
        new_user = {
            "id": len(users) + 1,
            "name": new_user_name,
            "active": True
        }
        users.append(new_user)
        self.data_service.save_users(users)
        return new_user

    def delete_all_users(self):
        """Deletes all users from the system."""
        self.data_service.save_users([])
        return True

    def get_user_performance_on_date(self, user_id, race_date):
        """Get user's detailed performance on a specific race day."""
        race_day_data = self.data_service.load_historical_data(race_date)
        
        if not race_day_data:
            return {"success": False, "error": f"Race day {race_date} not found"}
        
        user_performance = next((score for score in race_day_data.get("userScores", []) if score["userId"] == user_id), None)
        
        if not user_performance:
            return {"success": False, "error": f"User {user_id} did not participate on {race_date}"}
        
        enhanced_performance = {
            "raceDate": race_date,
            "userPerformance": user_performance,
            "races": race_day_data.get("races", [])
        }
        
        return {"success": True, "performance": enhanced_performance}

    def list_race_days(self):
        """Returns a list of all available race days from the index file."""
        try:
            index_data = self.data_service.get_race_day_index()
            return {"success": True, "raceDays": index_data.get("raceDays", [])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_current_race_day_data(self):
        """Get all data for the current race day."""
        try:
            current_day_data = self.data_service.get_current_race_day_data()
            return {"success": True, "data": current_day_data}
        except FileNotFoundError:
            return {"success": False, "error": "Race day data not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_current_race_day(self, data):
        """Updates the current race day with new data."""
        try:
            self.data_service.save_current_race_day_data(data)
            return {"success": True, "data": data}
        except Exception as e:
            print(f"Error updating race day data: {e}")
            return {"success": False, "error": "Failed to update race day data"}

    def get_specific_race_day_data(self, race_day):
        """Returns all data for a specific race day identified by its date string."""
        try:
            data = self.data_service.load_historical_data(race_day)
            if data:
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"Race day {race_day} not found"}
        except FileNotFoundError:
            return {"success": False, "error": f"Race day {race_day} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def complete_race_day(self, race_day):
        """Marks a specific race day as complete and saves it as historical data."""
        try:
            data = self.data_service.get_current_race_day_data()
            
            if data.get("date") != race_day:
                return {"success": False, "error": "Mismatch between request path and current race day"}
            
            data['status'] = 'completed'
            self.data_service.save_historical_data(race_day, data)
            
            self.scoring_service.update_user_scores()
            
            return {"success": True, "message": f"Race day {race_day} marked as completed and scores updated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_historical_race_days(self):
        """Returns a list of all historical race days."""
        try:
            index_data = self.data_service.get_race_day_index()
            historical_days = [day for day in index_data.get("raceDays", []) if day.get("status") == "completed"]
            return {"success": True, "historical_race_days": historical_days}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_historical_race_day(self, race_date):
        """Returns all data for a specific historical race day."""
        try:
            data = self.data_service.load_historical_data(race_date)
            if data:
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": f"Historical race day {race_date} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
