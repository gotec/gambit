import sqlite3
import pandas as pd
import unidecode
from Levenshtein import distance as lev_dist
from pyjarowinkler.distance import get_jaro_distance as jw_sim
import tqdm
import numpy as np
import re 
import os

def get_email_base(s):
    if s:
        s = s.split('@')[0]
    
    return s


def compare_rows(idx1, idx2, row1, row2):
    tresh = 3
    
    if (len(str(row1.name)) >= tresh) and (len(str(row2.name)) >= tresh) and (row1.name == row2.name):
        return True
    elif (len(str(row1.email_base)) >= tresh) and (len(str(row2.email_base)) >= tresh) and (row1.email_base == row2.email_base):
        return True
    else:
        return False

# -------------------------------------------------------------------
    
def simple(authors):
    authors.reset_index(inplace=True, drop=True)

    authors['name'] = authors['alias_name']
    authors['email'] = authors['alias_email']
    authors['email_base'] = authors.email.apply(get_email_base)
    
    authors['author_id'] = None
    next_id = 0
    
    with tqdm.tqdm(total = int(len(authors)*(len(authors)-1)/2), desc='author identity disambiguation') as pbar:
        for idx1, row1 in authors.iterrows():        
            if pd.isnull(authors.loc[idx1, 'author_id']):
                authors['author_id'][idx1] = next_id
                next_id += 1

            for idx2, row2 in authors[idx1+1:].iterrows():
                if compare_rows(idx1, idx2, row1, row2):
                    if pd.notnull(authors.loc[idx1, 'author_id']) and pd.notnull(authors.loc[idx2, 'author_id']):
                        min_id = min(authors.loc[idx1, 'author_id'], authors.loc[idx2, 'author_id'])
                        authors.loc[authors.author_id == authors.loc[idx1, 'author_id'], 'author_id'] = min_id
                        authors.loc[authors.author_id == authors.loc[idx2, 'author_id'], 'author_id'] = min_id
                    elif pd.notnull(authors.loc[idx1, 'author_id']):
                        authors['author_id'][idx2] = authors.loc[idx1, 'author_id']
                    else:
                        assert False
                pbar.update(1)
    return authors

