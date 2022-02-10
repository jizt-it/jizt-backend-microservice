..
    Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

.. _summarization_summarization:

=============
Summarization
=============

In this stage we take the encoded fragments and we summarize each of them separately.
Then, we decode them, so we get again actual words instead of real numbers.

.. figure:: ../_static/images/summarization/summ-decoding-concat.png
   :alt: Summarization, decoding and concatenated.
   :name: fig:summ-decoding-concat.png
   :align: center
   :width: 100%

   Once we get the partial summaries from the model, we decode and concatenate them.

As the T5 model that we use is uncased the final summary obtained at this point is all
in lowercase. This is something we deal with in the next stage, the post-processing,
so the summary returned to the user is correctly cased.

If you curious about how these language generation models work, we recommend to read
this `fantastic article <https://huggingface.co/blog/how-to-generate>`__ by Hugging
Face on the different decoding strategies used in transformer-based language models. 