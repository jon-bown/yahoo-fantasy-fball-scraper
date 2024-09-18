#!/usr/bin/python3
__author__ = 'agoss'

import argparse
from datetime import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import helper


def init_config():
    start = time.time()
    arg_list = get_arg_list()
    return start, arg_list


# Listing the arguments that can be passed in though the command line
def get_arg_list():
    parser = argparse.ArgumentParser(description='Parses command line arguments')
    parser.add_argument('--yahoo_email', type=str, required=True, help='Yahoo email address for account login.')
    parser.add_argument('--yahoo_pw', type=str, required=True, help='Password for Yahoo account login.')
    parser.add_argument('--yahoo_league_id', type=str, required=True, help='ID associated with Yahoo '
                                                                           'fantasy football league.')
    return parser.parse_args()


def write_player_record_to_csv(csv_extract, player_details, player_status, player_projections):
    csv_contents = '\n' + player_details[0] + '{0}' + player_details[1] + '{0}' + player_details[2] + '{0}' + player_status + '{0}'
    for player_projection in player_projections:
        csv_contents = csv_contents + player_projection + '{0}'
    with open(csv_extract, 'a', encoding='utf-8') as output_file:
        output_file.write(csv_contents.format(',')[:-1])


def main():
    start, args = init_config()
    print('Program started\n**************START**************\n')

    #GET NFL WEEK
    # NFL season start date (example: start of the 2024 season)
    season_start_date = datetime(2024, 9, 5)  # Adjust the date accordingly
    current_date = datetime.now()
    # Get the current NFL week
    current_nfl_week = helper.get_current_nfl_week(season_start_date, current_date)
    # Calculate the next NFL week
    next_nfl_week = helper.get_next_nfl_week(current_nfl_week)

    csv_extract = datetime.now().strftime('%Y_%m_%d_') + f'yahoo_player_week_{next_nfl_week}_projections.csv'
    # Create output file headers
    with open(csv_extract, 'x', encoding='utf-8') as output_file:
        output_file.write(
            'PLAYER_NAME,TEAM,POSITION,PLAYER_STATUS,GP*,BYE,FANTASY_POINTS,PRESEASON_RANKING,ACTUAL_RANKING,PCT_ROSTERED,PASSING_YDS,'
            'PASSING_TD,PASSING_INT,RUSHING_ATT,RUSHING_YDS,RUSHING_TD,RECEPTIONS,RECEIVING_YDS,RECEIVING_TD,TARGETS,RET_TD,'
            '2PT_CONVERSIONS,FUMBLES_LOST')

    # Remotely control safari web browser
    browser = webdriver.Safari()
    browser = helper.yahoo_account_login(args.yahoo_email, args.yahoo_pw, browser)
    wait = WebDriverWait(browser, 30)  # Wait for up to 15 seconds

    # Cycle through player data and extract season-long projections
    print('Extracting Yahoo! fantasy football player season projections...')
    pagination = 0  # Initialize at player 0
    while pagination <= 275:  # Last page begins at player 275, extract top 300 player projections by points
        browser.get(f'https://football.fantasysports.yahoo.com/f1/{args.yahoo_league_id}/players?&sort=PTS&sdir=1&status=A'
                    f'&pos=O&stat1=S_PW_{next_nfl_week}&count={str(pagination)}')
        # Extract data from first web page table
        tables = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Table')))
        #tables = browser.find_elements(By.CLASS_NAME, 'Table')
        table_data = tables[0].get_attribute('innerText')
        table_rows = table_data.splitlines()
        del table_rows[:35]  # Remove header rows
        del table_rows[0]  # Remove first row
        del table_rows[0]  # Remove second row

        # Initialize variables
        i = 0
        player_details = []
        player_status = 'A'  # Player without a status has a null record, so default to 'A' (Active/Available)
        player_projections = []

        # Parse records and write to output file
        for table_row in table_rows:
            if i == 0:  # Capture player name from record
                player_details.append(table_row)
                i += 1
                continue
            if i == 1:  # Capture team and position from record
                team_pos = table_row.split(' ')
                player_details.append(team_pos[0])  # NFL team
                player_details.append(team_pos[2])  # Position
                print(f'{player_details[0]} - {player_details[2]} - {player_details[1]}')
                i += 1
                continue
            # Handle other player statuses
            if table_row.lower() in ('ir', 'nfi-r', 'nfi-a', 'o', 'pup', 'pup-p', 'd', 'na', 'p', 'q', 'susp'):
                player_status = table_row
                continue
            if i in (2, 3, 4, 5):  # Skip specific unused record using iterator
                i += 1
                continue
            if table_row.lower() == '':  # Write current player projections and advance to next player
                write_player_record_to_csv(csv_extract, player_details, player_status, player_projections)
                # Reset variables
                i = 0
                player_details = []
                player_status = 'A'
                player_projections = []
                continue
            # Store player projection figures in list
            player_projections.append(table_row)
            i += 1
            continue

        write_player_record_to_csv(csv_extract, player_details, player_status, player_projections)  # Write final page record
        pagination += 25  # Paginate to the next 25 players

    end = time.time()
    print('Program finished\n\n**************DONE**************\n' + 'Time elapsed: ' + str(end - start) + '\n')


if __name__ == '__main__':
    try:
        main()
    except RuntimeError as err:
        raise err
