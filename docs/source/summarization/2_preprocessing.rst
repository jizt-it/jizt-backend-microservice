..
    Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

.. _summarization_preprocessing:

==============
Pre-processing
==============

The main goal of this stage is to adapt the input text so that it is as close as
possible to what the model expects. Additionally, the input text is separated into
sentences. This separation may seem a trivial task, but it involves a series of
difficulties that we will soon explain.

Broadly speaking, the pre-processing stage is further divided into the following
steps:

-  Remove carriage returns, tab stops  (``\n``, ``\t``) and extra spaces between
   words (e.g., ``"I    am"`` → ``"I am"``).

-  Add a space at the beginning of intermediate sentences (e.g., ``"How’s it
   going?Great!"`` → ``"How’s it going? Great!"``).

-  Divide the text in sentences. This is important since some models (like the T5)
   have a maximum input size (which is the length of the sequences used to train
   them). Two common strategies to avoid this limitation are (a) truncating the input
   text, which can lead to significant loss of information, or (b) splitting the text
   into smaller fragments, summarizing each of these fragments, and then concatenating
   them to create the final summary. In our case, we follow this second strategy.
   Furthermore, we make sure that, when fragmenting the text, no sentence is split in
   order to keep the cohesion of the text. And that is why we first carry out this
   division of the text in sentences.

Currently, we use Microsoft's `Bling Fire library
<https://github.com/microsoft/BlingFire>`__ to carry out the division of the
sentences, which gives good results overall.