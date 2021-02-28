import sqlite3
import pandas as pd
import unidecode
from Levenshtein import distance as lev_dist
from pyjarowinkler.distance import get_jaro_distance as jw_sim
import tqdm
import numpy as np
import re 
import os

def fix_capitalisation(s):
    # replaces all caps by only first letter caps
    return ''.join([c if (idx == 0) or not (s[idx-1].isupper()) else c.lower() for idx, c in enumerate(s)])


def split_delimiters(s): 
    delimiters = r'\ |\+|-|,|\.|_|;'
    
    s = fix_capitalisation(s)
    
    # Replace camel case through whitespaces
    lot = re.findall(r'([^\ A-Z]*)?([A-Z][^\ A-Z]*)?', s)
    s = ' '.join([n if type(t) == tuple else t for t in lot for n in t])
    
    # Split at delimiters
    ss = re.split(delimiters, s)
    
    return ss

def clean_name(s):
    if s:
        s = unidecode.unidecode(str(s))
    
        ss = split_delimiters(s)
    
        ss = [s.lower() for s in ss]
        
        ss = [''.join([i for i in s if i.isalpha() or i == ' ']) for s in ss]
        
        while 'jr' in ss:
            ss.remove('jr')

        while 'admin' in ss:
            ss.remove('admin')

        while 'support' in ss:
            ss.remove('support')

        while 'anonymous' in ss:
            ss.remove('anonymous')

        while 'anon' in ss:
            ss.remove('anon')

        while 'user' in ss:
            ss.remove('user')

        while 'cvs' in ss:
            ss.remove('cvs')
            
        while '' in ss:
            ss.remove('')

        timezones = ['cst', 'pst', 'pdt', 'cdt', 'gmt', 'bst', 'cet', 'cest']
        for tz in timezones:
            while tz in ss:
                ss.remove(tz)
        
        s = ' '.join(ss)
    
    return s

def clean_email(s):
    if s:
        s = unidecode.unidecode(str(s))
    
        s = s.lower()
    
    return s

def get_first_name(s):
    if s:
        ss = s.split(' ')
        if len(ss) > 0:
            s = ss[0]
        else:
            s = ''
            
    return s

def get_penultimate_name(s):
    if s:
        ss = s.split(' ')
        if len(ss) > 2:
            s = ss[-2]
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


def compare_rows(idx1, idx2, row1, row2, authors, thresh=.90, sim='jw'):
    name_thresh = 3
    email_thresh = 3
    
    sims = []
    
    if sim == 'lev':
        sim_f = lev_sim
    elif sim == 'jw':
        sim_f = jw_sim
    else:
        assert False
    
    print_dict = {}
    
    name1 = row1['name']
    first_name1 = row1['first_name']
    penultimate_name1 = row1['penultimate_name']
    last_name1 = row1['last_name']
    email1 = row1['email']
    email_base1 = row1['email_base']

    name2 = row2['name']
    first_name2 = row2['first_name']
    penultimate_name2 = row2['penultimate_name']
    last_name2 = row2['last_name']
    email2 = row2['email']
    email_base2 = row2['email_base']
    
    if (name1 and len(name1) >= name_thresh) and (name2 and len(name2) >= name_thresh):
        sims.append(sim_f(name1, name2))
        sims.append(''.join([i for i in name1 if i.isalpha()]) == name2)
        sims.append(''.join([i for i in name2 if i.isalpha()]) == name1)
        sims.append(''.join([i for i in name1 if i.isalpha()]) == \
                    ''.join([i for i in name2 if i.isalpha()]))
        
    if (first_name1 and len(first_name1) >= name_thresh) and \
       (last_name1 and len(last_name1) >= name_thresh) and \
       (first_name2 and len(first_name2) >= name_thresh) and \
       (last_name2 and len(last_name2) >= name_thresh):
        if (penultimate_name1 and len(penultimate_name1) >= name_thresh) and \
           (penultimate_name2 and len(penultimate_name2) >= name_thresh):
            sims.append(min(sim_f(first_name1, first_name2),
                            max(sim_f(last_name1, last_name2),
                                sim_f(last_name1, penultimate_name2),
                                sim_f(penultimate_name1, last_name2))))
            sims.append(min(sim_f(first_name1, last_name2),
                            max(sim_f(penultimate_name1, first_name2),
                                sim_f(last_name1, penultimate_name2),
                                sim_f(last_name1, first_name2))))
            sims.append(min(sim_f(last_name1, first_name2),
                            max(sim_f(penultimate_name1, last_name2),
                                sim_f(first_name1, penultimate_name2),
                                sim_f(first_name1, last_name2))))
        elif (penultimate_name1 and len(penultimate_name1) >= name_thresh):
            sims.append(min(sim_f(first_name1, first_name2),
                            max(sim_f(penultimate_name1, last_name2),
                                sim_f(last_name1, last_name2))))
            sims.append(min(sim_f(first_name1, last_name2),
                            max(sim_f(penultimate_name1, first_name2),
                                sim_f(last_name1, first_name2))))
            sims.append(min(sim_f(last_name1, first_name2),
                            max(sim_f(penultimate_name1, last_name2),
                                sim_f(first_name1, last_name2))))
        elif (penultimate_name2 and len(penultimate_name2) >= name_thresh):
            sims.append(min(sim_f(first_name2, first_name1),
                            max(sim_f(penultimate_name2, last_name1),
                                sim_f(last_name2, last_name1))))
            sims.append(min(sim_f(first_name2, last_name1),
                            max(sim_f(penultimate_name2, first_name1),
                                sim_f(last_name2, first_name1))))
            sims.append(min(sim_f(last_name2, first_name1),
                            max(sim_f(penultimate_name2, last_name1),
                                sim_f(first_name2, last_name1))))
        else:
            sims.append(min(sim_f(first_name1, first_name2),
                            sim_f(last_name1, last_name2)))
            sims.append(min(sim_f(first_name1, last_name2),
                            sim_f(last_name1, first_name2)))
        
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
            
            sims.append(2*((email_base1.find(first_name2) != -1) and \
                        (email_base1.find(last_name2)) != -1))
        if first_name1 != last_name1:
            sims.append(email_base2.find(first_name1[0] + last_name1) != -1)
            
            sims.append(email_base2.find(first_name1 + last_name1[0]) != -1)
            
            sims.append(2*((email_base2.find(first_name1) != -1) and \
                        (email_base2.find(last_name1)) != -1))
    
    if len(sims) > 0:
        return np.mean(sorted(sims, reverse=True)[:2]) >= thresh
    else:
        return False

# -------------------------------------------------------------------
    
def gambit(authors, thresh=0.95, sim='lev'):
    authors.reset_index(inplace=True, drop=True)

    authors['name'] = authors['alias_name'].apply(clean_name)
    authors['email'] = authors['alias_email'].apply(clean_email)
    authors['first_name'] = authors.name.apply(get_first_name)
    authors['last_name'] = authors.name.apply(get_last_name)
    authors['penultimate_name'] = authors.name.apply(get_penultimate_name)
    authors['email_base'] = authors.email.apply(get_email_base)
    
    authors['author_id'] = None
    next_id = 0
    
    with tqdm.tqdm(total = int(len(authors)*(len(authors)-1)/2), desc='author identity disambiguation') as pbar:
        for idx1, row1 in authors.iterrows():        
            if pd.isnull(authors.loc[idx1, 'author_id']):
                authors['author_id'][idx1] = next_id
                next_id += 1

            for idx2, row2 in authors[idx1+1:].iterrows():
                if compare_rows(idx1, idx2, row1, row2, authors, thresh=thresh, sim=sim):
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