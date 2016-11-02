# oracle-audience

This CLI tool `odc` and python script is meant to be used for the Oracle Audience Competition. Below are usage
instructions

## Installation

This script has been tested with Python 3.5

```bash
$ git clone git@github.com:CoDataScience/oracle-audience.git
$ python setup.py install
```

## Usage

```bash
$ odc --help
Usage: odc [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  sample
  score
```

### Scoring

Using files in the correct input format and using the spend files provided in slack

```bash
$ odc score --help
Usage: odc score [OPTIONS] SPEND_FILE SUBMISSION_FILE

Options:
  --ratio  Score by computing top K using ratio instead of K=100,000
  --help   Show this message and exit.
```

```bash
$ odc score data/all_val_spend.csv vw_data/submission.csv
```

Below is sample output

```
Revenue: 10184379.730004184
Fraction of Possible Revenue: 0.6169140659646304
Number of Responders: 57033
Fraction of Possible Responders 0.5721379559407729
```

If you are using sampled data then the first file should only include what you want to score against
and you should use the `--ratio` flag. Otherwise its expected you give exactly 100,000 advertisements

### Sampling Data

For convenience there is also a script to sample data so you can model on smaller datasets that
have the correct class balance. This script was used to generate the sampled data provided and can
be used as below

```bash
$ odc sample --help
Usage: odc sample [OPTIONS] N_SAMPLES INPUT_PATH OUTPUT_PATH

Options:
  --seed INTEGER
  --help          Show this message and exit.
```

```bash
$ odc sample 10000 data/train data/sampled_train.txt
```

This will sample 10000 examples from data files that are in `data/train`. The files in there can be
decompressed or still compressed in bz2 format. The script handles both.
