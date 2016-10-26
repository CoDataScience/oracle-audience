import os
import glob
import random
import smart_open
import pandas as pd
import click


N_POSITIVE = 99684
N_NEGATIVE = 996941
N_TOTAL = N_POSITIVE + N_NEGATIVE
POSITIVE_RATIO = N_POSITIVE / N_TOTAL


def read_submission(file, n_advertise):
    df = pd.read_csv(file)
    columns = df.columns.values
    assert len(columns) == 2, 'There must be only two columns'
    assert columns[0] == 'household_id', 'The first column must be household_id'
    assert columns[1] == 'advertise', 'The second column must be advertise'
    n_found = len(df[df['advertise'] != 0])
    assert n_found == n_advertise, 'There must be exactly {} non-zeros and found {}'.format(
        n_advertise, n_found)
    return df


def read_spends(file):
    spend_lookup = {}
    total_possible = 0
    spenders = set()
    with open(file) as f:
        for l in f:
            hhid, spend = l.strip().split(',')
            hhid = int(hhid)
            spend = float(spend)
            spend_lookup[hhid] = spend
            total_possible += spend
            if spend > 0:
                spenders.add(hhid)
    return spend_lookup, total_possible, spenders


def filter_advertise(submission):
    return submission[submission['advertise'] != 0]


def compute_revenue(submission, spend_lookup):
    revenue = 0

    for ix, row in submission.iterrows():
        revenue += spend_lookup[row.household_id]

    return revenue


def compute_n_responders(submission, spenders):
    n_responders = 0

    for ix, row in submission.iterrows():
        if row.household_id in spenders:
            n_responders += 1

    return n_responders


@click.group()
def cli():
    pass


@cli.command()
@click.option('--ratio', is_flag=True,
              help='Score by computing top K using ratio instead of K=100,000')
@click.argument('spend_file')
@click.argument('submission_file')
def score(ratio, spend_file, submission_file):
    spend_lookup, total_possible, spenders = read_spends(spend_file)

    if ratio:
        n_examples = len(spend_lookup)
        n_advertise = int(n_examples * POSITIVE_RATIO)
        print("Using {} total examples, expecting exactly {} advertisements".format(
            n_examples, n_advertise, POSITIVE_RATIO))
    else:
        n_advertise = 100000

    raw_submission = read_submission(submission_file, n_advertise)
    filtered_submission = filter_advertise(raw_submission)

    revenue = compute_revenue(filtered_submission, spend_lookup)
    n_responders = compute_n_responders(filtered_submission, spenders)

    print('Revenue:', revenue)
    print('Fraction of Possible Revenue:', revenue / total_possible)
    print('Number of Responders:', n_responders)
    print('Fraction of Possible Responders', n_responders / len(spenders))


def is_positive_example(line):
    fields = line.split(',')
    return float(fields[1]) != 0


@cli.command()
@click.option('--seed')
@click.argument('n_samples', type=int)
@click.argument('input_path', type=str)
@click.argument('output_path', type=str)
def sample(seed, n_samples, input_path, output_path):
    if os.path.isdir(input_path):
        print('Directory detected, using all files in directory')
        glob_path = os.path.join(input_path, '/*')
        files = [smart_open.smart_open(p) for p in glob.glob(glob_path)]
    else:
        print('Single file detected')
        files = [smart_open.smart_open(input_path)]

    output = open(output_path, 'w')

    if seed is not None:
        random.seed(seed)

    examples = []
    total_positive = int(n_samples * POSITIVE_RATIO)
    total_negative = n_samples - total_positive

    n_positive = 0
    n_negative = 0

    while len(examples) < n_samples:
        random_file = random.choice(files)
        try:
            line = next(random_file).decode('utf8')
        except StopIteration:
            continue

        is_positive = is_positive_example(line)

        if is_positive and n_positive < total_positive:
            output.write(line)
            n_positive += 1
            continue

        if not is_positive and n_negative < total_negative:
            output.write(line)
            n_negative += 1
            continue

    for f in files:
        f.close()

    output.close()

if __name__ == '__main__':
    cli()
