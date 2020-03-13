import matplotlib.pyplot as plt
import numpy as np


def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def make_barchart(axis, op_scr, ms_scr, x_lbl, idx, rouge_score):
    labels = ['10', '20', 'Full']

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    rects1 = axis.bar(x - width / 2, op_scr, width, label='Opinosis')
    rects2 = axis.bar(x + width / 2, ms_scr, width, label='MSC')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    axis.set_ylabel(rouge_score)
    axis.set_xlabel(x_lbl)
    if idx == 0:
        axis.set_title('Scores by size of data set')
        axis.legend()
    axis.set_xticks(x)
    axis.set_xticklabels(labels)


    autolabel(rects1, axis)
    autolabel(rects2, axis)


if __name__ == '__main__':
    op_op_scores = [0.02915, 0.03582, 0.06663]
    op_ms_scores = [0.00700, 0.03074, 0.04014]
    mi_op_scores = [0.00000, 0.00040, 0.00593]
    mi_ms_scores = [0.00000, 0.00007, 0.00310]
    am_op_scores = [0.00865, 0.00865, 0.00865]
    am_ms_scores = [0.01862, 0.01862, 0.01862]

    op_scores = []
    ms_scores = []
    op_scores.append(op_op_scores)
    op_scores.append(mi_op_scores)
    op_scores.append(am_op_scores)
    ms_scores.append(op_ms_scores)
    ms_scores.append(mi_ms_scores)
    ms_scores.append(am_ms_scores)

    x_labels = ['Opinosis', 'Micropinion', 'Amazon']

    fig, axes = plt.subplots(nrows=3, ncols=1)

    for i in range(len(axes)):
        ax = axes[i]
        op_score = op_scores[i]
        ms_score = ms_scores[i]
        x_label = x_labels[i]
        make_barchart(ax, op_score, ms_score, x_label, i, 'ROUGE-2')

    fig.tight_layout()

    plt.show()

    op_op_scores = [0.02782, 0.05017, 0.10675]
    op_ms_scores = [0.02779, 0.07058, 0.08220]
    mi_op_scores = [0.00001, 0.00022, 0.01165]
    mi_ms_scores = [0.00003, 0.00063, 0.00661]
    am_op_scores = [0.00649, 0.00649, 0.00649]
    am_ms_scores = [0.01548, 0.01548, 0.01548]

    op_scores = []
    ms_scores = []
    op_scores.append(op_op_scores)
    op_scores.append(mi_op_scores)
    op_scores.append(am_op_scores)
    ms_scores.append(op_ms_scores)
    ms_scores.append(mi_ms_scores)
    ms_scores.append(am_ms_scores)

    x_labels = ['Opinosis', 'Micropinion', 'Amazon']

    fig, axes = plt.subplots(nrows=3, ncols=1)

    for i in range(len(axes)):
        ax = axes[i]
        op_score = op_scores[i]
        ms_score = ms_scores[i]
        x_label = x_labels[i]
        make_barchart(ax, op_score, ms_score, x_label, i, 'ROUGE-SU4')

    fig.tight_layout()

    plt.show()


# plt.subplot(2, 1, 2)
# x1 = np.linspace(0.0, 5.0)
# x2 = np.linspace(0.0, 2.0)
#
# y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
# y2 = np.cos(2 * np.pi * x2)
#
# plt.subplot(2, 1, 1)
# plt.plot(x1, y1, 'o-')
# plt.title('A tale of 2 subplots')
# plt.ylabel('Damped oscillation')
#
# plt.subplot(2, 1, 1)
# plt.plot(x2, y2, '.-')
# plt.xlabel('time (s)')
# plt.ylabel('Undamped')
#
# plt.show()
