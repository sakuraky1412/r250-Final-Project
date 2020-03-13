import os
import re
import sys


def preprocess_output(dir):
    for filename in os.listdir(dir):
        # , encoding='windows-1252'
        with open(os.path.join(dir, filename)) as f:
            content = f.readlines()
            text_file = open("AmazonDataset/20-pre-parsed/%s" % filename, "w")
            for line in content:
                line = line.lower()
                line += "\n"
                text_file.write(line)
            text_file.close()


def postprocess_output(dir):
    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename)) as f:
            content = f.readlines()
            text_file = open("HotelDataset/f-parsed/%s" % filename, "w")
            for line in content:
                line = line.replace("_", "/")
                line += "\n"
                # print(line)
                text_file.write(line)
            text_file.close()


def data_stats(dir):
    sen_sum = 0
    avg_sen_len_sum = 0
    topic_num = len(os.listdir(dir))
    print("Topic number: %d" % topic_num)
    for filename in os.listdir(dir):
        # , encoding='windows-1252'
        with open(os.path.join(dir, filename), encoding='windows-1252') as f:
            content = f.readlines()
            sen_num = len(content)
            # print("Sentence number: %d" % sen_num)
            sum = 0
            for line in content:
                word_num = len(line.split(" "))
                # print("Word number: %d" % word_num)
                sum += word_num
            avg_sen_len = sum / sen_num
            # print("Average sentence length is %f" % avg_sen_len)
            avg_sen_len_sum += avg_sen_len
            sen_sum += sen_num
    print("Average sentence length across all data is %f" % (avg_sen_len_sum / topic_num))
    print("Average sentence number is %f" % (sen_sum / topic_num))


def summary_stats(dir):
    sen_sum = 0
    avg_sen_len_sum = 0
    topic_num = len(os.listdir(dir)) - 1
    print("Topic number: %d" % topic_num)
    for dirname in os.listdir(dir):
        if dirname != ".DS_Store":
            avg_sen_sum = 0
            avg_avg_sen_len_sum = 0
            summary_num = len(os.listdir(os.path.join(dir, dirname)))
            # print("Summary number: %d" % summary_num)
            for filename in os.listdir(os.path.join(dir, dirname)):
                # , encoding='windows-1252'
                with open(os.path.join(dir, dirname, filename)) as f:
                    content = f.readlines()
                    # content.remove("\n")
                    sen_num = len(content)
                    # print("Sentence number: %d" % sen_num)
                    sum = 0
                    for line in content:
                        words = line.split(" ")
                        if "," in words:
                            words.remove(",")
                        word_num = len(words)
                        # print("Word number: %d" % word_num)
                        sum += word_num
                    avg_sen_len = sum / sen_num
                    # print("Average sentence length is %f" % avg_sen_len)
                    avg_avg_sen_len_sum += avg_sen_len
                    avg_sen_sum += sen_num
            avg_sen_len_sum += avg_avg_sen_len_sum / summary_num
            sen_sum += avg_sen_sum / summary_num
    print("Average sentence length across all data is %f" % (avg_sen_len_sum / topic_num))
    print("Average sentence number is %f" % (sen_sum / topic_num))


BEAM_SIZE = 2


def process_output(output_filename):
    with open(output_filename) as f:
        content = f.readlines()
    text_file = open("split_output.txt", "w")
    large_set = []
    for line in content:
        split_lines = line.split("In city is ")
        small_set = []
        for split_line in split_lines:
            if split_line == ".\n":
                split_line = ""
            split_line += "\n"
            if split_line != "\n":
                small_set.append(split_line)
            text_file.write(split_line)
        large_set.append(small_set)
    text_file.close()
    return large_set


def sim(dir, length):
    for filename in os.listdir(dir):
        # , encoding = 'windows-1252'
        with open(os.path.join(dir, filename)) as f:
            content = f.readlines()
            result_file = open("HotelDataset/20-raw/%s" % filename, "w")
            precision_scores = []
            for cur_line in content:
                cur_line = cur_line.strip()
                precision_score = 0
                for other_line in content:
                    other_line = other_line.strip()
                    precision_score += precision(other_line, cur_line)
                precision_scores.append([precision_score, cur_line])
            precision_scores.sort(key=lambda tup: tup[0], reverse=True)
            for i in range(length):
                if i < len(precision_scores):
                    result_file.write(precision_scores[i][1] + "\n")
        result_file.close()


def range_voting(prob_filename, lstm_filename, large_set):
    with open(prob_filename) as f:
        probs = f.readlines()
    with open(lstm_filename) as f:
        lstms = f.readlines()

    assert len(large_set) == len(lstms)
    lstm_text_file = open("lstm_res.txt", "w")
    for i in range(len(lstms)):
        assert int(lstms[i]) < len(large_set)
        if len(large_set[i]) <= int(lstms[i]):
            lstm_text_file.write(large_set[i][0])
        else:
            lstm_text_file.write(large_set[i][int(lstms[i])])
    lstm_text_file.close()

    large_prob_set = []
    small_prob_set = []
    for prob in probs:
        if prob != "\n":
            small_prob_set.append(prob)
        else:
            large_prob_set.append(small_prob_set)

    assert len(large_set) == len(large_prob_set)
    precision_text_file = open("precision_res.txt", "w")
    overlap_text_file = open("overlap_res.txt", "w")
    for i in range(len(large_set)):
        cur_output_set = large_set[i]
        cur_prob_set = large_prob_set[i]
        if len(cur_output_set) != BEAM_SIZE:
            precision_text_file.write(cur_output_set[0])
            overlap_text_file.write(cur_output_set[0])
            continue
        precision_scores = []
        overlap_scores = []
        for j in range(len(cur_output_set)):
            cur_output = cur_output_set[j].strip()
            precision_score = 0
            overlap_score = 0
            for k in range(len(cur_output_set)):
                other_output = cur_output_set[k].strip()
                other_prob = cur_prob_set[k].strip()
                precision_score += float(other_prob) * precision(other_output, cur_output)
                overlap_score += float(other_prob) * overlap(other_output, cur_output)
            precision_scores.append([precision_score, cur_output])
            overlap_scores.append([overlap_score, cur_output])

        precision_scores.sort(key=lambda tup: tup[0])
        overlap_scores.sort(key=lambda tup: tup[0])
        precision_text_file.write(precision_scores[0][1] + "\n")
        overlap_text_file.write(overlap_scores[0][1] + "\n")
    precision_text_file.close()
    overlap_text_file.close()


def precision(s, t):
    bag_s = bag(s)
    bag_t = bag(t)
    return len(set(bag_s).intersection(bag_t)) / len(bag_s)


def overlap(s, t):
    set_s = set(bag(s))
    set_t = set(bag(t))
    return len(set_s.intersection(set_t)) / len(set_s)


def bag(s):
    bag = s.split(" ")
    if "." in bag:
        bag.remove(".")
    return bag


def sim_list(lst):
    precision_scores = []
    for cur_line in lst:
        cur_line = cur_line.strip()
        precision_score = 0
        for other_line in lst:
            other_line = other_line.strip()
            precision_score += precision(other_line, cur_line)
        precision_scores.append([precision_score, cur_line])
    precision_scores.sort(key=lambda tup: tup[0], reverse=True)
    # print number of sentences
    # print("number of sentences: %d" % len(precision_scores))
    # print sentence length
    gold = []
    raw = []
    i = 0
    while i < len(precision_scores) and i < 10:
        cur_sen = precision_scores[i][1]
        if len(cur_sen.split(" ")) < 16:
            gold.append(cur_sen)
        else:
            raw.append(cur_sen)
        i += 1
    if len(gold) == 0:
        gold.append(precision_scores[0][1])
        raw.remove(precision_scores[0][1])
    while i < len(precision_scores):
        raw.append(precision_scores[i][1])
        i += 1
    return gold, raw
        #     print(precision_scores[i][1] + "\n")
        #     print("sentence length: %d" % len(precision_scores[i][1].split(" ")))


def parse_micropinion_gold(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename)) as f:
                #         filename = '160gb-onetouch-external-hard-drive-and-backup-system-firewire-and-usb-2.0-1.1.raw'
                #         with open(os.path.join(dir, filename)) as f:
                content = f.read()
                reviews = content.split("$$;")
                gold = []
                for review in reviews:
                    if "Summary:." in review:
                        # Pros:. Good paper manual, smart and simple use.
                        # Cons:. Needs proper care as all external disk drives do !.
                        # Summary:. My Maxtor OneTouch 160G works as advertised.
                        s = 'asdf=5;iwantthis123jasd'
                        if "Pros:." in review and "Cons:." in review:
                            pro = re.search('Pros:\. (.*)\.', review).group(1)
                            con = re.search('Cons:\. (.*)\.', review).group(1)
                            gold.append(pro + "; " + con + "\n")
                            # print(pro + "; " + con)

            # get top 10 similarity sentences
            if len(gold) != 0:
                # print("filename: %s" % filename)
                gold_summaries, raw_sentences = sim_list(gold)
                # put the rest of the sentences into the raw file
                # filename: windows-2000-professional-edition.raw
                # number of sentences: 4
                # put 2 sentences into each of the summary files
                directory = "MicropinionDataset/summaries-gold/"
                name = os.path.splitext(filename)[0]
                path = os.path.join(directory, name)
                if not os.path.isdir(path):
                    os.mkdir(path)

                line_num = int(len(gold_summaries) / 5) + 1

                for i in range(0, len(gold_summaries), line_num):
                    result_file = open(os.path.join(path, name + "." + str(i) + ".gold"), "w")
                    for j in range(i, i + line_num):
                        if j < len(gold_summaries):
                            result_file.write(gold_summaries[j] + "\n")
                            # print(gold[j])
                    result_file.close()

                directory = "MicropinionDataset/pre-processed-copy/"
                name = os.path.splitext(filename)[0] + ".data"
                path = os.path.join(directory, name)
                raw_file = open(path, "a")
                for sentence in raw_sentences:
                    raw_file.write(sentence + "\n")
                raw_file.close()

def preprocess_amazon_raw(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename)) as f:
                content = f.readlines()
                text_file = open("AmazonDataset/pre-processed-raw/%s" % filename, "w")
                for line in content:
                    if line != "\n":
                        lines = line.split(".")
                        for l in lines:
                            l = l.strip()
                            if l != "":
                                text_file.write(l + ".\n")
                text_file.close()


def preprocess_amazon_summaries(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename + "/" + filename + ".gold")) as f:
                content = f.readlines()
                # content = content.replace("\n", " , ")
                # text_file = open(os.path.join("AmazonDataset/pre-processed-summaries-gold", filename + "/" + filename + ".gold"),
                #                  "w")
                # text_file.write(content)
                # text_file.close()

                # line_num = int(len(gold_summaries) / 5) + 1
                print(content)
                for i in range(0, len(content), 2):
                    result_file = open(
                        os.path.join("AmazonDataset/pre-processed-summaries-gold", filename + "/" + filename + "." + str(i) + ".gold"),
                                         "w")
                    for j in range(i, i + 2):
                        if j < len(content):
                            result_file.write(content[j])
                            print(content[j])
                    result_file.close()


def process_hotel(filename):
    with open(filename) as f:
        content = f.readlines()
        for line in content:
            split_line = line.split("\t\t")
            user_ID = split_line[0]
            review = split_line[1]
            reviews = review.split("<sssss>")
            summary = split_line[2]

            reviews_len = len(reviews)
            if reviews_len >= 20 and reviews_len < 25:
                sum = 0
                for r in reviews:
                    r_words = r.split(" ")
                    sum += len(r_words)
                if sum / reviews_len > 20:
                    summary_words = summary.split(" ")
                    summary_len = len(summary_words)
                    if summary_len >= 15 and summary_len < 20:
                        text_file = open("HotelDataset/raw/%s" % user_ID, "w")
                        for r in reviews:
                            r = r.strip()
                            text_file.write(r + "\n")
                        text_file.close()

                        path = os.path.join("HotelDataset/summaries-gold/", user_ID)
                        if not os.path.isdir(path):
                            os.mkdir(path)

                        text_file = open(
                            os.path.join("HotelDataset/summaries-gold", user_ID + "/" + user_ID + ".gold"), "w")
                        text_file.write(summary)
                        text_file.close()


def split_10(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename)) as f:
                content = f.readlines()
                text_file = open("HotelDataset/10-parse/%s" % filename, "w")
                for i in range(10):
                    if i < len(content):
                        text_file.write(content[i])
                text_file.close()

def split_half(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename)) as f:
                content = f.readlines()
                text_file = open("MicropinionDataset/mi-10-parsed/%s" % filename, "w")
                for i in range(int(len(content)/2)):
                    text_file.write(content[i])
                text_file.close()


def check_length(dir):
    for filename in os.listdir(dir):
        if filename != ".DS_Store":
            with open(os.path.join(dir, filename)) as f:
                content = f.read()
                # content = f.readlines()
                # if len(content) < 19:
                #     print("not pass %s" % filename)
                if 'and' in content and 'but' in content:
                    print("and but %s" % filename)
                elif 'and' in content:
                    print("and %s" % filename)
                elif 'but' in content:
                    print("but %s" % filename)

if __name__ == '__main__':
    # preprocess_output('OpinosisDataset/20-raw')
    # split_10('HotelDataset/20-parse')
    # check_length('stitching/OP_OP_F')
    # check_length('stitching/OP_MS_F')
    print(len(["a", "able", "about", "above", "after", "all", "also", "an",
                "and", "any", "as", "ask", "at", "back", "bad", "be", "because", "beneath", "big", "but", "by",
                "call", "can", "case", "child", "come", "company", "could", "day", "different", "do", "early", "even",
                "eye", "fact", "feel", "few", "find", "first", "for", "from", "get", "give", "go", "good",
                "government", "great", "group", "hand", "have", "he", "her", "high", "him", "his", "how", "i", "if",
                "important", "in", "into", "it", "its", "just", "know", "large", "last", "leave", "life", "like",
                "little", "long", "look", "make", "man", "me", "most", "my", "new", "next", "no", "not", "now",
                "number", "of", "old", "on", "one", "only", "or", "other", "our", "out", "over", "own", "part",
                "people", "person", "place", "point", "problem", "public", "right", "same", "say", "see", "seem",
                "she", "small", "so", "some", "take", "tell", "than", "that", "the", "their", "them", "then", "there",
                "these", "they", "thing", "think", "this", "time", "to", "try", "two", "under", "up", "us", "use",
                "want", "way", "we", "week", "well", "what", "when", "which", "who", "will", "with", "woman", "work",
                "world", "would", "year", "you", "young", "your"]))
    # split_half('MicropinionDataset/mi-20-parsed')
    # postprocess_output('HotelDataset/f-parse')
    # data_stats('AmazonDataset/raw3')
    # summary_stats('AmazonDataset/pre-processed-summaries-gold')
    # sim('HotelDataset/raw', 20)
    # parse_micropinion_gold('MicropinionDataset/raw')
    # preprocess_amazon_raw("AmazonDataset/raw")
    # preprocess_amazon_summaries("AmazonDataset/summaries-gold")
    # process_hotel('HotelDataset/full')
