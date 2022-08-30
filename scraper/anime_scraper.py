
from cgi import print_form
from gettext import find
from pickle import NONE
import requests
from bs4 import BeautifulSoup
import pandas as pd
from configparser import ConfigParser
from datetime import datetime
import logging

def find_seasonal_anime_urls():
    html_text = requests.get('https://myanimelist.net/anime/season').text
    soup = BeautifulSoup(html_text, 'lxml')
    seasonal_list = soup.find_all('div', class_ = 'js-anime-category-producer seasonal-anime js-seasonal-anime js-anime-type-all js-anime-type-1')
    links = []
    for anime in seasonal_list:
        anime_link = anime.find('h2', class_ = 'h2_anime_title')
        link = anime_link.find('a', href=True)
        links.append(link['href'])

    return links

def get_all_anime(links):
    animes = []
    for link in links:
        animes.append(get_anime(link))

    return animes

def get_anime(link):
     html_text = requests.get(link).text
     logging.info(link)
     soup = BeautifulSoup(html_text, 'lxml')
     
     titleElement = soup.find('div', itemprop='name')
     title = titleElement.text

     englishTitle = titleElement.find('p', class_ = 'title-english title-inherit')
     if not englishTitle:
         englishTitle = ''
     else:
        englishTitle = englishTitle.text

     animeInfo = soup.find('div', class_='leftside')

     episodes_label = animeInfo.find('span', string='Episodes:')
     episodes_text = episodes_label.next_sibling.strip()

     type_label_parent = animeInfo.find('span', string='Type:').parent
     type = type_label_parent.find('a').text

     broadcast_label = animeInfo.find('span', string='Broadcast:')
     broadcast_text = broadcast_label.next_sibling.strip() if broadcast_label else ""
     
     status_label = animeInfo.find('span', string='Status:')
     status_text = status_label.next_sibling.strip()

     anime = Anime(title, englishTitle, episodes_text,broadcast_text, type, status_text)
     
     return anime

class Anime:

    def __init__(self, title, eng_title, episodes, broadcast, type, status):
        self.title = title
        self.english_title = eng_title
        self.episodes = episodes if episodes.isdigit() else None
        date_time = self.parse_broadcast_date(broadcast)
        self.broadcast_day = date_time[0]
        self.broadcast_time = date_time[1]
        self.media_genre = type
        self.status = status

    def print(self):
        logging.info(f'Title: {self.title}')
        logging.info(f'English Title: {self.english_title}')
        logging.info(f'Episodes: {self.episodes}')
        logging.info(f'BroadcastDay: {self.broadcast_day}')
        logging.info(f'BroadcastTime: {self.broadcast_time}')
        logging.info(f'Type: {self.media_genre}')
        logging.info(f'Status: {self.status}')

    def parse_broadcast_date(self, date):
      if date.lower() == 'unknown' or date == "":
        return None, None

      list = date.split()
      day = list[0]
      time = list[2]

      try:
        datetime.strptime(time, '%H:%M')
        return day, time
      except ValueError:
        return None, None

     
def get_season_anime(season, year):
   anime_links = find_seasonal_anime_urls()
   animes = get_all_anime(anime_links)
   return animes


def get_current_season_anime():
   anime_links = find_seasonal_anime_urls()
   animes = get_all_anime(anime_links)
   return animes