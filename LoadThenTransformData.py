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
    randomsize = 200 * 2
    randomsize = int(randomsize + 1)
    datasize = int(500 * 2)
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
    c = 0
    for i in range(randomsize):
        rand_idx = random.randrange((len(os.listdir(path))-datasize-1))
        filename = os.listdir(path)[rand_idx]
        with open(os.path.join(path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                joined = pd.concat([joined,tmp])
                c+=1
                print("Success: " + filename + " c: " + str(c))
            except Exception as e:
                print(e)
    c = 0
    for filename in os.listdir(path)[-datasize:]:
        with open(os.path.join(path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                joined = pd.concat([joined,tmp])
                c += 1
                print("Success: " + filename + " c: " + str(c))
            except Exception as e:
                print(e)
    c = 0
    print("Joining small future dataframes into a large one begins.")
    for filename in os.listdir(future_path):
        with open(os.path.join(future_path, filename), 'r', encoding="utf8") as f:
            try:
                tmp = pd.read_csv(f)
                future = pd.concat([future, tmp])
                match_str = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                res = datetime.datetime.strptime(match_str.group(), '%Y-%m-%d').date()
                dates.append(res)
                c += 1
                print("Success: " + filename + " c: " + str(c))
            except Exception as e:
                print(e)
    print("Joining small future dataframes into a large one finished.")
    try:
        matches = joined
        team1winprob = matches["props_pageProps_match_matchInfo_prematchWinProbability_team1Winprob"].tolist()
        team2winprob = matches["props_pageProps_match_matchInfo_prematchWinProbability_team2Winprob"].tolist()
        winning = matches["props_pageProps_match_matchInfo_games_0_snapshotPlayerStats_0_winningTeam"].tolist()
        target = matches["props_pageProps_match_matchInfo_team1_abbreviation"].tolist()
        pwr1 = matches["props_pageProps_match_matchInfo_team1_powrRanking_ranking"].tolist()
        pwr2 = matches["props_pageProps_match_matchInfo_team2_powrRanking_ranking"].tolist()
        team1winprobfloat = [float(team1winprob[i]) for i in range(len(team1winprob))]
        team2winprobfloat = [float(team2winprob[i]) for i in range(len(team2winprob))]
        result = [1 if str(winning[i]) in str(target[i]) or str(target[i]) in str(winning[i]) else 0 for i in range(len(winning))]
        pwr1result = [float(pwr1[i]) for i in range(len(pwr1))]
        pwr2result = [float(pwr2[i]) for i in range(len(pwr2))]
        print("Cleaning finished.")
        matches["team1_winprob"] = team1winprobfloat
        matches["team2_winprob"] = team2winprobfloat
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
        matches_tmp = matches.dropna(axis=0, subset=["team1_winprob"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["team2_winprob"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["team1_power"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["team2_power"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["tournament"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["team"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["opp_code"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["year"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["month"])
        matches_tmp = matches_tmp.dropna(axis=0, subset=["day_code"])
        matches = matches_tmp
        matches = matches[matches.winning != 0]
        matches = matches[matches.winning != float("nan")]
        matches = matches[matches.team != -1.0]
        matches = matches[matches.team != float("nan")]
        print("Extended data is ready, Transformation finished.")
    except Exception as e:
        print(e)
    print("Machine Learning file begins.")
    global predictors, preds, test, matches_future
    try:
        matches_future = future
        tournament = matches_future["props_pageProps_match_seriesName"]
        team = matches_future["props_pageProps_match_matchInfo_team1_abbreviation"]
        opp_code = matches_future["props_pageProps_match_matchInfo_team2_abbreviation"]
        opp_code = list(opp_code)
        tournament = list(tournament)
        team = list(team)
        team1winprob = matches_future["props_pageProps_match_matchInfo_prematchWinProbability_team1Winprob"].tolist()
        team2winprob = matches_future["props_pageProps_match_matchInfo_prematchWinProbability_team2Winprob"].tolist()
        pwr1 = matches_future["props_pageProps_match_matchInfo_team1_powrRanking_ranking"].tolist()
        pwr2 = matches_future["props_pageProps_match_matchInfo_team2_powrRanking_ranking"].tolist()
        mcattournament = list(matches["tournament"])
        mtournament = list(matches["props_pageProps_match_seriesName"])
        mcatopp_code = list(matches["opp_code"])
        mopp_code = list(matches["props_pageProps_match_matchInfo_team2_abbreviation"])
        mcatteam = list(matches["team"])
        mteam = list(matches["props_pageProps_match_matchInfo_team1_abbreviation"])
        team1winprobfloat = [float(team1winprob[i]) for i in range(len(team1winprob))]
        team2winprobfloat = [float(team2winprob[i]) for i in range(len(team2winprob))]
        pwr1result = [float(pwr1[i]) for i in range(len(pwr1))]
        pwr2result = [float(pwr2[i]) for i in range(len(pwr2))]
        tournament_cat = [mcattournament[mtournament.index(tournament[i])] if tournament[i] in mtournament else float("nan") for i in range(len(tournament))]
        opp_code_cat = [mcatopp_code[mopp_code.index(opp_code[i])] if opp_code[i] in mopp_code else float("nan") for i in range(len(opp_code))]
        team_cat = [mcatteam[mteam.index(team[i])] if team[i] in mteam else float("nan") for i in range(len(team))]
        tmp3col = pd.DataFrame(list(zip(tournament_cat, team_cat, opp_code_cat)),columns =['tournament', 'team', 'opp_code'])
        print("Extended future data is ready.")
        matches_future["team1_winprob"] = team1winprobfloat
        matches_future["team2_winprob"] = team2winprobfloat
        matches_future["team1_power"] = pwr1result
        matches_future["team2_power"] = pwr2result
        matches_future["date"] = pd.to_datetime(dates)
        matches_future['tournament'] = tmp3col['tournament']
        matches_future['team'] = tmp3col['team']
        matches_future['opp_code'] = tmp3col['opp_code']
        matches_future["year"] = matches_future["date"].dt.year
        matches_future["month"] = matches_future["date"].dt.month
        matches_future["day_code"] = matches_future["date"].dt.dayofweek
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
        with open(os.getcwd() + "/MLresults.txt", "w") as f:
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
        with open(os.getcwd() + "/results.txt", "w") as f:
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
