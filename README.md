### ⚠️ Not currently maintained ⚠️
The Jizt backend proved to work great under a distributed, microservices architecture. For over one year, it was hosted on Google Cloud (GKE) powered by Kubernetes and Kafka. However, the implementation of the architecture on its own actually took most part of our development time, and due to our limited resources, slowed down the arrival of new features.

With this in mind, we decided to migrate the Jizt backend to a simpler monolithic architecture in order to focus our efforts on our main goal: provide a great summarization tool. Since we still don't have that many users the new architecture should work just fine. Nevertheless, we'll never say we won't come back to a distributed approach! ;)

**You can check the currently developed backend at [jizt-it/jizt-backend](https://github.com/jizt-it/jizt-backend).**

---

<p align="center"><img width="400" src="https://github.com/dmlls/jizt/blob/main/img/readme/JIZT-logo.svg" alt="Jizt"></p>

<p align="center" display="inline-block">
  <a href="https://docs.jizt.it">
    <img src="https://github.com/jizt-it/jizt-backend/actions/workflows/build-docs.yml/badge.svg" alt="Build & Publish docs">
  </a>
  <a href="https://deepsource.io/gh/jizt-it/jizt-backend/?ref=repository-badge">
    <img src="https://deepsource.io/gh/jizt-it/jizt-backend.svg/?label=active+issues" alt="Active Issues">
  </a>
  <a href="https://deepsource.io/gh/jizt-it/jizt-backend/?ref=repository-badge">
    <img src="https://deepsource.io/gh/jizt-it/jizt-backend.svg/?label=resolved+issues" alt="Resolved Issues">
  </a>
</p>

<h3 align="center">AI Text Summarization in the Cloud</h3>
<br/>

Jizt makes use of the latest advances in Natural Language Processing (NLP), using state-of-the-art language generation models, such as Google's <a href="https://arxiv.org/abs/1910.10683">T5</a> model, to provide accurate and complete abstractive summaries.

## Jizt in 86 words

📄 Jizt generates abstractive summaries, i.e. summaries containing words or expressions that do not appear in the original text. In addition, it allows you to adjust the parameters of the summary, such as its length or the generation method to be used.

📡 Jizt provides a REST API supported by a backend that implements an event-driven microservices architecture (Kubernetes + Apache Kafka), in order to provide scalability and high availability. The REST API documentation is accessible via [docs.api.jizt.it](https://docs.api.jizt.it).

✨ Check out our app! Available at [app.jizt.it](https://app.jizt.it) and through [Google Play](https://play.google.com/store/apps/details?id=it.jizt.app).

## Docs

You can access the project documentation through [docs.jizt.it](https://docs.jizt.it).

## Contribute

Do you want to contribute to the project? Awesome! At [CONTRIBUTING.md](https://github.com/dmlls/jizt/blob/main/CONTRIBUTING.md) you will find helpful information. Also, if you want to financially support the project, you can do so at [paypal.me/jiztit](https://www.paypal.com/paypalme/jiztit).

## What's coming next?

You can take a look at the [Jizt Roadmap](https://github.com/orgs/jizt-it/projects/1) GitHub project to find information about the tasks we are currently working on, and those that will be implemented soon.
