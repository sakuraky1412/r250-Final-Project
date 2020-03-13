import os

import pandas as pd
import csv
from mlxtend.evaluate import permutation_test


def rouge_results2csv(txt_filepath):
    # 'rouge_results/myresults_020503_test.txt'
    read_file = pd.read_csv(txt_filepath,
                            names=["experiment", "rouge_type", "score_type", "score", "confidence_level", "level1", "-",
                                   "level2"], header=None, delim_whitespace=True)
    csv_filepath = os.path.splitext(txt_filepath)[0] + '.csv'
    read_file.to_csv(csv_filepath)
    with open(csv_filepath, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        cur_experiment = ""
        cur_rouge2_score = 0
        cur_rougesu_score = 0
        with open('rouge_results/020503.csv', mode='w') as csv_file:
            fieldnames = ['ROUGE-2', 'ROUGE-SU*', 'group_names']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for i, row in enumerate(csv_reader):
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    # line_count += 1
                if cur_experiment != row["experiment"] and i != 0:
                    writer.writerow(
                        {'ROUGE-2': cur_rouge2_score, 'ROUGE-SU*': cur_rougesu_score, 'group_names': cur_experiment})
                cur_experiment = row["experiment"]
                if row["rouge_type"] == "ROUGE-2" and row["score_type"] == "Average_F:":
                    cur_rouge2_score = row["score"]
                if row["rouge_type"] == "ROUGE-SU*" and row["score_type"] == "Average_F:":
                    cur_rougesu_score = row["score"]
                line_count += 1
            print(f'Processed {line_count} lines.')


def extract_rouge_results(txt_filepath):
    read_file = pd.read_csv(txt_filepath,
                            names=["experiment", "rouge_type", "score_type", "score", "confidence_level", "level1", "-",
                                   "level2"], header=None, delim_whitespace=True)
    csv_filepath = os.path.splitext(txt_filepath)[0] + '.csv'
    read_file.to_csv(csv_filepath)
    experiment2score_lists = {}
    experiments = set()
    with open(csv_filepath, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for i, row in enumerate(csv_reader):
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                # line_count += 1
            cur_experiment = row["experiment"]
            experiments.add(cur_experiment)
            if cur_experiment not in experiment2score_lists:
                experiment2score_lists[cur_experiment] = [[],[]]
            if row["rouge_type"] == "ROUGE-2" and row["score_type"] == "Average_F:":
                experiment2score_lists[cur_experiment][0].append(float(row["score"]))
            if row["rouge_type"] == "ROUGE-SU*" and row["score_type"] == "Average_F:":
                experiment2score_lists[cur_experiment][1].append(float(row["score"]))
            line_count += 1
        print(f'Processed {line_count} lines.')
    return experiments, experiment2score_lists

if __name__ == '__main__':
    # rouge_results2csv()
    experiments, experiment2score_lists = extract_rouge_results('rouge_results/am2.txt')
    for experiment in experiments:
        treatment_rouge2scores = experiment2score_lists[experiment][0]
        treatment_rougesuscores = experiment2score_lists[experiment][1]
        for ref_experiment in experiments:
            if experiment == ref_experiment:
                continue
            control_rouge2scores = experiment2score_lists[ref_experiment][0]
            control_rougesuscores = experiment2score_lists[ref_experiment][1]
            # treatment = [28.44, 29.32, 31.22, 29.58, 30.34, 28.76, 29.21, 30.4,
            #              31.12, 31.78, 27.58, 31.57, 30.73, 30.43, 30.31, 30.32,
            #              29.18, 29.52, 29.22, 30.56]
            # control = [33.51, 30.63, 32.38, 32.52, 29.41, 30.93, 49.78, 28.96,
            #            35.77, 31.42, 30.76, 30.6, 23.64, 30.54, 47.78, 31.98,
            #            34.52, 32.42, 31.32, 40.72]
            rouge2_p_value = permutation_test(treatment_rouge2scores, control_rouge2scores,
                                       method='approximate',
                                       num_rounds=10000,
                                       seed=0)
            rougesu_p_value = permutation_test(treatment_rougesuscores, control_rougesuscores,
                                              method='approximate',
                                              num_rounds=10000,
                                              seed=0)
            if rouge2_p_value < 0.1:
                print("%s, %s, rouge2" % (experiment, ref_experiment))
                print(rouge2_p_value)
            if rougesu_p_value < 0.1:
                print("%s, %s, rougesu" % (experiment, ref_experiment))
                print(rougesu_p_value)