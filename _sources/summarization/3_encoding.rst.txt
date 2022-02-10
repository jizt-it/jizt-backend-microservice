..
    Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

.. _summarization_encoding:

========
Encoding
========

As we mentioned before, AI models generally work with numerical representations. *Word
embedding* techniques focus on linking text (either words, sentences, etc.) with real
number vectors. This makes it possible to apply common architectures within AI (and
especially Deep Learning), such as Convolutional Neural Networks (CNN), to text
generation. This idea, conceptually simple, involves great complexity, since the
generated vectors must retain as much information as possible from the original text,
including semantic and grammatical aspects. For example, the vectors corresponding to
the words "teacher" and "student" must preserve a certain relationship between them,
as well as with the word "education" or "school". In addition, their connection with
the words "teach" or "learn" will be slightly different, since in this case we are
dealing with a different grammatical category (verbs, instead of nouns). Through
this example, we can understand that this is a complex process\ [1]_.

Apart from that, in this stage, once we have the sentences divided from the previous
stage, we now are able to:

#. Split the text in smaller fragments, so we don't exceed the model's maximum
   sequence length. This division is made, as we said, without splitting any
   sentences.

#. Encode each of these fragments separately. The encoding itself is made by the `T5
   Tokenizer <https://huggingface.co/transformers/model_doc/t5.html#t5tokenizer>`__
   provided by Hugging Face.

#. Summarize the encoded fragments (this is carried out in the :ref:`summarization_summarization` stage).

#. Concatenate these partial summaries so we end up with a single summary. As we
   always keep the order of the text fragments, this resultant summary will be
   cohesive and coherent.

.. figure:: ../_static/images/summarization/summarization-process-detail.png
   :alt: Summarization process in detail.
   :name: fig:summarization-process-detail
   :align: center
   :width: 100%

   Detailed steps in the summarization process. Text taken from *The Catcher in the
   Rye*.

Something worth mentioning is that, while keeping the sentences complete, we ensure
that each all the fragments contain roughly the same number of sentences. This is
important because otherwise, some of the partial summaries could be too short.

For this, we first split the text eagerly, attending to the maximum sequence length,
and then we balance the number of sentences each fragment, keeping the order. The
following figure shows an example with a maximum length of 100 tokens.

.. figure:: ../_static/images/summarization/sentence-balancing-process.png
   :alt: Division of the text into fragments.
   :name: fig:sentence-balancing-process
   :align: center
   :width: 100%

   Once we have divided the sentences eagerly, we balance the number of sentences in
   each fragment.

In the previous example, the standard deviation in the number of tokens between
fragments begins being :math:`\sigma_1` = 39.63 and at the end is :math:`\sigma_5` =
1.53.


.. [1]
   If you want to learn more about this topic, we recommend to watch `Lecture 1
   <https://www.youtube.com/watch?v=8rXD5-xhemo&list=PLoROMvodv4rOhcuXMZkNm7j3fVwBBY42z>`__
   and `Lecture 2
   <https://www.youtube.com/watch?v=kEMJRjEdNzM&list=PLoROMvodv4rOhcuXMZkNm7j3fVwBBY42z&index=2>`__
   from the *Stanford CS224N: NLP with Deep Learning* course (the whole course is a
   pleasure to watch, anyway).