import random
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import datetime
import re
import numpy as np
from sklearn.neural_network import MLPClassifier

def function():

    global df2, matches, matches2, rf, df, matches_future, dates
    print("Joining small dataframes into larger one.")
    randomsize = 201*2
    datasize = 500*2
    trainsize = int((((randomsize+datasize)-1)/4)*3)
    testsize = int((((randomsize+datasize)-1)/4))
    dates = []
    joined = pd.DataFrame()
    future = pd.DataFrame()
    path = os.getcwd() + "/matches/"
    future_path = os.getcwd() + "/future/"

    source = os.getcwd() + "/new_matches/"
    allfiles = os.listdir(source)
    destination = os.getcwd() + "/matches/"
    try:
        for f in allfiles:
            src_path = os.path.join(source, f)
            dst_path = os.path.join(destination, f)
            os.rename(src_path, dst_path)
    except Exception as e:
        print(e)
    print("Moving files to matches folder is finished.")

    for i in range(randomsize):
        rand_idx = random.randrange(len(os.listdir(path)))
        filename = os.listdir(path)[rand_idx]
        with open(os.path.join(path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                joined = pd.concat([joined,tmp])
                print("Success: " + filename)
            except Exception as e:
                print(e)

    for filename in os.listdir(path)[-datasize:]: #-200
        with open(os.path.join(path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                joined = pd.concat([joined,tmp])
                print("Success: " + filename)
            except Exception as e:
                print(e)

    print("Joining small future dataframes into a large one begins.")
    for filename in os.listdir(future_path):
        with open(os.path.join(future_path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                future = pd.concat([future, tmp])
                match_str = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                res = datetime.datetime.strptime(match_str.group(), '%Y-%m-%d').date()
                dates.append(res)
                print("Success: " + filename)
            except Exception as e:
                print(e)

    print("Joining small future dataframes into a large one finished.")

    try:
        matches = joined
        totallost = matches["props_pageProps_match_matchInfo_team1_gameRecord_totalLost"].tolist()
        totallost_int = [int(totallost[i]) for i in range(len(totallost))]
        matches["team1_total_lost"] = totallost_int
        totalwin = matches["props_pageProps_match_matchInfo_team1_gameRecord_totalWin"].tolist()
        totalwin_int = [int(totalwin[i]) for i in range(len(totalwin))]
        matches["team1_total_win"] = totalwin_int
        totallost2 = matches["props_pageProps_match_matchInfo_team2_gameRecord_totalLost"].tolist()
        totallost_int2 = [int(totallost2[i]) for i in range(len(totallost2))]
        matches["team2_total_lost"] = totallost_int2
        totalwin2 = matches["props_pageProps_match_matchInfo_team2_gameRecord_totalWin"].tolist()
        totalwin_int2 = [int(totalwin2[i]) for i in range(len(totalwin2))]
        matches["team2_total_win"] = totalwin_int2
        team1winprob = matches["props_pageProps_match_matchInfo_prematchWinProbability_team1Winprob"].tolist()
        team1winprobfloat = [float(team1winprob[i]) for i in range(len(team1winprob))]
        matches["team1_winprob"] = team1winprobfloat
        team2winprob = matches["props_pageProps_match_matchInfo_prematchWinProbability_team2Winprob"].tolist()
        team2winprobfloat = [float(team2winprob[i]) for i in range(len(team2winprob))]
        matches["team2_winprob"] = team2winprobfloat
        winning = matches["props_pageProps_match_matchInfo_games_0_snapshotPlayerStats_0_winningTeam"].tolist()
        target = matches["props_pageProps_match_matchInfo_team1_abbreviation"].tolist()
        result = [1 if str(winning[i]) in str(target[i]) or str(target[i]) in str(winning[i]) else 0 for i in range(len(winning))]
        print("Cleaning finished.")
        pwr1 = matches["props_pageProps_match_matchInfo_team1_powrRanking_ranking"].tolist()
        pwr1result = [float(pwr1[i]) for i in range(len(pwr1))]
        pwr2 = matches["props_pageProps_match_matchInfo_team2_powrRanking_ranking"].tolist()
        pwr2result = [float(pwr2[i]) for i in range(len(pwr2))]
        matches["team1_power"] = pwr1result
        matches["team2_power"] = pwr2result
        matches["date"] = pd.to_datetime(matches["props_pageProps_match_matchInfo_games_0_gameStartDateTime"])
        matches["tournament"] = matches["props_pageProps_match_seriesName"].astype("category").cat.codes
        matches["team"] = matches["props_pageProps_match_matchInfo_team1_abbreviation"].astype("category").cat.codes
        matches["opp_code"] = matches["props_pageProps_match_matchInfo_team2_abbreviation"].astype("category").cat.codes
        matches["year"] = matches["date"].dt.year
        matches["month"] = matches["date"].dt.month
        matches["day_code"] = matches["date"].dt.dayofweek
        matches["target"] = result
        matches["winning"] = matches["props_pageProps_match_matchInfo_games_0_snapshotPlayerStats_0_winningTeam"]
        print("Extended data is ready, Transformation finished.")
    except Exception as e:
        print(e)

    print("Machine Learning file begins.")
    global predictors, preds, test, matches_future
    try:
        matches_future = future
        tournament = matches_future["props_pageProps_match_seriesName"]
        tournament = list(tournament)
        team = matches_future["props_pageProps_match_matchInfo_team1_abbreviation"]
        team = list(team)
        opp_code = matches_future["props_pageProps_match_matchInfo_team2_abbreviation"]
        opp_code = list(opp_code)
        # NEW DATA
        totallost = matches_future["props_pageProps_match_matchInfo_team1_gameRecord_totalLost"].tolist()
        totallost_int = [int(totallost[i]) for i in range(len(totallost))]
        matches_future["team1_total_lost"] = totallost_int
        totalwin = matches_future["props_pageProps_match_matchInfo_team1_gameRecord_totalWin"].tolist()
        totalwin_int = [int(totalwin[i]) for i in range(len(totalwin))]
        matches_future["team1_total_win"] = totalwin_int
        totallost2 = matches_future["props_pageProps_match_matchInfo_team2_gameRecord_totalLost"].tolist()
        totallost_int2 = [int(totallost2[i]) for i in range(len(totallost2))]
        matches_future["team2_total_lost"] = totallost_int2
        totalwin2 = matches_future["props_pageProps_match_matchInfo_team2_gameRecord_totalWin"].tolist()
        totalwin_int2 = [int(totalwin2[i]) for i in range(len(totalwin2))]
        matches_future["team2_total_win"] = totalwin_int2
        team1winprob = matches_future["props_pageProps_match_matchInfo_prematchWinProbability_team1Winprob"].tolist()
        team1winprobfloat = [float(team1winprob[i]) for i in range(len(team1winprob))]
        matches_future["team1_winprob"] = team1winprobfloat
        team2winprob = matches_future["props_pageProps_match_matchInfo_prematchWinProbability_team2Winprob"].tolist()
        team2winprobfloat = [float(team2winprob[i]) for i in range(len(team2winprob))]
        matches_future["team2_winprob"] = team2winprobfloat
        pwr1 = matches_future["props_pageProps_match_matchInfo_team1_powrRanking_ranking"].tolist()
        pwr1result = [float(pwr1[i]) for i in range(len(pwr1))]
        pwr2 = matches_future["props_pageProps_match_matchInfo_team2_powrRanking_ranking"].tolist()
        pwr2result = [float(pwr2[i]) for i in range(len(pwr2))]
        matches_future["team1_power"] = pwr1result
        matches_future["team2_power"] = pwr2result
        matches_future["date"] = pd.to_datetime(dates)
        mcattournament = list(matches["tournament"])
        mtournament = list(matches["props_pageProps_match_seriesName"])
        tournament_cat = [mcattournament[mtournament.index(tournament[i])] if tournament[i] in mtournament else float("nan") for i in range(len(tournament))]
        mcatopp_code = list(matches["opp_code"])
        mopp_code = list(matches["props_pageProps_match_matchInfo_team2_abbreviation"])
        opp_code_cat = [mcatopp_code[mopp_code.index(opp_code[i])] if opp_code[i] in mopp_code else float("nan") for i in range(len(opp_code))]
        mcatteam = list(matches["team"])
        mteam = list(matches["props_pageProps_match_matchInfo_team1_abbreviation"])
        team_cat = [mcatteam[mteam.index(team[i])] if team[i] in mteam else float("nan") for i in range(len(team))]
        tmp3col = pd.DataFrame(list(zip(tournament_cat, team_cat, opp_code_cat)),columns =['tournament', 'team', 'opp_code'])
        print("Extended future data is ready.")
        matches_future['tournament'] = tmp3col.tournament
        matches_future['team'] = tmp3col.team
        matches_future['opp_code'] = tmp3col.opp_code
        matches_future["year"] = matches_future["date"].dt.year
        matches_future["month"] = matches_future["date"].dt.month
        matches_future["day_code"] = matches_future["date"].dt.dayofweek
        matches_future = matches_future.dropna(axis=0, subset=['tournament'])
        matches_future = matches_future.dropna(axis=0, subset=['team'])
        matches_future = matches_future.dropna(axis=0, subset=['opp_code'])
        matches_future = matches_future.dropna(axis=0, subset=['team1_power'])
        matches_future = matches_future.dropna(axis=0, subset=['team2_power'])
        matches_future = matches_future.dropna(axis=0, subset=['team1_winprob'])
        matches_future = matches_future.dropna(axis=0, subset=['team2_winprob'])
        print("Transformation finished.")
        print("Values for file writing  are created.")
    except Exception as e:
        print(e)

    try:
        print("Machine learning begins.")
        rf = RandomForestClassifier(n_estimators=500, min_samples_split=7, random_state=1)
        #rf = RandomForestClassifier(n_estimators=500, min_samples_split=7, max_depth = 4, max_features = 3, bootstrap = True, random_state = 18)
        #clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes = (5, 2), random_state = 1)
        train = matches.head(trainsize) #matches[matches["date"] < '2022-01-01']
        test = matches.tail(testsize) #matches[matches["date"] > '2022-01-01']
        train.fillna(0,inplace= True)
        test.fillna(0,inplace=True)
        matches_future.fillna(0,inplace=True)
        predictors_list = ["team1_winprob","team2_winprob","team1_power","team2_power","tournament", "team", "opp_code", "year","month" ,"day_code"]
        a = np.intersect1d((matches.select_dtypes(include=[np.number])).columns,(matches_future.select_dtypes(include=[np.number])).columns)
        predictors = a.tolist()
        #s = np.intersect1d((matches.select_dtypes(include=["string"])).columns,(matches_future.select_dtypes(include=["string"])).columns)
        #s = s.tolist()
        #predictors.extend(s)
        predictors.extend(predictors_list)
        print("Predictors are ready, beginning fitting.")
        rf.fit(train[predictors], train["target"])
        #clf.fit(train[predictors], train["target"])
        print("Predicting.")
        preds = rf.predict(test[predictors])
        #preds = clf.predict(test[predictors])
        backup = predictors
        predictors = predictors_list
        acc = accuracy_score(test["target"], preds)
        with open("D:/LOL/MLresults.txt", "w") as f:
            test["results"] = preds
            predictors.append("date")
            predictors.append("props_pageProps_match_seriesName")
            predictors.append("props_pageProps_match_matchInfo_team1_abbreviation")
            predictors.append("props_pageProps_match_matchInfo_team2_abbreviation")
            predictors.append("results")
            predictors.append("target")
            predictors.append("winning")
            f.write(test[predictors].to_string())
            f.write("\n")
            f.write(str(acc * 100) + "%")
        print("Appending newest matches data to test.")
        predictors.remove("winning")
        predictors.remove("target")
        predictors.remove("results")
        predictors.remove("props_pageProps_match_matchInfo_team2_abbreviation")
        predictors.remove("props_pageProps_match_matchInfo_team1_abbreviation")
        predictors.remove("props_pageProps_match_seriesName")
        predictors.remove("date")
        predictors = backup
        test = test.drop(columns=["results"])
        test = pd.concat([test, matches_future], ignore_index=True)
        preds = rf.predict(test[predictors])
        #preds = clf.predict(test[predictors])
        predictors = predictors_list
        print("Printing results into a file.")
        with open("D:/LOL/results.txt", "w") as f:
            test["results"] = preds
            predictors.append("date")
            predictors.append("props_pageProps_match_seriesName")
            predictors.append("props_pageProps_match_matchInfo_team1_abbreviation")
            predictors.append("props_pageProps_match_matchInfo_team2_abbreviation")
            predictors.append("results")
            predictors.append("winning")
            f.write(test[predictors].to_string())
            f.write("\n")
            f.write(str(acc*100) + "%")
        print("Printing is done, ML is finished.")
    except Exception as e:
        print(e)

function()
