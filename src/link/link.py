"""Link data from an earlier time point to
data from a later time point."""

import argparse
import csv
import cython_winkler
from functools import partial
import os
import pandas as pd
import yaml

def parse_args():
    """Parse commandline arguments."""
    parser = argparse.ArgumentParser(description='Link data from an earlier time point to data from a later time point.')
    parser.add_argument('--earlier_file', required=True, help='file containing data from the earlier time point')
    parser.add_argument('--later_file', required=True, help='file containing data from the later time point')
    parser.add_argument('--configuration_file', required=True, help='YAML configuration file')
    parser.add_argument('--output_file', required=True, help='file to which results are to be written')
    return parser.parse_args()

def load_configuration(configuration_file):
    """Load configuration file."""
    with open(configuration_file) as f:
        return yaml.safe_load(f)

def winkler(earlier, later, threshold):
    score = cython_winkler.winkler(earlier, later)
    return (score, score >= threshold)

def initial(earlier, later, default_initial_score, threshold):
    (e_len, l_len) = (len(earlier), len(later))
    if e_len and l_len and (e_len == 1 or l_len == 1):
        if earlier[0] == later[0]:
            (default_initial_score, True)
    return winkler(earlier, later, threshold)

def window(): pass

def rename_column(column, suffix):
    return '_'.join([column, suffix])

def rename_column_pair(columns):
    return [rename_column(columns[0], '1'), rename_column(columns[1], '2')]

def rename_earlier_column(column):
    return rename_column(column, '1')

def rename_later_column(column):
    return rename_column(column, '2')

def link(earlier_file, later_file, configuration_file, output_file):
    """Link data from an earlier point in time to data from
    a later point in time.

    Parameters
    ----------
    earlier_file : str
        name of file containing data from the earlier time point
    later_file : str
        name of file containing data from the later time point
    configuration_file : str
        name of file containing configuration options in YAML
    output_file : str
        name of file to which results are to be written
    """
    config = load_configuration(configuration_file)
    (earlier_sep, later_sep) = (config['earlier_sep'], config['later_sep'])
    output_sep = config['output_sep']
    chunksize = config['chunksize']
    default_initial_score = config['default_initial_score']
    scorers = {'winkler': winkler, 'initial': partial(initial, default_initial_score=default_initial_score), 'window': window}
    combine_scores = config['combine_scores']
    combined_threshold = config['combined_threshold']

    for function in config['functions']:
        function['columns'] = rename_column_pair(function['columns'])
    new_columns = [function['name'] for function in config['functions']]

    results = None
    earlier_reader = pd.read_csv(earlier_file, dtype=str, sep=earlier_sep, quoting=csv.QUOTE_NONE, na_filter=False, chunksize=chunksize)
    for earlier_df in earlier_reader:
        earlier_df.columns = map(rename_earlier_column, earlier_df.columns)
        later_reader = pd.read_csv(later_file, dtype=str, sep=later_sep, quoting=csv.QUOTE_NONE, na_filter=False, chunksize=chunksize)
        for later_df in later_reader:
            later_df.columns = map(rename_later_column, later_df.columns)
            earlier_df.index = [1] * len(earlier_df)
            later_df.index = [1] * len(later_df)
            product_df = earlier_df.join(later_df)[list(earlier_df.columns) + list(later_df.columns)]
            for function in config['functions']:
                scorer = scorers.get(function['function'], None)
                if scorer is None:
                    raise NotImplementedError("{} not implemented".format(str(function['function'])))
                elif scorer is scorers['window']:
                    columns = function['columns']
                    scores = abs(product_df[columns[0]].astype(int) - product_df[columns[1]].astype(int))
                    product_df[function['name']] = list(scores)
                    passed = scores <= function['threshold']
                else:
                    
                    threshold = function['threshold']
                    results = product_df[function['columns']].apply(lambda row: scorer(earlier=row[0], later=row[1], threshold=threshold), axis=1)
                    product_df[function['name']] = list(results.map(lambda t: t[0]))
                    passed = list(results.map(lambda t: t[1]))
                product_df = product_df[passed]
                if not len(product_df):
                    break
            if len(product_df):
                product_df['weight'] = product_df[combine_scores].sum(axis=1)
                product_df = product_df[product_df['weight'] >= combined_threshold]
            if len(product_df):
                mode = 'a' if os.path.exists(output_file) else 'w'
                header = (mode == 'w')
                product_df.to_csv(output_file, sep=output_sep, mode=mode, header=header, index=False, quoting=csv.QUOTE_NONE)

def main():
    """Parse commandline arguments & link datasets."""
    args = parse_args()
    link(args.earlier_file, args.later_file, args.configuration_file, args.output_file)

if __name__ == '__main__':
    main()
