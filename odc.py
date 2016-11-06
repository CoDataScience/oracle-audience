import os
import random
import smart_open
import pandas as pd
import click


N_POSITIVE = 99684
N_NEGATIVE = 996941
N_TOTAL = N_POSITIVE + N_NEGATIVE
POSITIVE_RATIO = N_POSITIVE / N_TOTAL


def read_submission(file, ordered):
    df = pd.read_csv(file)
    columns = df.columns.values
    if ordered:
        assert len(columns) == 1, 'For ordered scoring there must be only one column'
        assert columns[0] == 'household_id', 'The first column must be household_id'
    else:
        assert len(columns) == 2, 'There must be only two columns'
        assert columns[0] == 'household_id', 'The first column must be household_id'
        assert columns[1] == 'advertise', 'The second column must be advertise'
    return df.sort_values('advertise', ascending=False)['household_id'].values


def read_spends(file):
    spend_lookup = {}
    spenders = set()
    with open(file) as f:
        for l in f:
            hhid, spend = l.strip().split(',')
            hhid = int(hhid)
            spend = float(spend)
            spend_lookup[hhid] = spend
            if spend > 0:
                spenders.add(hhid)
    return spend_lookup, spenders


def compute_revenue(all_hhids, advertise_hhids, spend_lookup):
    revenue = 0
    total_revenue = 0

    for hhid in advertise_hhids:
        revenue += spend_lookup[hhid]

    for hhid in all_hhids:
        total_revenue += spend_lookup[hhid]

    return revenue, total_revenue


def compute_n_responders(all_hhids, advertise_hhids, spenders):
    n_responders = 0
    total_n_responders = 0

    for hhid in advertise_hhids:
        if hhid in spenders:
            n_responders += 1

    for hhid in all_hhids:
        if hhid in spenders:
            total_n_responders += 1

    return n_responders, total_n_responders


@click.group()
def cli():
    pass


@cli.command()
@click.option('--ratio', is_flag=True,
              help='Score by computing top K using ratio instead of K=100,000')
@click.option('--ordered', is_flag=True,
              help='Accept submission as ordered list of hhids from most to least likely to spend')
@click.argument('spend_file')
@click.argument('submission_file')
def score(ratio, ordered, spend_file, submission_file):
    spend_lookup, spenders = read_spends(spend_file)

    ordered_hhids = read_submission(submission_file, ordered)
    if ratio:
        n_examples = len(ordered_hhids)
        n_advertise = int(n_examples * POSITIVE_RATIO)
        print("Using {} total examples, expecting exactly {} advertisements".format(
            n_examples, n_advertise))
    else:
        n_advertise = 100000

    advertize_hhids = ordered_hhids[0:n_advertise]

    revenue, total_revenue = compute_revenue(ordered_hhids, advertize_hhids, spend_lookup)
    n_responders, n_total_responders = compute_n_responders(
        ordered_hhids, advertize_hhids, spenders)

    print('Revenue:', revenue)
    print('Possible Revenue:', total_revenue)
    print('Fraction of Possible Revenue:', revenue / total_revenue)
    print('Number of Responders:', n_responders)
    print('Possible Number of Responders:', n_total_responders)
    print('Fraction of Possible Responders', n_responders / n_total_responders)


def is_positive_example(line):
    fields = line.split(',')
    return float(fields[1]) != 0


@cli.command()
@click.option('--seed', type=int)
@click.argument('n_samples', type=int)
@click.argument('input_path', type=str)
@click.argument('output_path', type=str)
def sample(seed, n_samples, input_path, output_path):
    if os.path.isdir(input_path):
        print('Directory detected, using all files in directory')
        files = [smart_open.smart_open(os.path.join(input_path, p)) for p in os.listdir(input_path)]
    else:
        print('Single file detected')
        files = [smart_open.smart_open(input_path)]

    output = open(output_path, 'w')

    if seed is not None:
        random.seed(seed)

    total_positive = int(n_samples * POSITIVE_RATIO)
    total_negative = n_samples - total_positive

    print('Finding a total of {} examples, {} positive and {} negative'.format(
        n_samples, total_positive, total_negative))

    n_positive = 0
    n_negative = 0

    while n_positive + n_negative < n_samples:
        if len(files) == 0:
            raise Exception('There are not enough files to get {} examples'.format(n_samples))
        random_index = random.randrange(len(files))
        random_file = files[random_index]
        try:
            line = next(random_file).decode('utf8')
        except StopIteration:
            random_file.close()
            files.pop(random_index)

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
