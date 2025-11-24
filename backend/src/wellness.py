import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger("wellness")

class WellnessManager:
    def __init__(self, storage_file: str = "wellness_log.json"):
        self.storage_file = storage_file
        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self):
        """Loads the wellness log from the JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode {self.storage_file}. Starting with empty history.")
                self.history = []
        else:
            self.history = []

    def save_entry(self, mood: str, objectives: List[str], summary: str):
        """Saves a new check-in entry to the log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "mood": mood,
            "objectives": objectives,
            "summary": summary
        }
        self.history.append(entry)
        self._save_to_file()
        return entry

    def _save_to_file(self):
        """Persists the history to the JSON file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save wellness log: {e}")

    def get_context_prompt(self) -> str:
        """Generates a context string for the agent based on the last check-in."""
        if not self.history:
            return "This is the first time you are meeting the user. Welcome them warmly."

        last_entry = self.history[-1]
        
        # Parse timestamp for friendly display
        try:
            dt = datetime.fromisoformat(last_entry["timestamp"])
            date_str = dt.strftime("%A, %B %d")
        except:
            date_str = "the last session"

        prompt = f"""
Here is context from the user's last check-in on {date_str}:
- Mood: {last_entry.get('mood', 'Unknown')}
- Objectives: {', '.join(last_entry.get('objectives', []))}
- Summary: {last_entry.get('summary', '')}

Use this information to personalize your greeting. For example, ask if they completed their objectives or if their mood has improved.
"""
        return prompt

    def get_weekly_summary(self) -> str:
        """Generates a simple summary of the last 7 days (Advanced Goal)."""
        if not self.history:
            return "No history available for a weekly summary."

        # Filter for last 7 days could be added here, for now just taking all history
        # In a real app, we'd filter by timestamp
        
        total_entries = len(self.history)
        entries_with_goals = sum(1 for e in self.history if e.get('objectives'))
        
        return f"You have checked in {total_entries} times. You set goals in {entries_with_goals} of those sessions."
