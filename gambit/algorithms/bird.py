import sqlite3
import pandas as pd
import unidecode
from Levenshtein import distance as lev_dist
from pyjarowinkler.distance import get_jaro_distance as jw_sim
import tqdm
import numpy as np
import re 
import os

def split_delimiters(s): 
    delimiters = r'\ |,|\.'
    
    # Split at delimiters
    ss = re.split(delimiters, s)
    
    return ss

def clean_name(s):
    if s:   
        ss = split_delimiters(s)
    
        ss = [''.join([i for i in s if i.isalpha() or i == ' ']) for s in ss]

        while 'jr' in ss:
            ss.remove('jr')

        while 'admin' in ss:
            ss.remove('admin')

        while 'support' in ss:
            ss.remove('support')
            
        while '' in ss:
            ss.remove('')
        
        s = ' '.join(ss)
    
    return s


def get_first_name(s):
    if s:
        ss = s.split(' ')
        if len(ss) > 0:
            s = ss[0]
        else:
            s = ''
            
    return s

def get_last_name(s):
    if s:
        ss = s.split(' ')
        if len(ss) > 0:
            s = ss[-1]
        else:
            s = ''
            
    return s

def get_email_base(s):
    if s:
        s = s.split('@')[0]
    
    return s
    
def lev_sim(s1, s2):
    # 1 minus normalised Levenshtein edit distance
    return 1 - lev_dist(s1, s2)/max(len(s1), len(s2))


def compare_rows(idx1, idx2, row1, row2, thresh=.90):
    name_thresh = 2
    email_thresh = 3
    
    sims = []

    sim_f = lev_sim
    
    name1 = row1['name']
    first_name1 = row1['first_name']
    last_name1 = row1['last_name']
    email1 = row1['email']
    email_base1 = row1['email_base']

    name2 = row2['name']
    first_name2 = row2['first_name']
    last_name2 = row2['last_name']
    email2 = row2['email']
    email_base2 = row2['email_base']
    
    if (name1 and len(name1) >= name_thresh) and (name2 and len(name2) >= name_thresh):
        sims.append(sim_f(name1, name2))
        
    if (first_name1 and len(first_name1) >= name_thresh) and \
       (last_name1 and len(last_name1) >= name_thresh) and \
       (first_name2 and len(first_name2) >= name_thresh) and \
       (last_name2 and len(last_name2) >= name_thresh):
            sims.append(min(sim_f(first_name1, first_name2),
                            sim_f(last_name1, last_name2)))
        
    # comparing email base leads to many false positives e.g. with emails following first_name@last_name
    if (email_base1 and len(email_base1) >= email_thresh) and \
       (email_base2 and len(email_base2) >= email_thresh):
        sims.append(2*(email1 == email2))
        sims.append(sim_f(email_base1, email_base2))
        
    if (first_name1 and len(first_name1) >= name_thresh) and \
       (last_name1 and len(last_name1) >= name_thresh) and \
       (first_name2 and len(first_name2) >= name_thresh) and \
       (last_name2 and len(last_name2) >= name_thresh) and \
       (email_base1 and len(email_base1) >= email_thresh) and \
       (email_base2 and len(email_base2) >= email_thresh):
        if first_name2 != last_name2:
            sims.append(email_base1.find(first_name2[0] + last_name2) != -1)
            sims.append(email_base1.find(first_name2 + last_name2[0]) != -1)
            sims.append((email_base1.find(first_name2) != -1) and \
                        (email_base1.find(last_name2) != -1))

        if first_name1 != last_name1:
            sims.append(email_base2.find(first_name1[0] + last_name1) != -1)
            sims.append(email_base2.find(first_name1 + last_name1[0]) != -1)
            sims.append((email_base2.find(first_name1) != -1) and \
                        (email_base2.find(last_name1) != -1))
    
    if len(sims) == 0:
        return False
    else:
        return max(sims) >= thresh

# -------------------------------------------------------------------
    
def bird(authors, thresh=.95):
    authors.reset_index(inplace=True, drop=True)

    authors['name'] = authors['alias_name'].apply(clean_name)
    authors['email'] = authors['alias_email']
    authors['first_name'] = authors.name.apply(get_first_name)
    authors['last_name'] = authors.name.apply(get_last_name)
    authors['email_base'] = authors.email.apply(get_email_base)
    
    authors['author_id'] = None
    next_id = 0
    
    with tqdm.tqdm(total = int(len(authors)*(len(authors)-1)/2), desc='author identity disambiguation') as pbar:
        for idx1, row1 in authors.iterrows():        
            if pd.isnull(authors.loc[idx1, 'author_id']):
                authors['author_id'][idx1] = next_id
                next_id += 1

            for idx2, row2 in authors[idx1+1:].iterrows():
                if compare_rows(idx1, idx2, row1, row2, thresh=thresh):
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