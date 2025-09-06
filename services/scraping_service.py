import os
from datetime import datetime
from utils.smspariaz_scraper import scrape_horses_from_smspariaz
# from utils.results_scraper import scrape_results_with_fallback
from services.data_service import DataService

class ScrapingService:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        
    def scrape_races(self):
        """Scrapes races for a new race day and returns the data."""
        try:
            current_day = scrape_horses_from_smspariaz()
            return {"success": True, "data": current_day}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scrape_all_results(self):
        """Scrapes results for all races of the current race day and returns the updated data."""
        try:
            current_day = self.data_service.get_current_race_day_data()
            
            if not current_day:
                return {"success": False, "error": "No active race day to scrape results for."}
            
            updated_races = scrape_results_with_fallback(current_day['races'])
            
            current_day['races'] = updated_races
            current_day['lastUpdated'] = datetime.utcnow().isoformat()
            
            return {"success": True, "data": current_day}
        except Exception as e:
            return {"success": False, "error": str(e)}
