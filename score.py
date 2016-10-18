import sys
import pandas as pd


def read_submission(file):
    df = pd.read_csv(file)
    columns = df.columns.values
    assert len(columns) == 2, 'There must be only two columns'
    assert columns[0] == 'household_id', 'The first column must be household_id'
    assert columns[1] == 'advertise', 'The second column must be advertise'
    assert len(df[df['advertise'] != 0]) == 100000, 'There must be exactly 100,000 non-zeros'
    return df


def read_spends(file):
    spend_lookup = {}
    total_possible = 0
    total_responders = 0
    with open(file) as f:
        for l in f:
            hhid, spend = l.strip().split(',')
            hhid = int(hhid)
            spend = float(spend)
            spend_lookup[hhid] = spend
            total_possible += spend
            if spend > 0:
                total_responders += 1
    return spend_lookup, total_possible, total_responders

def filter_advertise(submission):
    return submission[submission['advertise'] != 0]


def compute_revenue(submission, spend_lookup):
    revenue = 0

    for ix, row in submission.iterrows():
        revenue += spend_lookup[row.household_id]

    return revenue


def compute_n_responders(submission, spend_lookup):
    n_responders = 0

    for ix, row in submission.iterrows():
        if row.household_id in spend_lookup:
            n_responders += 1

    return n_responders


if __name__ == '__main__':
    spend_file = sys.argv[1]
    submission_file = sys.argv[2]

    spend_lookup, total_possible, total_responders = read_spends(spend_file)

    raw_submission = read_submission(submission_file)
    filtered_submission = filter_advertise(raw_submission)

    revenue = compute_revenue(filtered_submission, spend_lookup)
    n_responders = compute_n_responders(filtered_submission, spend_lookup)

    print('Revenue:', revenue)
    print('Fraction of Possible Revenue:', revenue / total_possible)
    print('Number of Responders:', n_responders)
    print('Fraction of Possible Responders', n_responders / total_responders)

