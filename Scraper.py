# Scraper Class
# scraps fbref.com to get matches info either by league or by country
# Leagues Supported:
# Serie A, La Liga, Premier League, Ligue 1, Bundesliga
# Countries Supported:
# Italy, Spain, France, Germany, England

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
from colorama import init

fbref_url = 'https://fbref.com/en/matches/'
class Scraper:
    # init the scraper object
    def __init__(self, args):
        self.date = args.date
        self.request = requests.get(fbref_url + self.date)
        self.soup = BeautifulSoup(self.request.content, 'lxml')
        self.leagues = args.league
        self.countries = args.country
        self.searchmethod = "all" if args.all else "league" if len(self.countries) == 0 else "country"
        self.CountriesLeagues = {}
    
    # parse leagues names
    def parseLeagues(self):
        for i in range(len(self.leagues)):
            if "Serie" == self.leagues[i]:
                self.leagues[i] = "Serie A"
            elif "Liga" == self.leagues[i]:
                self.leagues[i] = "La Liga"
            elif "ligue" == self.leagues[i]:
                self.leagues[i] = "Ligue 1"
            elif "Premier" == self.leagues[i]:
                self.leagues[i] = "Premier League"
            elif "bundesliga" == self.leagues[i]:
                self.leagues[i] = "Bundesliga"

    # parse countries names
    def parseCountries(self):
        for i in range(len(self.countries)):
            if "England" == self.countries[i]:
                self.countries[i] = "eng"
            elif "Italy" == self.countries[i]:
                self.countries[i] = "it"
            elif "Spain" == self.countries[i]:
                self.countries[i] = "es"
            elif "France" == self.countries[i]:
                self.countries[i] = "fr"
            elif "Germany" == self.countries[i]:
                self.countries[i] = "de"
    
    # in case of search by country, map all the leagues to their countries
    def getCountriesLeagues(self):
        self.parseCountries()
        main = self.soup.find_all("div", class_= lambda text: False if text is None else "table_wrapper" in text.lower())
        self.CountriesLeagues = {country: [] for country in self.countries}
        for country in self.countries:
            for row in main:
                tags = row.find("h2").find_all("span", class_= lambda text: False if text is None else "f-i" in text.lower())
                for tag in tags:
                    if tag.text == country:
                        self.CountriesLeagues[country].append(row)


    # get the details of the matches
    def get_matches_info(self, matches):
        for i, match in enumerate(matches, 0):
            match_details = match.find("td")
            for match_details in match:
                if match_details['data-stat'] == "home_team":
                    HomeTeam = match_details.find('a').text
                elif match_details['data-stat'] == "away_team":
                    AwayTeam = match_details.find('a').text
                elif match_details['data-stat'] == "score":
                    PossibleScore = match_details.find('a')
                    Score = "" if PossibleScore is None else PossibleScore.text
                elif match_details['data-stat'] == "start_time":
                    Time = match_details.find_all("span", class_="venuetime")[0].text
                elif match_details['data-stat'] == "notes":
                    try:
                        Notes = match_details.text
                    except:
                        Notes = ""
            print(str(i+1) + ") " + HomeTeam + " vs " + AwayTeam + " " + Fore.GREEN + Score)
            print(Time)
            if Notes != "":
                print(Fore.RED + Notes)
            if i != len(matches)-1:
                print("-"*15)

    # get matches by country 
    def get_matches_info_by_country(self):
        self.getCountriesLeagues()
        print("-"*15)
        for j, country in enumerate(self.CountriesLeagues, 0):
            if len(self.CountriesLeagues[country]) == 0:
                print(Fore.RED + f"No matches found on {self.date} for " + country)
                continue
            if j != 0:
                print()
            print(Fore.RED + country)
            print("-"*15)
            for i, league in enumerate(self.CountriesLeagues[country], 0):
                league_title = league.find('a')
                print(Fore.CYAN + league_title.text)
                print("-"*15)
                matches = league.find_all("tr")
                matches.pop(0)
                self.get_matches_info(matches)
                if i != len(self.CountriesLeagues[country])-1:
                    print("") # seperate between leagues and cups
            if j != len(self.CountriesLeagues)-1:
                print("-"*15) # seperate between countries

    # get matches by league    
    def get_matches_info_by_league(self):
        body = self.soup.find_all("div", class_= lambda text: False if text is None else "table_wrapper" in text.lower())
        self.parseLeagues()
        # get the data of each league
        for row in body:
            league_title = row.find('a')
            if league_title.text in self.leagues or self.searchmethod == "all":
                print(Fore.CYAN + league_title.text)
                print("-"*15)
                matches = row.find_all("tr")
                matches.pop(0) # keys row
                self.get_matches_info(matches)
                print()
    
    # main function
    def run(self):
        init(autoreset=True)
        if self.searchmethod == "league" or self.searchmethod == "all":
            self.get_matches_info_by_league()
        else:
            self.get_matches_info_by_country()
