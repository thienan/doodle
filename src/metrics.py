# coding: utf-8

"""
モデルの評価指針となるメトリクスを計算するモジュールです。

カテゴリ分類器でよくもちいられるメトリックを計算します。まず以下の4つの統計量を出します。

    True  Ppsitive   : ポジティブな予測が正解だった数。
    True  Negative   : ネガティブな予測が正解だった数。
    False Positive   : ポジティブな予測が不正解だった数。
    False Negative   : ネガティブな予測が不正解だった数。

メトリクスは以下の4つを計算します。

    Accuracy  : 正解率。(TP+TN)/(TP+TN+FP+FN)
    Precition : 適合率。予測が正のもののうち、正解も正だった割合。TP/(TP+FP)
    Recall    : 再現率。正解が正のもののうち、予測が正だった割合。TP/(TP+FN)
    F-Measure : F値。適合率と再現率の調和平均。

Accuracyは正解した割合です。わかりやすいので精度として扱われることの多い値です。
ただ、不正解には「負を正としてしまった(FP)」か、「正を負としてしまった(FN)」の二種類があります。
Accuracyではどちらで間違えているのかがわかりません。

2つの間違いの違いはよく病気の誤診で説明されます。
    - 「病気じゃないのに病気と診断した(FP)」
    - 「病気だったのに病気じゃないと診断した(FN)」
両者は明らかに深刻度が異なります。
前者は「間違えました」で済まされるかもしれませんが、後者は重い病気であれば大変なミスになります。

そこで、適合率と再現率を見ます。

適合率は、予測が正のもののうち正解も正だった割合なので、上記例であれば「病気だと診断した時に、本当に病気だった割合」です。
再現率は、正解が正のもののうち予測が正だった割合なので、上記例であれば「病気の人を、病気と予測できた割合」です。

病気の患者を漏れなく発見することが重要な場合、再現率が重要となります。
適合率と再現率はトレードオフになることが多いです。
両者のどちらが重要なのかは、ケースによります。誤診の例では再現率でしたが、必ずしも再現率が重要とは限りません。
手書き数字ではぶっちゃけどっちでもあまり関係ありませんが、計算しておきましょう。
また、両者のバランスをとった指針としてF値というものがあります。

それぞれ、マクロ平均とマイクロ平均を計算します。

    Macro Average : クラスごとに計算した値の平均
    Micro Average : 全クラスの結果を合計して計算した値

マイクロ平均は全体の結果なので計算しやすくわかりやすいですが、データ数の多いクラスの重みが大きくなります。
クラスごとに出現頻度が異なるケースで、それを加味した値を計算したい場合はマイクロ平均での結果が必要ですが、
クラスごとに平等に値を計算したい場合は、マクロ平均を用います。
"""

import tensorflow as tf

def add_summary(labels, classes, num_classes):
    cm = tf.confusion_matrix(labels, classes, num_classes=num_classes, dtype=tf.float32)
    ln = tf.reduce_sum(cm)
    tp = tf.diag_part(cm)
    fp = tf.reduce_sum(cm, axis=1) - tp
    fn = tf.reduce_sum(cm, axis=0) - tp
    tn = ln - tp - fp - fn
    eps = tf.convert_to_tensor(1e-7)
    micro_metrics(tp, fp, tn, fn, eps)
    macro_metrics(tp, fp, tn, fn, num_classes, eps)

def micro_metrics(tp, fp, tn, fn, eps):
    tp_sum = tf.reduce_sum(tp)
    fp_sum = tf.reduce_sum(fp)
    tn_sum = tf.reduce_sum(tn)
    fn_sum = tf.reduce_sum(fn)
    accuracy  = (tp_sum + tn_sum) / (tp_sum + fp_sum + tn_sum + fn_sum)
    precision = tp_sum / (tp_sum + fp_sum + eps)
    recall    = tp_sum / (tp_sum + fn_sum + eps)
    f_measure = 2 * precision * recall / (precision + recall + eps)
    
    family = 'micro_metrics'
    tf.summary.scalar('accuracy' , accuracy , family=family)
    tf.summary.scalar('precision', precision, family=family)
    tf.summary.scalar('recall'   , recall   , family=family)
    tf.summary.scalar('f_measure', f_measure, family=family)

def macro_metrics(tp, fp, tn, fn, num_classes, eps):
    accuracies = (tp + tn) / (tp + fp + tn + fn)
    precisions = tp / (tp + fp + eps)
    recalls    = tp / (tp + fn + eps)
    f_measures = 2 * precisions * recalls / (precisions + recalls + eps)
    
    for i in range(num_classes):
        family = 'metric_{}'.format(i)
        tf.summary.scalar('accuracy' , accuracies[i], family=family)
        tf.summary.scalar('precision', precisions[i], family=family)
        tf.summary.scalar('recall'   , recalls[i]   , family=family)
        tf.summary.scalar('f_measure', f_measures[i], family=family)

    accuracy  = tf.reduce_mean(accuracies)
    precision = tf.reduce_mean(precisions)
    recall    = tf.reduce_mean(recalls)
    f_measure = tf.reduce_mean(f_measures)

    family = 'macro_metrics'
    tf.summary.scalar('accuracy' , accuracy , family=family)
    tf.summary.scalar('precision', precision, family=family)
    tf.summary.scalar('recall'   , recall   , family=family)
    tf.summary.scalar('f_measure', f_measure, family=family)
