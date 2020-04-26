from secrets import *
import tweepy
import requests
import os, sys, time
import json
import logging
from bs4 import BeautifulSoup as bs
from termcolor import colored
from lxml import etree, html
from scrapy.selector import Selector
from time import strftime, gmtime
import difflib

bot_username = 'Next Match BOT'
logfile_name = bot_username.lower().replace(" ", "_") + ".log"
hltv = "https://www.hltv.org/"
team_list = ['natus vincere', 'mousesports', 'mibr', 'faze', 'g2', 'bad news bears', 'astralis', 'fnatic']

def log(message):
    """Log message to logfile."""
    path = os.path.realpath(os.getcwd())
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)


def search_team(team_name):
    search_page_link = hltv + "search?query={}".format(team_name)
    soup = bs(requests.get(search_page_link).text, 'html.parser')
    links_with_text = []
    for a in soup.find_all('a', href=True): 
        if a.text and a['href'].startswith('/team/'):
            links_with_text.append(a['href'])
    first_result = links_with_text[0]
    return  hltv + first_result[1:]

def get_team_next_match(team_page):
    matches_page = team_page + '#tab-matchesBox'
    matches_page_html = requests.get(matches_page).text
    scrapy_page = Selector(text=matches_page_html)
    team_name = scrapy_page.xpath('//*[@id="matchesBox"]/table[1]/tbody[1]/tr[1]/td[2]/div[3]/div/img/@alt').get()
    match_page = hltv + scrapy_page.xpath('//*[@id="matchesBox"]/table[1]/tbody[1]/tr[1]/td[3]/a/@href').get()[1:]
    event_name = scrapy_page.xpath('//*[@id="matchesBox"]/table[1]/thead[2]/tr/th/text()').get()
    
    return team_name, match_page, event_name

def get_time_countdown(match_page):
    match_page_html = requests.get(match_page).text
    scrapy_page = Selector(text=match_page_html)
    count_down = scrapy_page.xpath('/html/body/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div[5]/text()').get()
    return count_down

def create_api():
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
    wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        log(e.message)
        raise e
    print('API '+ colored('created', 'green'))
    return api

def get_similarity(meant_word, word, dic):
    ratio = difflib.SequenceMatcher(None, meant_word, word).ratio()
    dic.update({word: ratio})
    return dic

def process_tweet_text(tweet_text, team_list):
    # remove mentions:
    list_of_words = [word for word in tweet_text.split() if not word.startswith('@')]
    # let's assume that the first word is meant to be the team name
    meant_team_name = list_of_words[0].lower()
    dic = {}
    for team_name in team_list:
        dic = get_similarity(meant_team_name, team_name, dic)
    nearest_team = max(dic, key=dic.get)
    return nearest_team


def create_tweet(team_name):
    """Create the text of the tweet you want to send."""
    team_page = search_team(team_name)
    adversary_team, match_page, event_name = get_team_next_match(team_page)
    count_down = get_time_countdown(match_page)
    text = "Next match of {}: vs {} in {} for {}. More info: {}".format(
        team_name, adversary_team, count_down, event_name, match_page)
    return text


def check_mentions(api, since_id, team_list):
    log("Procurando menções...")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        log("Menção encontrada de @{}".format(tweet.user.screen_name))
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            log(f"Respondendo {tweet.user.name}...")
            continue

        tweet_content = process_tweet_text(tweet.text.lower(), team_list)
        tweet_answer = create_tweet(tweet_content)
        tweet_answer = "@{} ".format(tweet.user.screen_name) + tweet_answer
        
        api.update_status(
            status=tweet_answer,
            in_reply_to_status_id=tweet.id,
            )
        if not tweet.user.following:
            log("Seguindo @{}".format(tweet.user.screen_name))
            tweet.user.follow()

    return new_since_id

def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = check_mentions(api, since_id, team_list)
        print(colored("Rodando...", 'green'))
        time.sleep(60)

main()