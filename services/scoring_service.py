import os
import json
from datetime import datetime

class ScoringService:
    def __init__(self, data_service):
        self.data_service = data_service
        self.POINTS_PER_WIN = 100
        self.BANKER_MULTIPLIER = 1.5
        self.MAX_POINTS_PER_RACE = 150
        self.ALL_RACES_INDEX_FILE = os.path.join(self.data_service.ALL_RACES_DIR, 'index.json')

    def calculate_race_score(self, bet, race_winner):
        """
        Calculates the score for a single bet on a race.
        Args:
            bet (dict): The user's bet for a race.
            race_winner (str): The winning horse number for the race.
        Returns:
            int: The calculated score.
        """
        if bet and str(bet['horse']) == str(race_winner):
            return self.POINTS_PER_WIN
        return 0

    def calculate_banker_score(self, bankers, race_id, winner):
        """
        Calculates the banker bonus score.
        Args:
            bankers (dict): The user's banker selections.
            race_id (int): The ID of the race.
            winner (str): The winning horse number.
        Returns:
            int: The banker bonus score.
        """
        for user_id, banker_race_id in bankers.items():
            if str(banker_race_id) == str(race_id):
                # We need to find the user's bet for this race to check if it matches the winner.
                # Assuming bets are available in the current context or can be fetched.
                # For now, let's assume we can get the user's bet.
                all_bets = self.data_service.get_bets()
                user_bet = next((b for b in all_bets if str(b['userId']) == str(user_id) and str(b['raceId']) == str(race_id)), None)
                if user_bet and str(user_bet['horse']) == str(winner):
                    return int(self.POINTS_PER_WIN * self.BANKER_MULTIPLIER)
        return 0

    def update_current_user_scores(self):
        """
        Recalculates and updates scores for all users on the current race day.
        """
        print("🧮 Recalculating current user scores...")
        current_day = self.data_service.get_current_race_day_data()
        races = current_day.get("races", [])
        bets = self.data_service.get_bets()
        bankers = self.data_service.get_bankers()
        users = self.data_service.get_users()
        
        # Initialize scores for all users
        user_scores = {user['id']: {"dailyScore": 0, "raceScores": {}} for user in users}

        for race in races:
            race_id = race['id']
            winner = race.get('winner')
            
            if winner is not None:
                # Calculate scores for each user for this completed race
                for user in users:
                    user_id = user['id']
                    
                    # Find the user's bet for this race
                    user_bet = next((b for b in bets if b['userId'] == user_id and b['raceId'] == race_id), None)
                    
                    if user_id not in user_scores:
                        user_scores[user_id] = {"dailyScore": 0, "raceScores": {}}
                        
                    score = 0
                    if user_bet:
                        score = self.calculate_race_score(user_bet, winner)
                        
                        # Apply banker multiplier if applicable
                        if bankers and str(bankers.get(str(user_id))) == str(race_id):
                            score *= self.BANKER_MULTIPLIER
                            
                    user_scores[user_id]["raceScores"][race_id] = score
                    user_scores[user_id]["dailyScore"] += score

        # Update the user scores in the current race day data
        current_day["userScores"] = [
            {"userId": user_id, "dailyScore": score_data["dailyScore"], "raceScores": score_data["raceScores"]}
            for user_id, score_data in user_scores.items()
        ]
        
        self.data_service.save_current_race_day_data(current_day)
        print("✅ Scores recalculated and saved to current race day data.")
        
    def get_current_race_day_scores(self):
        """
        Retrieves the current scores for all users on the current race day.
        """
        current_day = self.data_service.get_current_race_day_data()
        user_scores = current_day.get("userScores", [])
        return user_scores
        
    def update_user_scores(self, race_date=None):
        """
        Updates user scores for a specific race day or all race days.
        """
        print(f"🧮 Updating user scores for {'all race days' if race_date is None else race_date}...")
        
        users = self.data_service.get_users()
        all_bets = self.data_service.get_bets()
        bankers = self.data_service.get_bankers()

        # Initialize global leaderboard
        leaderboard = {str(user['id']): {"userName": user['name'], "totalScore": 0, "raceDays": []} for user in users}
        
        race_days_to_process = []
        if race_date:
            # Process a single specific historical race day
            historical_data = self.data_service.load_historical_data(race_date)
            if historical_data:
                race_days_to_process.append(historical_data)
        else:
            # Process all historical race days
            index_data = self.data_service.get_race_day_index()
            for day_entry in index_data.get("raceDays", []):
                day_data = self.data_service.load_historical_data(day_entry['date'])
                if day_data:
                    race_days_to_process.append(day_data)
        
        for race_day_data in race_days_to_process:
            day_score_data = {str(user['id']): {"dailyScore": 0, "raceScores": {}} for user in users}
            
            for race in race_day_data.get("races", []):
                winner = race.get('winner')
                if winner:
                    for user in users:
                        user_id = str(user['id'])
                        bet = next((b for b in all_bets if str(b['userId']) == user_id and str(b['raceId']) == str(race['id'])), None)
                        
                        score = 0
                        if bet:
                            score = self.calculate_race_score(bet, winner)
                            if bankers and str(bankers.get(user_id)) == str(race['id']):
                                score *= self.BANKER_MULTIPLIER
                        
                        if user_id in day_score_data:
                            day_score_data[user_id]["raceScores"][str(race['id'])] = score
                            day_score_data[user_id]["dailyScore"] += score
            
            # Update user scores for this race day
            race_day_data["userScores"] = [
                {"userId": int(uid), "dailyScore": data["dailyScore"], "raceScores": data["raceScores"]}
                for uid, data in day_score_data.items()
            ]
            self.data_service.save_historical_data(race_day_data['date'], race_day_data)
            
            # Update leaderboard
            for user_id, scores in day_score_data.items():
                if user_id in leaderboard:
                    leaderboard[user_id]["totalScore"] += scores["dailyScore"]
                    leaderboard[user_id]["raceDays"].append({
                        "date": race_day_data['date'],
                        "dailyScore": scores["dailyScore"]
                    })
        
        # Save the updated leaderboard (optional, for caching)
        self.data_service.save_json('data/leaderboard.json', leaderboard)
        print("✅ Global and daily scores updated successfully.")
        return True

    def get_leaderboard_data(self):
        """
        Retrieves the global leaderboard data.
        """
        # Load from a cached file or recalculate
        leaderboard = self.data_service.load_json('data/leaderboard.json', {})
        if not leaderboard:
            self.update_user_scores()
            leaderboard = self.data_service.load_json('data/leaderboard.json', {})

        return sorted(list(leaderboard.values()), key=lambda x: x['totalScore'], reverse=True)
