from .algorithms.gambit import gambit
from .algorithms.bird import bird
from .algorithms.simple import simple

import pandas as pd

def disambiguate_aliases(aliases, method='gambit', **quargs):
    """ Computes author ids for all provided aliases.
    
    Args:
        aliases: pandas.DataFrame object with columns "alias_name" and "alias_email"
        method: disambiguation method from {"gambit", "bird", "simple"}
        quargs: hyperparameters for the selected algorithm
            gambit: similarity threshold (thresh): 0-1,
                    string similarity measure (sim): {'lev', 'jw'}
            bird:   similarity threshold (thresh): 0-1,
            simple: -
            
    Returns:
        pandas.DataFrame with disambiguation information and author ids for all provided aliases
    """
    
    if not type(aliases) == pd.DataFrame or not ('alias_name' in aliases.columns and 'alias_email' in aliases.columns):
        raise Exception('aliases must be a pandas.DataFrame object with columns "alias_name" and "alias_email"')
    
    if method == 'gambit':
        disambig_fun = gambit
    elif method == 'bird':
        disambig_fun = bird
    elif method == 'simple':
        disambig_fun = simple
    else:
        raise Exception('invalid method')
    
    return disambig_fun(aliases, **quargs)