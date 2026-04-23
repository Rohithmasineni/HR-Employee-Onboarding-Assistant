# HR-Employee-Onboarding-Assistant

An AI-powered HR chatbot built with **Qwen3-32B (Groq)** and the **Model Context Protocol (MCP)** architecture. This project demonstrates a clean, framework-less approach to building intelligent assistants—**no LangChain, no RAG, and no heavy agent libraries.**

---

## 📌 Problem Statement

In mid-to-large organizations, employees and HR teams face several persistent hurdles:
* [cite_start]**Information Overload:** Employees waste time searching through lengthy policy documents for simple answers[cite: 11, 17].
* [cite_start]**HR Fatigue:** HR teams spend significant effort answering the same repetitive queries about leave and onboarding weekly[cite: 13, 18].
* [cite_start]**Onboarding Confusion:** New joiners often miss critical steps because they lack guided, context-aware assistance[cite: 15, 21].
* [cite_start]**Data Fragmentation:** Leave balances and employee records are often scattered, making quick checks difficult[cite: 20].

[cite_start]This project centralizes these processes into a **24/7 intelligent system** that fetches data live at runtime[cite: 19, 26].

---

## ✨ Features

* [cite_start]**📋 Policy Q&A:** Instant answers regarding leave types, rules, application processes, and probation limits[cite: 26, 44].
* [cite_start]**📊 Real-Time Leave Balance:** Fetches live yearly remaining balances and monthly usage breakdowns[cite: 27].
* [cite_start]**🗓️ Context-Aware Onboarding:** Tailored guidance for "Day 1" through "Week 2" with specific tracks for **Freshers** vs. **Experienced** hires[cite: 25, 44].
* [cite_start]**👤 Employee Profile:** Quick access to reporting manager details, department, designation, and leave history[cite: 56].
* [cite_start]**🔌 Pure MCP Architecture:** The LLM does not have documents pre-loaded; it must actively invoke tools to "see" data[cite: 47, 52].

---

## 🏗️ Architecture & Workflow

[cite_start]The system operates on a clean three-layer architecture: **Streamlit (Frontend)**, **Groq/Qwen3 (Intelligence)**, and **Filesystem MCP (Data Bridge)**[cite: 32, 76].



### End-to-End Flow:
1. [cite_start]**User Input:** Employee asks a question (e.g., "What is the leave policy?")[cite: 48].
2. **LLM Decision:** Groq (Qwen3-32B) receives the query + tool definitions. [cite_start]It realizes it lacks the data and generates a `tool_use` block[cite: 48].
3. [cite_start]**MCP Interception:** The app routes this request to the `mcp_handler.py`[cite: 51].
4. [cite_start]**Data Retrieval:** The MCP server reads the relevant file from the `/data` directory[cite: 51].
5. [cite_start]**Final Generation:** The model receives the file content, processes the natural language, and returns the final answer[cite: 51].

---

## 🔌 MCP Tools

| Tool | Trigger | Action |
| :--- | :--- | :--- |
| `read_leave_policy` | Questions about rules, types, or application | [cite_start]Reads `leave_policy.txt` [cite: 56] |
| `read_onboarding_checklist` | Questions about Day 1, IT setup, or documents | [cite_start]Reads `onboarding_checklist.txt` [cite: 56] |
| `read_employee_record` | Leave balance, manager, or profile queries | [cite_start]Reads `employee_record.json` [cite: 56] |

---

## 📁 Data Files

[cite_start]The `/data` folder serves as the single source of truth for the assistant[cite: 62]:

* [cite_start]**`leave_policy.txt`**: A comprehensive guide containing leave types (Casual, Sick, Earned), carry-forward rules, and the standard application process[cite: 44].
* **`onboarding_checklist.txt`**: A structured task list categorized by timeline (Day 1/Week 1) and experience level (Fresher/Experienced)[cite: 44].
* **`employee_record.json`**: A dynamic mini-database storing personal profiles, manager info, live leave balances, and historical usage[cite: 44, 61].

---

## ⚙️ Tech Stack

* **Frontend:** Streamlit [cite: 73]
* [cite_start]**LLM:** Qwen3-32B via Groq API [cite: 76]
* [cite_start]**MCP Server:** Python-based Filesystem MCP [cite: 76]
* **Language:** Python 3.9+ [cite: 76]

---

## 🚀 Live Demo

Experience the assistant live on Hugging Face Spaces:
**[HR & Employee Onboarding Assistant](https://huggingface.co/spaces/rohithmasineni/HR_and_Employee_Onboarding_Assistant)**

---

## 🛠️ Setup & Installation

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/your-username/hr-onboarding-assistant.git](https://github.com/your-username/hr-onboarding-assistant.git)
   cd hr-onboarding-assistant
