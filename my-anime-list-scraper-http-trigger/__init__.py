import logging
from scraper import anime_scraper
import os
import pyodbc
import azure.functions as func

from configparser import ConfigParser


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    config = ConfigParser()

    server = os.environ["ANIME-SCRAPER-SERVER"]
    database = os.environ["ANIME-SCRAPER-DATABASE"]
    username = os.environ["DB-USERNAME"]
    password = os.environ["DB-PASSWORD"]

    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;'

    try:
        conn = pyodbc.connect(connection_string)
    except:
        logging.info('Failed to connect to database')
        return func.HttpResponse(status_code=500)

    logging.info('Getting anime')

    animes = []
    if True:
        animes = anime_scraper.get_current_season_anime()
    else: # TODO: Add seasons and years in body
        animes = anime_scraper.get_seasonal_anime(season, year)

    cursor = conn.cursor()
    
    logging.info('Start Inserting')
    for anime in animes:
        logging.info(f'Inserting {anime.title}')
        cursor.execute("SELECT title FROM Anime WHERE title = ?", (anime.title))
        exist = cursor.fetchall()
        if len(exist)==0:
              cursor.execute(f'insert into Anime (Title, EnglishTitle, Episode, MediaGenre, Status, BroadcastDay, BroadcastDay) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (anime.title, anime.english_title, anime.episodes, anime.media_genre, anime.status, anime.broadcast_day, anime.broadcast_time))
              logging.info('Adding new anime')
        else:
            cursor.execute(f'UPDATE Anime SET BroadcastDay = ?, BroadcastTime= ? WHERE Title = ?;', (anime.broadcast_day, anime.broadcast_time, anime.title))
            logging.info('Updating anime')
    conn.commit()

    logging.info('Success')
    return func.HttpResponse(status_code=200)
