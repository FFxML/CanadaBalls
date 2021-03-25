#!/usr/bin/env python
# coding: utf-8

# ## FFxML Toolbox

# In[7]:


# Required input variables for the master script

# Global variables
# leagueID = '6787729' #input("Enter League ID: ")
# league_name = 'CanadianBallsRBigger'#input ("League Name: ")
# season = '2019'#input("Season: ")
# pos = {'QB':1,'RB':2,'WR':3,'TE':1,'K':1,'DEF':1,'Flex':1,'BN':5,'RES':2}


## Get league data
# leagueID = '6787729' #input("Enter League ID: ")
# league_name = 'CanadianBallsRBigger'#input ("League Name: ")
# season = '2019'#input("Season: ")

## Ball Wrangling
# pos = ['QB','RB','WR','TE','R/W/T','K','DEF','BN','RES']

## Transaction Soup
# leagueID = '6787729' #input("Enter League ID: ")
# league_name = 'CanadianBallsRBigger'#input ("League Name: ")
# season = '2019'#input("Season: ")
# ownerDict

## OBrienOMatic
# pos = {'QB':1,'RB':2,'WR':3,'TE':1,'K':1,'DEF':1}
# flex = ['RB','WR','TE']


# In[8]:


# workflow
# 1. Collect and organize web data
## a) GetLeagueData
## b) BallWrangling
# 2. Make the transaction table
## a) TransactionSoup
# 3. Get the draft data
## a) DraftSoup
# 4. Evaluating trades
## a) TradeEvaluator
# 5. Waiver Wire Performance
## a) PointsPer
# . Check for the coaching performance
## a) OBrienOMatic
## b) OBrienPoints


# In[12]:


from sklearn.ensemble import RandomForestClassifier


# In[10]:


# Required Modules
# GetLeagueData
import csv
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import re

# BallWrangling / OBrienOMatic
import os
import pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob

# Transaction Soup
import datetime

# TradeEvaluator / DraftSoup / DraftOutcomes
from difflib import get_close_matches


# In[2]:


# default variables
TeamDict = dict({
    'ARI':'Arizona Cardinals',
    'ATL':'Atlanta Falcons',
    'BAL':'Baltimore Ravens',
    'BUF':'Buffalo Bills',
    'CAR':'Carolina Panthers',
    'CHI':'Chicago Bears',
    'CIN':'Cincinnati Bengals',
    'CLE':'Cleveland Browns',
    'DAL':'Dallas Cowboys',
    'DEN':'Denver Broncos',
    'DET':'Detroit Lions',
    'GB':'Green Bay Packers',
    'HOU':'Houston Texans',
    'IND':'Indianapolis Colts',
    'JAX':'Jacksonville Jaguars',
    'KC':'Kansas City Chiefs',
    'LAC':'Los Angeles Chargers',
    'LA':'Los Angeles Rams',
    'LV':'Las Vegas Raiders',
    'MIA':'Miami Dolphins',
    'MIN':'Minnesota Vikings',
    'NE':'New England Patriots',
    'NO':'New Orleans Saints',
    'NYG':'New York Giants',
    'NYJ':'New York Jets',
    'PHI':'Philadelphia Eagles',
    'PIT':'Pittsburgh Steelers',
    'SF':'San Francisco 49ers',
    'SEA':'Seattle Seahawks',
    'TB':'Tampa Bay Buccaneers',
    'WAS':'Washington Football Team'})
TeamDict_Rev = {value:key for (key,value) in TeamDict.items()}


# In[13]:


# Get the league data (completed locked)
def GetLeagueData(leagueID, league_name, season):
    '''
    "So you've admitted to yourself that you don't really know football and 
    now you're looking for a different edge..."
    
    A downloader of league data from NFL Fantasy Football. This function will 
    download each week of player points as individual CSVs and save them to a directory. 
    Your league must be made publicly visible.
    -----------
    Parameters
    ----------- 
    leagueID: str
        Find the league ID in the URL of your league
        i.e. fantasy.nfl.com/league/*leagueID*
    
    league_name: str
        Decide what you want to name the directory where the league data will be stored
        
    season: str
        Which season's data are you collecting? Written as the first year in the season's calendar
        i.e. the 2020-2021 season would be 2020
    
    '''
    number_of_owners = get_numberofowners() #number of teams in the league

    #checks if a directory exists with that team name. If it doesn't it asks the user if it wants to create a new directory
    #to store the league data in.
    if not os.path.isdir('./' + league_name + '-League-History') :
        if(input('No folder named ' + league_name + '-League-History found would you like to create a new folder with that name y/n?' ) == 'y') :
            os.mkdir('./' + league_name + '-League-History')
        else :
            exit()

    path = './' + league_name + '-League-History/' + season #the path of the folder where the weekly csv files are stored

    #if that folder doesn't already exist a new one is made
    if not os.path.isdir(path) :
        os.mkdir(path)

    #if input("Write season data to csv y/n?") == 'y' :
    print(season)
    page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=1&week=1')
    soup = bs(page.read(), 'html.parser')
    page.close()
    season_length = len(soup.find_all('li', class_ = re.compile('ww ww-'))) #determines how may unique csv files are created, total number of weeks in the season 

    for i in range(1, season_length + 1): #iterates through each week of the season, creating a new csv file every loop
        longest_bench = get_longest_bench(i) #a list containing the length of the longest bench followed by the ID of the team with the longest bench
        header = get_header(i, longest_bench[1]) #header for the csv
        with open('./' + league_name +'-League-History/' + season + '/' + str(i) + '.csv', 'w', newline='') as f :
            writer = csv.writer(f)
            writer.writerow(header) #writes header as the first line in the new csv file
            for j in range(1, number_of_owners + 1) : #iterates through every team owner
                writer.writerow(getrow(str(j), str(i), longest_bench[0])) #writes a row for each owner in the csv
        print("Week " + str(i) + " Complete")
    print("Done")

#gets the total numver of players in a given season
def get_numberofowners() :
    owners_url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
    owners_page = urlopen(owners_url)
    owners_html = owners_page.read()
    owners_page.close()
    owners_soup = bs(owners_html, 'html.parser')
    number_of_owners = len(owners_soup.find_all('tr', class_ = re.compile('team-')))
    return number_of_owners


#gets the team id number from a player name, currently unused
def getteamid(player) :
    url = 'https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/owners'
    page = urlopen(url)
    html = page.read()
    page.close()
    soup = bs(html, 'html.parser')
    teamWraps = soup.find_all('tr', class_ = re.compile('team-'))
    for teamWrap in teamWraps :
        if teamWrap.find('td', class_ = 'teamOwnerName').text.strip() == player :
            return teamWrap.attrs['class'][0].split('-')[1]

#teams that don't fill all their starting roster spots for a week will have a longer bench
#the more roster spots left unfilled, the more bench players that team will have
#this method gets the teamid of the team with the longest bench for the week as well as the length of their bench
def get_longest_bench(week) :
    longest_bench_data = [0, 0]
    for i in range (1, number_of_owners + 1) :
        page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + str(i) + '&week=' + str(week))
        soup = bs(page.read(), 'html.parser')
        page.close()
        bench_length = len(soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo'))
        if(bench_length > longest_bench_data[0]) :
            longest_bench_data = [bench_length, i]

    return longest_bench_data

#generates the header for the csv file for the week
#different weeks can have different headers if players do not fill all their starting roster spots
def get_header(week, longest_bench_teamID) :
    url = "https://fantasy.nfl.com/league/" + leagueID + "/history/" + season + "/teamgamecenter?teamId=" +str(longest_bench_teamID) + "&week=" + str(week)
    page = urlopen(url)
    html = page.read()
    page.close()
    soup = bs(html, 'html.parser') #uses the page of the teamID with the longest bench to generate the header

    position_tags = [tag.find('span').text for tag in soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('tr', class_ = re.compile('player-'))]
    #position tags are the label for each starting roster spot. different leagues can have different configurations for their starting rosters

    header = [] #csv file header

    #adds the position tags to the header. each tag is followed by a column to record the player's points for the week
    for i in range(len(position_tags)) :
        header.append(position_tags[i])
        header.append('Points')

    header = ['Owner',  'Rank'] + header + ['Total', 'Opponent', 'Opponent Total']

    return header

#gets one row of the csv file
#each row is the weekly data for one team in the league
def getrow(teamId, week, longest_bench) : 

    #loads gamecenter page as soup
    page = urlopen('https://fantasy.nfl.com/league/' + leagueID + '/history/' + season + '/teamgamecenter?teamId=' + teamId + '&week=' + week)
    soup = bs(page.read(), 'html.parser')
    page.close()

    owner = soup.find('a', class_ = re.compile('userName userId')).text #username of the team owner

    starters = soup.find('div', id = 'tableWrap-1').find_all('td', class_ = 'playerNameAndInfo')
    starters = [starter.text for starter in starters]
    bench = soup.find('div', id = 'tableWrapBN-1').find_all('td', class_ = 'playerNameAndInfo')
    bench = [benchplayer.text for benchplayer in bench]

    #in order to keep the row properly aligned, bench spots that are filled by another team
    #but not by this team are filled with a -
    while len(bench) < longest_bench: 
        bench.append('-')

    roster = starters + bench #every player on the team roster, in the order they are listed in game center, for the given week

    player_totals = soup.find('div', id = 'teamMatchupBoxScore').find('div', class_ = 'teamWrap teamWrap-1').find_all('td', class_ = re.compile("statTotal"))
    player_totals = [player.text for player in player_totals] #point totals for each player with indecies which correspond to that player's index in roster

    teamtotals = soup.findAll('div', class_ = re.compile('teamTotal teamId-')) #the team's total points for the week
    ranktext = soup.find('span', class_ = re.compile('teamRank teamId-')).text
    rank = ranktext[ranktext.index('(') + 1: ranktext.index(')')]#the team's rank in the standings

    rosterandtotals = [] #alternating player names and their corresponding weekly point totals
    for i in range(len(roster)) :
         rosterandtotals.append(roster[i])

         #checks if there is a point total coressponding to the player, if not that spot is filled with a -
         try:
            rosterandtotals.append(player_totals[i])
         except:
            rosterandtotals.append('-')

    #try except statement is for the situation where the league member would not have an opponent for the week
    #in this case the Opponent and Opponent Total columns are filled with -
    try:
        completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, soup.find('div', class_ = 'teamWrap teamWrap-2').find('a', re.compile('userName userId')).text, teamtotals[1].text]
    except:
        completed_row = [owner, rank] + rosterandtotals + [teamtotals[0].text, '-', '-']

    return completed_row


# In[6]:


# Ball Wrangling
def BallWrangling(league_name, season, pos):
    '''
    "This here function will wrangle them balls" - Jake Vogel
    
    This function will organize the CSVs created by GetLeagueData into two player dataframes containing the points, owners, transaction status, roster status, position, and team
    
    -----------
    Parameters
    -----------
    league_name: str
        Decide what you want to name the directory where the league data will be stored
        
    season: str
        Which season's data are you collecting? Written as the first year in the season's calendar
        i.e. the 2020-2021 season would be 2020
    
    pos: dictionary
        Construct a dictionary containing the number of positions available in your league
        Ex: {'QB':1,'RB':2,'WR':3,'TE':1,'K':1,'DEF':1,'Flex':1,'BN':5,'RES':2}
    
    -------
    Outputs
    -------
    output1 : dataframe
        Dataframe organized with the status of a player in a single week captured on a row, then repeated for all weeks of the season, with points, owners, roster status, transaction status, and roster status on the columns
    
    output2 : dataframe
        Dataframe organized by players on the rows with points, owners, roster status, transaction status, and roster status for each week on the columns

    '''
    wdfs = sorted(glob(league_name + '-League-History/' + season+ '/*.csv'))
    player = pandas.DataFrame() # collect the results long form
    tplayer = pandas.DataFrame() # collect the results tall form
    count = 0
    
    # have to rename the flex entry because the raw data uses 'R/W/T'
    poslist = list(pos)
    poslist = ['R/W/T' if x=='Flex' else x for x in poslist]

    # iterate through week dataframes
    for wdf in wdfs:
        # get the week number
        pth,flnm = os.path.split(wdf)
        week = '%0.2d'%int(flnm.split('.')[0])
        # read data
        data = pandas.read_csv(wdf)
        for i,row in data.iterrows():
            # get basic player information
            owner = row['Owner']
            for col in row.index:
                # only columns that have players in them
                if any([x in col for x in poslist]):
                    # ignore if slot is empty
                    if row[col] == '-' or row[col] == "--empty--": 
                        continue
                    # defense are weird so deal w/ non defense first
                    if 'DEF' not in row[col]:
                        # get player info
                        info = row[col].split()
                        p_name = '%s, %s'%(info[1],info[0])
                        ppos = info[2]
                        if len(info) == 3: # i.e. if not on team
                            pteam = 'Free Agent'
                        else:
                            pteam = info[4]
                        # this will be the index because guaranteed to be unique
                        pstr = '%s %s %s'%(p_name,ppos,pteam)
                    # now deal w defenses
                    elif 'DEF' in row[col]: 
                        p_name = row[col]
                        ppos = row[col].split()[-1]
                        # deal with WFT
                        pteam = ''
                        for x in row[col].split()[:-1]:
                            pteam = pteam.join(x)
                        # this will be the index because guaranteed to be unique
                        pstr = row[col]

                    # get points for that week
                    nextcol = row.index.tolist().index(col)+1
                    points = row[nextcol]

                    # get status for that week
                    if 'BN' in col:
                        status = 'Inactive'
                        rstatus = 'Bench'
                    elif 'RES' in col:
                        status = 'Inactive'
                        rstatus = 'Reserve'
                    else:
                        status = 'Active'
                        rstatus = 'Starting'

                    ## Long form storing data
                    # if not already in spreadsheet
                    if pstr not in player.index.values:
                        # save basic info
                        player.loc[pstr,'name'] = p_name
                        player.loc[pstr,'position'] = ppos
                        player.loc[pstr,'team'] = pteam
                        player.loc[pstr,'first_owner'] = owner

                    # save weekly data (will make new column for each week)
                    player.loc[pstr,'Week%s_owner'%week] = owner
                    player.loc[pstr,'Week%s_points'%week] = points
                    player.loc[pstr,'Week%s_status'%week] = status
                    player.loc[pstr,'Week%s_RostStatus'%week] = rstatus

                    ## Tall form storing data
                    tplayer.loc[count,'name'] = p_name
                    tplayer.loc[count,'position'] = ppos
                    tplayer.loc[count,'team'] = pteam
                    tplayer.loc[count,'unique_str'] = pstr
                    tplayer.loc[count,'week'] = week
                    tplayer.loc[count,'owner'] = owner
                    tplayer.loc[count,'points'] = points
                    tplayer.loc[count,'status'] = status
                    tplayer.loc[count,'RostStatus'] = rstatus
                    count += 1

    # wide player df        
    ## Fill holes
    for i,row in player.iterrows():
        for col in player.columns:
            if '_status' in col and not pandas.notnull(row[col]):
                player.loc[i,col] = 'FA'
            elif '_RostStatus' in col and not pandas.notnull(row[col]):
                player.loc[i,col] = 'FA'
            elif '_owner' in col and not pandas.notnull(row[col]):
                player.loc[i,col] = 'FA'

    ## get transaction status
    owner_cols = [x for x in player.columns if '_owner' in x][1:]
    for i,row in player.iterrows():
        for c in range(len(owner_cols)):
            if c == 0:
                if row['Week01_owner'] == 'FA':
                    player.loc[i,'Week01_TransStatus'] = 'FA'
                else:
                    player.loc[i,'Week01_TransStatus'] = 'None'
            else:
                col = owner_cols[c]
                lastweek = owner_cols[c-1]
                week = col.split('_')[0].split('eek')[-1]
                if row[col] == row[lastweek]:
                    if row[col] == 'FA':
                        player.loc[i,'Week%s_TransStatus'%week] = 'FA'
                    else:
                        player.loc[i,'Week%s_TransStatus'%week] = 'None'
                elif row[col] == 'FA' and row[lastweek] != 'FA':
                    player.loc[i,'Week%s_TransStatus'%week] = 'Dropped'
                elif row[col] != 'FA' and row[lastweek] == 'FA':
                    player.loc[i,'Week%s_TransStatus'%week] = 'PickedUp'
                else:
                    player.loc[i,'Week%s_TransStatus'%week] = 'Traded'

    # tall player df
    vc = tplayer.unique_str.value_counts()
    need_to_fill = vc[vc<16].index

    pcols = tplayer.columns[:4]
    scols = ['owner','status','RostStatus']
    i = len(tplayer)
    allweeks = tplayer.week.unique()
    for pstr in need_to_fill:
        pdf = tplayer[tplayer.unique_str==pstr]
        missing_weeks = [x for x in allweeks if x not in pdf.week.values]
        for week in missing_weeks:
            tplayer.loc[i,pcols] = pdf.iloc[0][pcols].values
            tplayer.loc[i,'week'] = week
            tplayer.loc[i,scols] = 'FA'
            i += 1

    tplayer = tplayer.sort_index(axis=0)
    tplayer.points = pandas.to_numeric(tplayer.points)
    return tplayer, player


# In[4]:


# Transaction Soup
def transaction_soup_cleaner(df):
    trans = []
    row_marker = 0
    for row in df.find_all('tr'):
        #print(row_marker)
        column_marker = 0
        columns = row.find_all('td')
        col_data = []
        for column in columns:
            col_data.append(column.get_text())
            column_marker +=1
        trans.append(col_data)
        row_marker += 1

    return(trans)

def canadaschunkysoup(url, bowlsize):
    offset = 20
    counter = 0
    off_num = 0
    while bowlsize >= off_num:
        if counter == 0:
            page = urlopen(url)
        elif counter > 0:
            page = urlopen(url+'?offset='+str(off_num))
        html = page.read()
        page.close()
        canned = bs(html, 'html.parser') 
        soup = canned.find_all('table')[0]
        cleansoup = transaction_soup_cleaner(soup)
        if counter == 0: 
            soupbowl = cleansoup
        if counter > 0:
            soupbowl = soupbowl + cleansoup
        counter += 1
        off_num = (offset*counter)+1
    soupbowl = pandas.DataFrame(soupbowl)
    return soupbowl

def transaction_table_cleaner(df):
    df['Team'] = df.Player.str.split(pat = " - ", expand = False).str[1].str.split().str[0]
    df['Position'] = df.Player.str.split(pat = " - ", expand = False).str[0].str.split().str[-1]
    df['Player'] = df.Player.str.split(pat = " - ", expand = False).str[0].str.split().str[:-1].str.join(" ")
    return df

def transaction_trade_cleaner(df):
    # find trades with multiple players and split from single player trades
    # for multi player trades, duplicate the row
    multi = df.loc[df[df['Player'].str.count(" - ") > 1].index.repeat(2)]
    singles = df[(df['Player'].str.count(" - ") == 1)|(df['Player'].str.count(" - ") == 0)]
    for i in set(multi.index):
        # rewrite the top row with one player, and the bottom row with the other, NOTE: this only works with two players max
        multi.loc[i,'Player'].iloc[0] = multi.loc[i,'Player'].iloc[0].split(" - ")[0] +" - "+ multi.loc[i,'Player'].iloc[0].split(" - ")[1].split(" ")[0]
        multi.loc[i,'Player'].iloc[1] = " ".join(multi.loc[i,'Player'].iloc[1].split(" - ")[1].split(" ")[-3:]) +" - "+ multi.loc[i,'Player'].iloc[1].split(" - ")[2]
    df = pandas.concat([singles,multi],axis = 0).reset_index(drop = True)
    df = df.sort_values(by='Date')
    return(df)

def TransactionSoup(leagueID,season,bowlsize,FAAB=False):
    '''
    "Mats! It's time for your chunky soup! Mats, your mommy's calling" - The deep recesses of my mind, courtesy of 1990s advertising. 
    
    This function will collect the league transaction data from online, detailing all lineup changes, waiver or free agent adds and drops and trades. Your league must be publicly visible.
    
    -----------
    Parameters
    -----------
    leagueID: str
        Find the league ID in the URL of your league
        i.e. fantasy.nfl.com/league/*leagueID*
        
    season: str
        Which season's data are you collecting? Written as the first year in the season's calendar
        i.e. the 2020-2021 season would be 2020
    
    bowlsize: int
        You have to provide the number of transactions that existed, which can be found in the URL of your league transaction data once you navigate to the very first transaction. Each subsequent page increases the number in increments of 20 with the first number being 21, so hone in on the right number manually  
        Ex: https://canada.fantasy.nfl.com/league/*leagueID*/transactions?offset=*21* <- this number here
        
    FAAB: bool, default = False
        If your league used a Free Agent Action system, FAAB = True, and the Transaction Cost of each Waiver add will be included.
    
    -------
    Outputs
    -------
    output1 : dataframe
        Dataframe with the date and time of each transaction on the rows, and the week, transaction type, player info, transaction start and finish, the manager responsible, and transaction costs if necessary on the rows

    '''
    url = 'https://fantasy.nfl.com/league/'+leagueID+'/history/'+season+'/transactions'
    tables = canadaschunkysoup(url, bowlsize)
    tables.columns = ['Date','Week','TransType','Player','From','To','By']
    tables = tables[tables.TransType!='LM']
    tables = tables.dropna()
    
    # clean the trades
    trades = pandas.DataFrame(tables[tables['TransType'] == 'Trade'],copy = True)
    trades = transaction_table_cleaner(transaction_trade_cleaner(trades))
    
    # Clean the normal values
    Normal = pandas.DataFrame(tables[~((tables['TransType'] == 'Trade') | (tables.Player.str.contains('DEF')))], copy = True)
    Normal = transaction_table_cleaner(Normal)
    
    # Defenses 
    DEF = tables[tables.Player.str.contains('DEF')].copy()
    # split them via a similar method
    DEF['Position'] = DEF.Player.str.split(pat = " ", expand = False).str[-2]
    DEF['Team'] = DEF.Player.str.split(pat = " ", expand = False).str[:-2].str.join(" ")
    # remap the team names to be consistent
    DEF['Team'] = DEF['Team'].map(TeamDict_Rev)
    
    # create the master transaction table
    trans = pandas.concat([Normal,DEF,trades], axis = 0, ignore_index = True)
    trans = trans[['Date', 'Week', 'TransType', 'Player', 'Position', 'Team', 'From', 'To', 'By']]
    trans['Date'] = trans['Date'].apply(lambda x: datetime.datetime.strptime((season+' '+x),'%Y %b %d, %I:%M%p'))
    trans = trans.sort_values(by='Date').reset_index(drop = True)
    trans['Player'] = trans['Player'].str.strip()
    trans['Team'] = trans['Team'].str.strip()
    trans['Position'] = trans['Position'].str.strip()
    trans['By'] = trans.By.str.split(expand=False).str[0]
    trans.loc[trans['Team'].isna(),'Team'] = 'Free Agent'
    
    # FAAB calculations
    if FAAB == True:
        trans['TransCosts'] = trans['To'].str.split("(").str[1].str.split(")").str[0]
        trans['To'] = trans['To'].str.split("(").str[0].str.strip()
    
    return trans


# In[15]:


# The O'Brien-o-matic (completed locked)
def pot_points(data, pos, flex):
    idealteam =[]
    potpoints = 0
    # do the roster minus flex
    activepos = ['QB','RB','WR','TE','Flex','K','DEF']
    for p in pos:
        if p not in activepos:
            continue
        else:
            if p != 'Flex':
                # iso the players in the position
                players = data.loc[data['position'] == p,:]
                # pull the players with the maximum points
                maxinfo = players.nlargest(n = pos.get(p), columns='points')
                # add the max points to the sum
                potpoints = sum(maxinfo.points,potpoints)
                # add the players to the ideal roster
                idealteam.extend(maxinfo.name)
            elif p == 'Flex':
                # now do flex
                flexdata = data.loc[(~data['name'].isin(idealteam)) & (data['position'].isin(flex)),:]
                flexinfo = flexdata.nlargest(n = 1, columns='points')
                potpoints = sum(flexinfo.points,potpoints)
                idealteam.extend(flexinfo.name)
    # the option to output the ideal roster is saved for later
    missedchance = data.loc[data['name'].isin(idealteam),:]
    return potpoints

# iterate over the dataframe to calculate
def OBrienOMatic(playerdf, pos, flex = ['RB','WR','TE']):
    '''
    aka: The Marinelli Meter, Hue Jackson's Lake Erie Probability
    
    This function will calculate a coach's lineup decision making performance over the season vs their optimal potential lineups
    
    -----------
    Parameters
    -----------
    playerdf: dataframe
        Expects the output1 dataframe from BallWrangling
        
    pos: dictionary
        Construct a dictionary containing the number of positions available in your league
        Ex: {'QB':1,'RB':2,'WR':3,'TE':1,'K':1,'DEF':1,'Flex':1,'BN':5,'RES':2}
    
    flex: list, default = ['RB','WR','TE']
        A list of positions that can be used in the flex spot in your league
    
    -------
    Outputs
    -------
    output1: dataframe
        Dataframe with each owner by week on the rows, and their actual points earned, total points earned, and the difference on the columns
        -- output1.OBrienQuotient
            The calculated difference between actual and potential points earned

    '''
    points = pandas.DataFrame()
    weeks = set(playerdf['week'].values)
    owners = set(playerdf['owner'].values)
    owners.remove('FA')
    count = 0
    for week in weeks:
        for owner in owners:
            data = playerdf[(playerdf['week'] == week) & (playerdf['owner'] == owner)]
            points.loc[count,'week'] = week
            points.loc[count,'owners'] = owner
            points.loc[count,'actual points'] = sum(data.loc[data['status'] == 'Active','points'])
            points.loc[count,'potential points'] = pot_points(data, pos, flex)
            count += 1
    points['OBrien Quotient'] = points['actual points'] - points['potential points']
    points = points.sort_values(by=['week','owners'],axis = 0).reset_index(drop=True)
    return points

def OBrienPlot(OBrienPointsdf):
    '''
    "If you look at the chart here, we can see the week you thought Corey Davis was a good idea"
    
    -----------
    Parameters
    -----------
    OBrienPointsdf: dataframe
        Expects the output1 dataframe from OBrienOMatic
    
    -------
    Outputs
    -------
    output1: plot
        Plot showing the cumulative difference between actual points and potential points earned by each owner over the season

    '''
    pointsgraph = OBrienPointsdf.pivot("week","owners","OBrien Quotient")
    pointsgraph = pointsgraph.cumsum()
    plt.figure(figsize=(16,10))
    plt.title("Increasing O'Briens Over Time")
    sns.lineplot(data = pointsgraph)
    


# In[10]:


# Trades Evaluator

def traded_players(trades,player):
    unis = player.unique_str.unique()
    player.week = pandas.to_numeric(player.week)
    trades.Week = pandas.to_numeric(trades.Week)
    trades=trades.reset_index(drop=True)
    for i,row in trades.iterrows():
        pstr = get_unique_str(row)
        if pstr not in unis:
            match = get_close_matches(pstr,unis,cutoff=0.8)
            if len(match) > 0:
                pstr = match[0]
            else: 
                print('couldnt find a match for %s'%pstr)
                continue
        BeforeMask = (player['unique_str']==pstr) & (player['week']<row['Week']) & (player['owner']==row['From'])
        AfterMask = (player['unique_str']==pstr) & (player['week']>=row['Week']) & (player['owner']==row['To'])

        trades.loc[i,'Before'] = player.loc[BeforeMask,'points'].sum()
        trades.loc[i,'B_GamesOnTeam'] = BeforeMask.sum()
        trades.loc[i,'B_AvPoints'] = round((trades.loc[i,'Before'] / trades.loc[i,'B_GamesOnTeam']),2)
        trades.loc[i,'B_GamesStarted'] = len(player.loc[BeforeMask & (player['status']=='Active'),:])
        trades.loc[i,'B_%Started'] = len(player.loc[BeforeMask & (player['status']=='Active'),:])/row.Week

        trades.loc[i,'After'] = player.loc[AfterMask,'points'].sum()
        trades.loc[i,'A_GamesOnTeam'] = AfterMask.sum()
        trades.loc[i,'A_AvPoints'] = round((trades.loc[i,'After'] / trades.loc[i,'A_GamesOnTeam']),2)
        trades.loc[i,'A_GamesStarted'] = len(player.loc[AfterMask & (player['status']=='Active'),:])
        trades.loc[i,'A_%Started'] = len(player.loc[AfterMask & (player['status']=='Active'),:])/(17-row.Week)
    return trades


def get_unique_str(row):
    if row['Position'] == 'DEF':
        nsplit = row['Player'].split(' ')
        if 'Football Team' in row['Player']:
            pstr = '%s %s %s'%(nsplit[-3],nsplit[-2],nsplit[-1])
        else:
            pstr = '%s %s '%(nsplit[-2],nsplit[-1])
    else:
        nsplit = row['Player'].split(' ')
        name = ''
        for i in range(1,len(nsplit)):
            if i == len(nsplit)-1:
                name += '%s, '%nsplit[i]
            else:
                name += '%s '%nsplit[i]
        name += '%s.'%nsplit[0][0]
        pstr = '%s %s %s'%(name,row['Position'],row['Team'])
    
    return pstr

def TradeEvaluator(playerdf, transdf):
    '''
    "  "
    
    This function will evaluate the trades made over the season and determine which trades yielded the greatest increase in value
    
    -----------
    Parameters
    -----------
    playerdf: dataframe
        Expects the output1 dataframe from BallWrangling
    
    transdf: dataframe
        Expects the output1 dataframe from TransactionSoup
    
    -------
    Outputs
    -------
    output1: dataframe
        Dataframe displaying the calculated changes in value for each team after each trade
        -- output1.Improve?
            The average points gained or lost by the team after the trade
        -- output1.AtTheTime
            The average points earned by the traded players before the trade
        -- output1.%Started
            The percentage the traded players started for the receiving team
        -- output1.WeeksOnTeam
            The number of weeks the traded players stayed on the team
        
    '''
    tradecols = ['Date', 'Week', 'TransType', 'Player', 'Position', 'Team', 'From', 'To']
    trades = transdf.loc[transdf.TransType == 'Trade',tradecols]
    names = transdf.iloc[transdf.loc[transdf.TransType=='Add','To'].drop_duplicates().index]
    names = names.loc[:,['To','By']]
    names = names.set_index('To').to_dict()['By']
    trades.loc[:,'From'] = trades.loc[:,'From'].map(names)
    trades.loc[:,'To'] = trades.loc[:,'To'].map(names)
    trades = traded_players(trades,playerdf)
    
    tradelogA = pandas.DataFrame(columns = ['Date','GM','Improve?','AtTheTime','%Started'])
    tradelogB = pandas.DataFrame(columns = ['Date','GM','Improve?','AtTheTime','%Started'])
    for i,date in enumerate(set(trades.Date)):
        tradeIso = trades.loc[trades['Date']==date,:]
        tradelogA.loc[i,'Date'] = date
        tradelogB.loc[i,'Date'] = date
        GM1 = tradeIso.iloc[0]['From']
        GM2 = tradeIso.iloc[0]['To']
        tradelogA.loc[i,'GM'] = tradeIso.iloc[0]['From']
        tradelogB.loc[i,'GM'] = tradeIso.iloc[0]['To']
        # this is ugly af
        tradelogA.loc[i,'Improve?'] = (tradeIso.loc[tradeIso['To']==GM1,'A_AvPoints'].sum() - tradeIso.loc[tradeIso['From']==GM1,'A_AvPoints'].sum())
        tradelogA.loc[i,'AtTheTime'] = (tradeIso.loc[tradeIso['To']==GM1,'B_AvPoints'].sum() - tradeIso.loc[tradeIso['From']==GM1,'B_AvPoints'].sum())
        tradelogA.loc[i,'%Started'] = (tradeIso.loc[tradeIso['To']==GM1,'A_GamesStarted'].sum() / ((17-tradeIso.loc[tradeIso['To']==GM1,'Week'].iloc[0])*sum(tradeIso.To==GM1)))

        tradelogB.loc[i,'Improve?'] = (tradeIso.loc[tradeIso['To']==GM2,'A_AvPoints'].sum() - tradeIso.loc[tradeIso['From']==GM2,'A_AvPoints'].sum())
        tradelogB.loc[i,'AtTheTime'] = (tradeIso.loc[tradeIso['To']==GM2,'B_AvPoints'].sum() - tradeIso.loc[tradeIso['From']==GM2,'B_AvPoints'].sum())
        tradelogB.loc[i,'%Started'] = (tradeIso.loc[tradeIso['To']==GM2,'A_GamesStarted'].sum() / ((17-tradeIso.loc[tradeIso['To']==GM2,'Week'].iloc[0])*sum(tradeIso.To==GM2)))

    GMPerf = pandas.concat([tradelogA,tradelogB]).sort_values('Date').reset_index(drop = True)
    GMPerf[['Improve?','AtTheTime','%Started']] = GMPerf[['Improve?','AtTheTime','%Started']].astype(float)
    for i,row in GMPerf.iterrows():
        tradeIso = trades.loc[trades.Date == row['Date'],:]
        GMPerf.loc[i,'Sent'] = tradeIso.loc[tradeIso['From']==row['GM'],'Player'].str.cat(sep = ", ")
        GMPerf.loc[i,'Received'] = tradeIso.loc[tradeIso['To']==row['GM'],'Player'].str.cat(sep = ", ")
        GMPerf.loc[i,'WeeksOnTeam'] = 17-tradeIso['Week'].iloc[0]

    return GMPerf


# In[8]:


# Points Per Dollar Spent
def get_stint(pdf,owner):
    inds = []
    for i,row in pdf.iterrows():
        if row['owner'] == owner:
            inds.append(i)
        else:
            break
    return inds

def PointsPerDollar(playerdf,transdf):
    '''
    "  "
    
    This function evaluates which manager was the best at effectively using their FAAB budget to pick up players
    
    -----------
    Parameters
    -----------
    playerdf: dataframe
        Expects the output1 dataframe from BallWrangling
    
    transdf: dataframe
        Expects the output1 dataframe from TransactionSoup
    
    -------
    Outputs
    -------
    output1: dataframe
        Dataframe displaying the calculated changes in value for each team after each trade
        -- output1.Improve?
            The average points gained or lost by the team after the trade
        -- output1.AtTheTime
            The average points earned by the traded players before the trade
        -- output1.%Started
            The percentage the traded players started for the receiving team
        -- output1.WeeksOnTeam
            The number of weeks the traded players stayed on the team
        
    '''
    
    if 'TransCosts' not in transdf.columns:
        print("No FAAB this season")
        return
    else:
        adds = pandas.DataFrame(transdf[transdf.TransType=='Add'],copy=True)
        adds.loc[:,'TransCosts'] = [0 if not pandas.notnull(x) else                                    int(x.split(' ')[0])                                    for x in adds.TransCosts.values]
        adds.loc[:,'By'] = [x.split(' ')[0] if 'via' in x                            else x for x in adds.By.values]
        adds.Week = pandas.to_numeric(adds.Week)
        playerdf.week = pandas.to_numeric(playerdf.week)
        unis = playerdf.unique_str.unique()
        for i,row in adds.iterrows():
            pstr = get_unique_str(row)
            if pstr not in unis:
                match = get_close_matches(pstr,unis,cutoff=0.8)
                if len(match) > 0:
                    pstr = match[0]
                else: 
                    print('couldnt find a match for %s'%pstr)
                    continue
            pdf = playerdf[(playerdf.unique_str==pstr) & (playerdf.week>=row['Week'])]
            stindx = get_stint(pdf,row['By'])
            stint = playerdf.loc[stindx]
            adds.loc[i,'N_Weeks'] = len(stint)
            adds.loc[i,'Total_Points'] = stint['points'].sum()
            adds.loc[i,'Earned_Points'] = stint[stint.status=='Active'
                                               ].points.sum()
            if row['TransCosts'] == 0:
                adds.loc[i,'TP_perDollar'] = adds.loc[i,'Total_Points']
                adds.loc[i,'EP_perDollar'] = adds.loc[i,'Earned_Points']
            else:
                adds.loc[i,'TP_perDollar'] = adds.loc[i,'Total_Points'] /                                             adds.loc[i,'TransCosts']
                adds.loc[i,'EP_perDollar'] = adds.loc[i,'Earned_Points'] /                                             adds.loc[i,'TransCosts']

        TAvg = adds.pivot_table(values=['TransCosts','Earned_Points'],index='By',
                                aggfunc=np.sum)
        TAvg.loc[:,'PointsPerDollarSpent'] = TAvg['Earned_Points'] / TAvg['TransCosts']
        return adds, TAvg


# In[9]:


# Draft Soup
def get_unique_str_draft(row):
    info = row['info']
    if 'DEF' in info:
        nsplit = row['player'].split(' ')
        if 'Football Team' in row['player']:
            pstr = '%s %s DEF'%(nsplit[-2],nsplit[-1])
        else:
            pstr = '%s DEF '%(nsplit[-1])
    else:
        if ' - ' in info:
            position, team = info.split(' - ')
        else:
            position = info
            team = 'Free Agent'
        nsplit = row['player'].split(' ')
        name = ''
        for i in range(1,len(nsplit)):
            if i == len(nsplit)-1:
                name += '%s, '%nsplit[i]
            else:
                name += '%s '%nsplit[i]
        name += '%s.'%nsplit[0][0]
        pstr = '%s %s %s'%(name,position,team)
    
    return pstr

def DraftSoup(leagueID, n_rounds):
    
    
    draft = pandas.DataFrame()
    indx = 0
    # iterate through rounds
    for rnd in range(1,n_rounds+1):
        url = "https://canada.fantasy.nfl.com/league/"+leagueID+"/draftresults?draftResultsDetail=%s&draftResultsTab=round&draftResultsType=results"%rnd
        #print(url)
        page = urlopen(url)
        html = page.read()
        page.close()
        canned = bs(html, 'html.parser')
        # super janky way to get the picks using the order of presentation
        pick = 1
        i = 0
        for tag in canned.find_all(re.compile("^a")):
            jnk = tag.decode_contents()
            if '<' in jnk or 'View'  in jnk: continue
            if i % 2 == 0:
                draft.loc[indx,'round'] = rnd
                draft.loc[indx,'pick'] = pick
                draft.loc[indx,'player'] = jnk
                i += 1
            else:
                draft.loc[indx,'team'] = jnk
                i += 1
                pick += 1
                indx += 1
    indx = 0
    for rnd in range(1,n_rounds+1):
        url = "https://canada.fantasy.nfl.com/league/"+leagueID+"/draftresults?draftResultsDetail=%s&draftResultsTab=round&draftResultsType=results"%rnd
        #print(url)
        page = urlopen(url)
        html = page.read()
        page.close()
        canned = bs(html, 'html.parser')
        pick = 1
        i = 0
        for tag in canned.find_all(re.compile("^em")):
            jnk = tag.decode_contents()
            draft.loc[indx,'info'] = jnk
            indx += 1
    draft.loc[:,'overall'] = np.array(draft.index)+1
    for i,row in draft.iterrows():
        pstr = get_unique_str_draft(row)
        draft.loc[i,'unique_str'] = pstr
    return draft


# In[11]:


# Draft Outcomes
def radial_differential(df,i,r,col):
    pick = df.loc[i,'overall']
    r1 = pick - r
    r2 = pick + r
    radius = df[(df['overall']>=r1) & (df['overall']<=r2)]
    mn = radius[col].mean()
    
    return df.loc[i,col] - mn

def DraftOutcomes(player,draft,trans,radius=3):
    '''
    "Come on, Tom. Say it with me, you pancake-eating motherfucker" - Sonny Weaver Jr. Draft Day, 2014
    
    
    
    '''
    player.index = player.unique_str.values
    all_players = player.unique_str.unique()
    exceptions = []
    for i,row in draft.iterrows():
        if row['unique_str'] not in player['unique_str'].values:
            print(row['player'],i,'not found')
            matches = get_close_matches(row['unique_str'],all_players)
            print('Potential replacements?')
            print(matches,'\n')
            exceptions.append(row['player'])
    
    print(exceptions, 'will be skipped')
    team_table = trans.iloc[trans.loc[trans.TransType=='Add','To'].drop_duplicates().index]
    team_table = team_table.loc[:,['To','By']]
    team_table = team_table.set_index('To').to_dict()['By']
    for i,row in draft.iterrows():
        # deal with exceptions
        if row['player'] in exceptions:
            draft.loc[i,['ActivePoints','DrafterPoints',]] = 0
        else:
            pdf = player[player.unique_str==row['unique_str']]
            draft.loc[i,'TotalPoints'] = pdf.points.sum()
            draft.loc[i,'ActivePoints'] = pdf[pdf.status=='Active'
                                             ].points.sum()
            draft.loc[i,'DrafterPoints'] = pdf[
                        (pdf.status=='Active') & \
                        (pdf.owner==team_table[row['team']])
                                              ].points.sum()
            ## WARNING: Assumes 0 pt games = inactive (not always true)
            draft.loc[i,'Games'] = len(pdf[pdf.points!=0])
            draft.loc[i,'ActiveGames'] = len(pdf[(pdf.points!=0) &                                                 (pdf.status=='Active')])
        
    for i,row in draft.iterrows():
        diff = radial_differential(draft,i,radius,'TotalPoints')
        draft.loc[i,'R%s_TP_diff'%radius] = diff
        diff = radial_differential(draft,i,radius,'DrafterPoints')
        draft.loc[i,'R%s_DP_diff'%radius] = diff
    return draft

def DraftPlots(draft, graphtype):
    totalcolumns = ['TotalPoints', 'ActivePoints', 'DrafterPoints', 'Games', 'ActiveGames']
    if graphtype == 'Round':
        for col in totalcolumns:
            sns.pointplot(x='round',y=col,data=draft)
            plt.show()
    if graphtype == 'Team':
        for col in totalcolumns:
            order = draft.groupby('team')[col
                                         ].mean().sort_values(ascending=False).index
            g = sns.barplot(x='team',y=col,data=draft,order=order)
            g.set_xticklabels(g.get_xticklabels(),rotation = 90)
            plt.show()
    if graphtype == 'Average': 
        for col in draft.columns[-2:]:
            order = draft.groupby('team')[col
                                         ].mean().sort_values(ascending=False).index
            g = sns.barplot(x='team',y=col,data=draft,order=order)
            g.set_xticklabels(g.get_xticklabels(),rotation = 90)
            plt.show()
    if not graphtype:
        print('Please select a graphtype!')


# In[ ]:




