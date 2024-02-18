import pandas as pd
from datetime import datetime

import Constants


def dates_slice(frame: pd.DataFrame, ini_date: datetime, end_date: datetime):
    ini_date = ini_date if frame["date"].min() < ini_date else frame["date"].min()
    end_date = end_date if frame["date"].max() > end_date else frame["date"].max()
    
    mask = (frame["date"] > ini_date) & (frame["date"] <= end_date)
    
    return frame.loc[mask]

def expenses(frame: pd.DataFrame):

    return frame[frame["amount"] < 0]


def income(frame: pd.DataFrame): 
    return frame[frame["amount"] > 0]
    

def sort_frame_with_categories(frame: pd.DataFrame, categories: dict):
    descriptions = frame["description"]
    frame_by_categories: dict = {"other": frame.copy()}

    for category in categories:
        key_words = categories[category]

        all_matches = map(lambda key_word: frame[descriptions.str.contains(f"(?i){key_word}", regex=True)], key_words)
        all_matches = pd.concat(all_matches)

        frame_by_categories[category] = all_matches
        frame_by_categories["other"] = frame_by_categories["other"].drop(all_matches.index, axis=0)

    return frame_by_categories

