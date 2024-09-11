# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 15:44:34 2024

@author: logan
"""

from datetime import datetime, timedelta
from ics import Calendar, Event

# Create a calendar
cal = Calendar()

# Function to create a game event
def create_game_event(team, opponent, date, time, network):
    event = Event()
    event.name = f'{team} vs {opponent}'
    event.begin = f'{date} {time}'
    event.end = (datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M') + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
    event.description = f'Watch on {network}'
    event.location = 'TBD'
    cal.events.add(event)

# Schedule information for Detroit Lions and Green Bay Packers
games = [
    # Detroit Lions
    {"team": "Detroit Lions", "opponent": "Kansas City Chiefs", "date": "2024-09-05", "time": "20:20", "network": "NBC"},
    {"team": "Detroit Lions", "opponent": "Seattle Seahawks", "date": "2024-09-10", "time": "13:00", "network": "FOX"},
    {"team": "Detroit Lions", "opponent": "Atlanta Falcons", "date": "2024-09-17", "time": "13:00", "network": "FOX"},
    {"team": "Detroit Lions", "opponent": "Green Bay Packers", "date": "2024-09-24", "time": "20:15", "network": "Prime Video"},
    {"team": "Detroit Lions", "opponent": "Carolina Panthers", "date": "2024-10-01", "time": "13:00", "network": "FOX"},
    
    # Green Bay Packers
    {"team": "Green Bay Packers", "opponent": "Chicago Bears", "date": "2024-09-10", "time": "16:25", "network": "FOX"},
    {"team": "Green Bay Packers", "opponent": "Atlanta Falcons", "date": "2024-09-17", "time": "13:00", "network": "FOX"},
    {"team": "Green Bay Packers", "opponent": "New Orleans Saints", "date": "2024-09-24", "time": "13:00", "network": "FOX"},
    {"team": "Green Bay Packers", "opponent": "Detroit Lions", "date": "2024-09-24", "time": "20:15", "network": "Prime Video"},
    {"team": "Green Bay Packers", "opponent": "Las Vegas Raiders", "date": "2024-10-08", "time": "20:15", "network": "ESPN"}
]

# Add events to the calendar
for game in games:
    create_game_event(game["team"], game["opponent"], game["date"], game["time"], game["network"])

# Save the calendar to a file
with open("C:/Users/logan/Desktop/lions_packers_schedule.ics", "w") as f:
    f.writelines(cal)
