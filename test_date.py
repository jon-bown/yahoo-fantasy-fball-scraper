from datetime import datetime

def get_next_nfl_week(current_week: int) -> int:
    return current_week + 1

def get_current_nfl_week(start_date: datetime, current_date: datetime) -> int:
    # Calculate the number of days since the start of the season
    days_since_start = (current_date - start_date).days
    # Assuming each NFL week is 7 days long
    return days_since_start // 7 + 1

# NFL season start date (example: start of the 2024 season)
season_start_date = datetime(2024, 9, 5)  # Adjust the date accordingly
current_date = datetime.now()

# Get the current NFL week
current_nfl_week = get_current_nfl_week(season_start_date, current_date)

# Calculate the next NFL week
next_nfl_week = get_next_nfl_week(current_nfl_week)

print(f"Current NFL Week: {current_nfl_week}")
print(f"Next NFL Week: {next_nfl_week}")