..
    Copyright (C) 2020-2021 Diego Miguel Lozano <contact@jizt.it>
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

Jizt Docs - AI Summarization in the cloud
=========================================

Ever wondered what Jizt looks like under the hood? You are then in the right place.

Jizt aims to be a service that provides a series of ready-to-use NLP tools. As for
now, Jizt is able to generate abstractive summaries making use of the last advances in
NLP. More specifically, we currently use Google's `T5 model
<https://arxiv.org/abs/1910.10683>`__ in its implementation by `Hugging Face
<https://huggingface.co/transformers/model_doc/t5.html>`__ (big thanks to them!).

In the future, we plan to add more NLP tasks, so that Jizt can be even better!

Everything is still at a very early stage, but progressively, we will add new
features, so stay tuned! Please, keep in mind that Jizt is developed in our free time,
so more often than not, we won't be able to devote as much time as we would like.

You can take a look at the `Jizt Roadmap
<https://github.com/orgs/jizt-it/projects/1>`__ to see what's going on at the
moment.

Are you looking for the REST API documentation? You can find it
`here <https://docs.api.jizt.it>`__.

.. toctree::
   :hidden:
   :caption: Summarization
   :name: summarization
   :maxdepth: 2

   summarization/1_introduction
   summarization/2_preprocessing
   summarization/3_encoding
   summarization/4_summarization
   summarization/5_postprocessing

.. toctree::
   :hidden:
   :caption: Backend
   :name: backend
   :maxdepth: 2

   backend/1_architecture
   backend/2_rest_api

.. toctree::
   :hidden:
   :caption: Frontend
   :name: frontend
   :maxdepth: 2

   frontend/1_cross-platform-app.rst

.. toctree::
   :hidden:
   :caption: Help us
   :name: help us

   misc/CONTRIBUTING.rst
