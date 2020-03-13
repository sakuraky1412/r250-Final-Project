# r250-Final-Project
Comparison of Opinosis and Multi-Sentence Compression

# Final paper readme
This repository contains the implementations of [Opinosis](https://www.semanticscholar.org/paper/Opinosis%3A-A-Graph-Based-Approach-to-Abstractive-of-Ganesan-Zhai/129c96e900c5b0f4d41f449a89305d9cf91a1d1c) in the directory `opinosis-summarization`	 and [Multi-Sentence Compression](https://www.semanticscholar.org/paper/Multi-Sentence-Compression%3A-Finding-Shortest-Paths-Filippova/6872792acbfcafc900c79d2a2c0fb66afaa5ee5e) in the directory `Multi-Sentence-Compression`. 
Also, input data sets, outputs in the two directories listed above and preprocessing scripts in the directory `strsum`. 
Below are some run commands for reference, but they are not organized. 
Opinosis settings can be found in `/opinosis-summarization/OpinosisSummarizer-1.0/opinosis_sample/etc/opinosis.properties`

## Opinosis

1. Stanford parser
```
./stanford-postagger.sh models/english-left3words-distsim.tagger sample-input.txt

java -cp stanford-postagger.jar edu.stanford.nlp.process.DocumentPreprocessor sample.txt 


for F in topics/*.txt.data; do ./stanford-postagger.sh models/english-left3words-distsim.tagger "${F}"; done

parse-opinosis.sh

parse-opinosis.py
```

2. Run opinosis
```
change properties

java -jar opinosis.jar -b opinosis_sample/
java -jar opinosis.jar -b micropinion/
java -jar opinosis.jar -b opinosis_10/
java -jar opinosis.jar -b op_op_20/
java -jar opinosis.jar -b am_op_f/
java -jar opinosis.jar -b mi_op_10/
```
4. Run rouge
```
perl prepare4rouge.pl

ROUGE-1.5.5.pl -e data -f A -a -x -s -m -2 -4 -u output/settings1.xml
ROUGE-1.5.5.pl -e data -f A -a -x -s -m -2 -4 -u settings1.xml
ROUGE-1.5.5.pl -e data -f A -a -x -s -m -2 -4 -u -n 2 < your-project-name>/settings.xml

ROUGE-1.5.4.pl -e data -c 95 -2 -1 -U -r 1000 -n 4 -w 1.2 -a ROUGE-test.xml


./run_rouge.sh

perl rouge2csv.pl results/myresults.txt TEST
```

## Multi-sentence 
1. parameter
```
PathCompressor.MIN_DEPTH

gradle clean run
```

## permutation test
```
permtest 020503.csv group_names Opinosis10 -t MULTISEN > 020503.txt

```
