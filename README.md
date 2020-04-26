# hltv-next-match
## NOTE: This project was discontinued due to corporyght guidelines of HLTV.org.
Twitter BOT wrote in Python to get next match of certain team on HLTV.org.
Log file wrote in "PT_BR".

## TODO:
- insert get_team_list() function to get a team list

## Dependencies:
- tweepy
- requests
- os, sys, time, colored, json, logging
- BeautifulSoup, lxml, scrapy]
- difflib

## Funcionalities:
- reply someone's mention with the next match of the team (supposed to be the first word after the mention)
- follow everyone that mentions it

## How to use:
- create a secrets.py script with auth keys of your Twitter application
- run main()

## User usage:
- mention your BOT in Twitter with the team name
- example: "@HLTVnextmatch mibr"
- tweets back: "@user Next match of mibr: vs Bad News Bears in 2d : 23h : 2m : 6s for ESL One: Road to Rio - North America. More info: https://hltv.org/matches/2340933/bad-news-bears-vs-mibr-esl-one-road-to-rio-north-america"
