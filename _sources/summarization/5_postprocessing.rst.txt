..
    Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

.. _summarization_postprocessing:

===============
Post-processing
===============

Finally, once we get the summary, as it is uncased, we make use of a truecaser model
to case it correctly.

.. figure:: ../_static/images/summarization/final-summary.png
   :alt: Truecasing of the generated summary.
   :name: fig:final-summary
   :align: center
   :width: 100%

   Truecasing of the generated summary.

Currently, we use the `truecase <https://github.com/daltonfury42/truecase>`__ module
for Python, which implements a statistical model inspired by the paper `tRuEcasIng
<https://www.cs.cmu.edu/~llita/papers/lita.truecasing-acl2003.pdf>`__ by Lucian Vlad
Lita et al.

At this point, the summary is ready to be delivered to the user.