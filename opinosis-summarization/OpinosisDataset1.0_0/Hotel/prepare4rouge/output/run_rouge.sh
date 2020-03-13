for path in *.xml
do
    name="${path##*/}"
    filename="${name%%.*}"
    ROUGE-1.5.5.pl -e "$ROUGE_EVAL_HOME" -f "A" -a -x -s -m -2 -4 -u -n "2" "$path" >> "../results/myresults_021103.txt"
done
