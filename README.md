# Requirements

1. `uv` (to set up and run the project)
2. `.env` with a Serper API Key and other Model Keys
3. `npm`/`npx` (for website creation, building the Tauri application)
4. Rust/Cargo (for building the Tauri application)

# Instructions to run

1. Clone this repository
2. Run `uv run main.py` launch Unlovable

⚠️ Does not support MacOS due to a lack of a MacBook to test with.

# Overview of MAT496

In this course, we have primarily learned Langgraph. This is helpful tool to build apps which can process unstructured `text`, find information we are looking for, and present the format we choose. Some specific topics we have covered are:

- Prompting
- Structured Output
- Semantic Search
- Retreaval Augmented Generation (RAG)
- Tool calling LLMs & MCP
- Langgraph: State, Nodes, Graph

We also learned that Langsmith is a nice tool for debugging Langgraph codes.

---

# Capstone Project objective

The first purpose of the capstone project is to give a chance to revise all the major above listed topics. The second purpose of the capstone is to show your creativity. Think about all the problems which you can not have solved earlier, but are not possible to solve with the concepts learned in this course. For example, We can use LLM to analyse all kinds of news: sports news, financial news, political news. Another example, we can use LLMs to build a legal assistant. Pretty much anything which requires lots of reading, can be outsourced to LLMs. Let your imagination run free.

---

# Project report Template

## Title: Unlovable

## Overview

Unlovable is a multi-agent AI tool for even those with the least literacy in technology and web development to create beautiful MPAs (multi-page applications) fitting their needs. All they need to do is create folders with `.txt` files containing a prompt for each route in their site. Or they can just have a single route on `/` for an SPA. After that their website is generated and loaded on their browser. If the website contains any breaking bugs, the AI should self-detect and regenerate the website to eliminate the bug. The user is given the ability to click on specific elements in the site and prompt the AI with those particular elements to further tweak or fix the site to their specifications. The website itself shall be made using Next.js, TailwindCSS, Framer Motion (for animations), and Lucide (for icons).

## Reason for picking up this project

Web Development is a tedious task that almost no one who wants to build an application wants to go through. It has way too many issues with deprecated libraries, constantly evolving technologies, and outdated documentation (especially outdated documentation). This project aims to use LangChain and LangGraph to create a multi-agent team to optimally design and then develop the site according to the user's website, making maximal use of the technologies taught in this course.

## Video Summary Link:

Make a short - 3-5 min video of yourself, put it on youtube/googledrive, and put its link in your README.md.

- Video format should be like this:
- your face should be visible
- State the overall job of your agent: what inputs it takes, and what output it gives.
- Very quickly, explain how your agent acts on the input and spits out the output.
- show an example run of the agent in the video

## Plan

I plan to execute these steps to complete my project.

- [DONE] Create CLI and server to host landing page and handle generation
- [DONE] Write multi-agent generation workflow
- [DONE] Host generated Next.js application with Unlovable overlay
- [TODO] Chat UI and regeneration workflow
- [TODO] Build/deployment

## Conclusion:

I had planned to achieve a complete text to deployed web application. I think I have not achieved the conclusion satisfactorily. Since there are still a couple features left that require a lot of time to implement on the UI front, the product is not complete since it does not take care of building and deploying web applications yet. Moreover the UI can be polished a bit more.

---

# Added instructions:

- This is a `solo assignment`. Each of you will work alone. You are free to talk, discuss with chatgpt, but you are responsible for what you submit. Some students may be called for viva. You should be able to each and every line of work submitted by you.

- `commit` History maintenance.
  - Fork this repository and build on top of that.
  - For every step in your plan, there has to be a commit.
  - Change [TODO] to [DONE] in the plan, before you commit after that step.
  - The commit history should show decent amount of work spread into minimum two dates.
  - **All the commits done in one day will be rejected**. Even if you are capable of doing the whole thing in one day, refine it in two days.

- Deadline: Dec 2nd, Tuesday 11:59 pm

# Grading: total 25 marks

- Coverage of most of topics in this class: 20
- Creativity: 5
