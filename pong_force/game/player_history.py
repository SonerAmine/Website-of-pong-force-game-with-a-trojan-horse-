# ===== PONG FORCE - PLAYER HISTORY =====

import json
import os
from datetime import datetime

class PlayerHistory:
    def __init__(self):
        """Initialize player history system"""
        self.history_file = os.path.join(os.path.dirname(__file__), "..", "player_history.json")
        self.history_data = self.load_history()
    
    def load_history(self):
        """Load player history from file"""
        default_history = {
            "player1": {
                "vs_robot": {"wins": 0, "losses": 0, "games_played": 0},
                "two_player_local": {"wins": 0, "losses": 0, "games_played": 0},
                "multiplayer": {"wins": 0, "losses": 0, "games_played": 0}
            },
            "player2": {
                "vs_robot": {"wins": 0, "losses": 0, "games_played": 0},
                "two_player_local": {"wins": 0, "losses": 0, "games_played": 0},
                "multiplayer": {"wins": 0, "losses": 0, "games_played": 0}
            },
            "last_updated": None
        }
        
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    # Ensure all modes exist for backward compatibility
                    for player in ["player1", "player2"]:
                        for mode in ["vs_robot", "two_player_local", "multiplayer"]:
                            if mode not in history[player]:
                                history[player][mode] = {"wins": 0, "losses": 0, "games_played": 0}
                            elif "games_played" not in history[player][mode]:
                                history[player][mode]["games_played"] = history[player][mode].get("wins", 0) + history[player][mode].get("losses", 0)
                    return history
            except Exception as e:
                print(f"Error loading player history: {e}")
                return default_history
        else:
            return default_history
    
    def save_history(self):
        """Save player history to file"""
        try:
            self.history_data["last_updated"] = datetime.now().isoformat()
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2)
            print("Player history saved")
        except Exception as e:
            print(f"Error saving player history: {e}")
    
    def record_game(self, player_id, mode, won, win_score=None, lose_score=None):
        """Record a game result
        
        Args:
            player_id (int): Player ID (1 or 2)
            mode (str): Game mode ("vs_robot", "two_player_local", "multiplayer")
            won (bool): True if player won, False if lost
            win_score (int, optional): Player's score
            lose_score (int, optional): Opponent's score
        """
        player_key = f"player{player_id}"
        
        if mode not in self.history_data[player_key]:
            self.history_data[player_key][mode] = {"wins": 0, "losses": 0, "games_played": 0}
        
        if won:
            self.history_data[player_key][mode]["wins"] += 1
        else:
            self.history_data[player_key][mode]["losses"] += 1
        
        self.history_data[player_key][mode]["games_played"] += 1
        
        # Add recent game details
        if "recent_games" not in self.history_data[player_key][mode]:
            self.history_data[player_key][mode]["recent_games"] = []
        
        game_record = {
            "date": datetime.now().isoformat(),
            "won": won,
            "win_score": win_score,
            "lose_score": lose_score
        }
        
        self.history_data[player_key][mode]["recent_games"].append(game_record)
        
        # Keep only last 10 games
        if len(self.history_data[player_key][mode]["recent_games"]) > 10:
            self.history_data[player_key][mode]["recent_games"] = self.history_data[player_key][mode]["recent_games"][-10:]
        
        self.save_history()
    
    def get_stats(self, player_id, mode):
        """Get player statistics for a specific mode
        
        Args:
            player_id (int): Player ID (1 or 2)
            mode (str): Game mode
            
        Returns:
            dict: Statistics dictionary
        """
        player_key = f"player{player_id}"
        if mode in self.history_data[player_key]:
            stats = self.history_data[player_key][mode].copy()
            # Calculate win rate
            if stats["games_played"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["games_played"]) * 100
            else:
                stats["win_rate"] = 0
            return stats
        else:
            return {"wins": 0, "losses": 0, "games_played": 0, "win_rate": 0}
    
    def get_all_stats(self, player_id):
        """Get all statistics for a player
        
        Args:
            player_id (int): Player ID (1 or 2)
            
        Returns:
            dict: All statistics for the player
        """
        player_key = f"player{player_id}"
        all_stats = {}
        
        for mode in ["vs_robot", "two_player_local", "multiplayer"]:
            all_stats[mode] = self.get_stats(player_id, mode)
        
        # Calculate overall stats
        total_wins = sum(all_stats[mode]["wins"] for mode in all_stats)
        total_losses = sum(all_stats[mode]["losses"] for mode in all_stats)
        total_games = total_wins + total_losses
        
        all_stats["overall"] = {
            "wins": total_wins,
            "losses": total_losses,
            "games_played": total_games,
            "win_rate": (total_wins / total_games * 100) if total_games > 0 else 0
        }
        
        return all_stats
    
    def reset_stats(self, player_id=None, mode=None):
        """Reset statistics
        
        Args:
            player_id (int, optional): Specific player to reset (1 or 2). If None, resets all players
            mode (str, optional): Specific mode to reset. If None, resets all modes
        """
        players = [f"player{player_id}"] if player_id else ["player1", "player2"]
        modes = [mode] if mode else ["vs_robot", "two_player_local", "multiplayer"]
        
        for player_key in players:
            for mode_name in modes:
                if mode_name in self.history_data[player_key]:
                    self.history_data[player_key][mode_name] = {
                        "wins": 0, 
                        "losses": 0, 
                        "games_played": 0,
                        "recent_games": []
                    }
        
        self.save_history()
        print(f"Reset stats for players: {players}, modes: {modes}")
