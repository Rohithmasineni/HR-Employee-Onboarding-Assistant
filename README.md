# HR-Employee-Onboarding-Assistant

An AI-powered HR chatbot built with **Qwen3-32B (Groq)** and the **Model Context Protocol (MCP)** architecture. This project demonstrates a clean, framework-less approach to building intelligent assistants—**no LangChain, no RAG, and no heavy agent libraries.**

---

## Problem Statement

In mid-to-large organizations, employees and HR teams face several persistent hurdles:
* **Information Overload:** Employees waste time searching through lengthy policy documents for simple answers.
* **HR Fatigue:** HR teams spend significant effort answering the same repetitive queries about leave and onboarding weekly.
* [cite_start]**Onboarding Confusion:** New joiners often miss critical steps because they lack guided, context-aware assistance.
* **Data Fragmentation:** Leave balances and employee records are often scattered, making quick checks difficult.

This project centralizes these processes into a **24/7 intelligent system** that fetches data live at runtime.

---

## Features

* **Policy Q&A:** Instant answers regarding leave types, rules, application processes, and probation limits.
* **Real-Time Leave Balance:** Fetches live yearly remaining balances and monthly usage breakdowns.
* **Context-Aware Onboarding:** Tailored guidance for "Day 1" through "Week 2" with specific tracks for **Freshers** vs. **Experienced** hires.
* **Employee Profile:** Quick access to reporting manager details, department, designation, and leave history.
* **Pure MCP Architecture:** The LLM does not have documents pre-loaded; it must actively invoke tools to "see" data.

---

##  Architecture & Workflow

The system operates on a clean three-layer architecture: **Streamlit (Frontend)**, **Groq/Qwen3 (Intelligence)**, and **Filesystem MCP (Data Bridge)**.



### End-to-End Flow:
1. **User Input:** Employee asks a question (e.g., "What is the leave policy?").
2. **LLM Decision:** Groq (Qwen3-32B) receives the query + tool definitions. It realizes it lacks the data and generates a `tool_use` block.
3. **MCP Interception:** The app routes this request to the `mcp_handler.py`.
4. **Data Retrieval:** The MCP server reads the relevant file from the `/data` directory.
5. **Final Generation:** The model receives the file content, processes the natural language, and returns the final answer.

---

## MCP Tools

| Tool | Trigger | Action |
| :--- | :--- | :--- |
| `read_leave_policy` | Questions about rules, types, or application | [cite_start]Reads `leave_policy.txt` [cite: 56] |
| `read_onboarding_checklist` | Questions about Day 1, IT setup, or documents | [cite_start]Reads `onboarding_checklist.txt` [cite: 56] |
| `read_employee_record` | Leave balance, manager, or profile queries | [cite_start]Reads `employee_record.json` [cite: 56] |

---

## 📁 Data Files

The `/data` folder serves as the single source of truth for the assistant[cite: 62]:

* **`leave_policy.txt`**: A comprehensive guide containing leave types (Casual, Sick, Earned), carry-forward rules, and the standard application process[cite: 44].
* **`onboarding_checklist.txt`**: A structured task list categorized by timeline (Day 1/Week 1) and experience level (Fresher/Experienced)[cite: 44].
* **`employee_record.json`**: A dynamic mini-database storing personal profiles, manager info, live leave balances, and historical usage.

---

## Tech Stack

* **Frontend:** Streamlit 
* **LLM:** Qwen3-32B via Groq API 
* **MCP Server:** Python-based Filesystem MCP 
* **Language:** Python 3.9+ 

---

## Live Demo

Experience the assistant live on Hugging Face Spaces:
**[HR & Employee Onboarding Assistant](https://huggingface.co/spaces/rohithmasineni/HR_and_Employee_Onboarding_Assistant)**

