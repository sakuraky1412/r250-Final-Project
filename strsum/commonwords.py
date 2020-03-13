import collections
import pandas as pd
import matplotlib.pyplot as plt
# matplotlib inline
# Read input file, note the encoding is specified here
# It may be different in your text file
file = open('full.raw', encoding="utf8")
a= file.read()
# Stopwords
# stopwords = set(line.strip() for line in open('stopwords.txt'))
# stopwords = stopwords.union({'mr', 'mrs', 'one', 'two', 'said'})
# Instantiate a dictionary, and for every word in the file,
# Add to the dictionary if it doesn't exist. If it does, increase the count.
wordcount = {}
# To eliminate duplicates, remember to split by punctuation, and use case demiliters.
for word in a.lower().split():
    word = word.replace(".","")
    word = word.replace(",","")
    word = word.replace(":","")
    word = word.replace("\"","")
    word = word.replace("!","")
    word = word.replace("â€œ","")
    word = word.replace("â€˜","")
    word = word.replace("*","")
    # if word not in stopwords:
    if word not in wordcount:
        wordcount[word] = 1
    else:
        wordcount[word] += 1
# Print most common word
n_print = 1000
print("\nOK. The {} most common words are as follows\n".format(n_print))
word_counter = collections.Counter(wordcount)
text_file = open("am_stopwords.txt", "w")
for word, count in word_counter.most_common(n_print):
    text_file.write(word)
    print(word, ": ", count)
text_file.close()
# Close the file
file.close()
# Create a data frame of the most common words
# Draw a bar chart
# lst = word_counter.most_common(n_print)
# df = pd.DataFrame(lst, columns = ['Word', 'Count'])
# df.plot.bar(x='Word',y='Count')