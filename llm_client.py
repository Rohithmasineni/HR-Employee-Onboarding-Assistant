"""
llm_client.py
-------------
Handles all Groq API communication using qwen/qwen3-32b.
Implements the full MCP tool-use loop (OpenAI-compatible format):
  1. Send messages + tool definitions to Groq
  2. Model returns tool_calls → dispatch to MCP handler
  3. Send MCP results back as role="tool" messages
  4. Model generates final natural language answer
"""

import os
import json
from groq import Groq, APIConnectionError, APIStatusError, RateLimitError
from dotenv import load_dotenv
from mcp_handler import dispatch_tool

load_dotenv()

MODEL = "qwen/qwen3-32b"

# MCP TOOL DEFINITIONS  (Groq / OpenAI format)
# Passed to the model — no document content in prompt

MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_leave_policy",
            "description": (
                "Reads the company HR leave policy document from the filesystem via MCP. "
                "Call this when the user asks about leave types, entitlements, leave rules, "
                "how to apply for leave, carry-forward, probation leave limits, or anything "
                "related to leave policies."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_onboarding_checklist",
            "description": (
                "Reads the employee onboarding checklist from the filesystem via MCP. "
                "Call this when the user asks about Day 1 tasks, Week 1 tasks, onboarding "
                "process, documents to submit, IT setup, or what to do as a new joiner. "
                "The checklist has sections for ALL employees, FRESHER ONLY, and EXPERIENCED ONLY."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_employee_record",
            "description": (
                "Fetches the employee's record from the filesystem via MCP. "
                "Contains leave balance (yearly remaining), monthly usage, leave history, "
                "department, designation, reporting manager, and onboarding status. "
                "Call this when the user asks about remaining leaves, profile info, "
                "leave history, or monthly leave usage."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "The employee ID. Default is EMP123."
                    }
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_leave_balance",
            "description": (
                "Deducts leave days from the employee's yearly balance and records it. "
                "Call this ONLY when the user explicitly wants to apply, book, or take leave. "
                "Confirm leave_type and number of days with the user before calling."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "The employee ID. Default is EMP123."
                    },
                    "leave_type": {
                        "type": "string",
                        "description": "One of: casual_leave, sick_leave, earned_leave"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of leave days to deduct (positive integer)."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the leave application."
                    }
                },
                "required": ["employee_id", "leave_type", "days"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an intelligent HR & Employee Onboarding Assistant for TechCorp Solutions.
You help employees with leave policies, leave balances, onboarding guidance, and employee profile queries.

IMPORTANT — DATA RULES:
- You do NOT have any HR data in memory. You MUST always call the appropriate MCP tool to fetch data before answering.
- Never answer data-related questions from memory or assumptions.

IMPORTANT — CONTEXT-AWARE ANSWERING:
- The onboarding checklist has sections tagged [ALL], [FRESHER ONLY], and [EXPERIENCED ONLY].
- If the user says they are a FRESHER or has no prior work experience:
    → Do NOT mention Relieving Letter, Experience Letter, previous salary slips, or BGV.
    → Only list documents and steps tagged [ALL] or [FRESHER ONLY].
- If the user says they are EXPERIENCED or joining from another company:
    → Include all [ALL] and [EXPERIENCED ONLY] items including Relieving Letter, BGV, etc.
- If the user does NOT mention their experience level and asks about documents/onboarding:
    → First ask: "Are you joining as a fresher or as an experienced hire?" before answering.

IMPORTANT — LEAVE BALANCE RULES:
- leave_balance = YEARLY remaining balance. Never present it as monthly.
- For "this month" queries → check monthly_usage field for the current month.
- Always distinguish clearly: "used X days this month" vs "Y days remaining for the year".

GENERAL RULES:
- Be concise, friendly, and professional.
- For leave application, confirm leave_type and days with user before calling the update tool.
- Default employee is Rohith Kumar (EMP123).
"""

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")
    return Groq(api_key=api_key)


def chat_with_groq(conversation_history: list) -> tuple[str, list]:
    """
    Sends conversation history to Groq (qwen/qwen3-32b).
    Runs the full MCP tool-use loop until model gives a final text answer.

    Args:
        conversation_history: List of message dicts {"role": ..., "content": ...}

    Returns:
        (final_response_text, updated_conversation_history)
    """
    client = get_groq_client()

    MAX_TOOL_ROUNDS = 5
    tool_rounds = 0

    while tool_rounds < MAX_TOOL_ROUNDS:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=conversation_history,
                tools=MCP_TOOLS,
                tool_choice="auto",
                temperature=0.2,
                reasoning_effort="none",   # Disable chain-of-thought for faster responses
            )
        except RateLimitError as e:
            return (
                "Rate limit reached on Groq API. Please wait a moment and try again.\n"
                f"Details: {str(e)}"
            ), conversation_history
        except APIConnectionError as e:
            return (
                "Could not connect to Groq API. Please check your internet connection.\n"
                f"Details: {str(e)}"
            ), conversation_history
        except APIStatusError as e:
            return (
                f"Groq API error (status {e.status_code}). Please try again.\n"
                f"Details: {e.message}"
            ), conversation_history

        assistant_message = response.choices[0].message

        # Append assistant's response to history (serialize properly)
        assistant_entry = {"role": "assistant", "content": assistant_message.content or ""}
        if assistant_message.tool_calls:
            assistant_entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        conversation_history.append(assistant_entry)

        # If no tool calls — we have the final answer
        if not assistant_message.tool_calls:
            final_text = assistant_message.content or ""
            return final_text.strip(), conversation_history

        # ── Process each tool call → dispatch to MCP → append results ──
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id

            # Safely parse arguments JSON string
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except (json.JSONDecodeError, TypeError):
                tool_args = {}

            # Call the MCP handler
            mcp_result = dispatch_tool(tool_name, tool_args)

            # Append tool result — role must be "tool" for Groq
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": str(mcp_result)
            })

        tool_rounds += 1

    # Fallback if max rounds hit (shouldn't happen in normal use)
    return (
        "I was unable to retrieve the information after several attempts. Please try rephrasing your question.",
        conversation_history
    )


def build_user_message(text: str) -> dict:
    """Returns a properly formatted user message dict for Groq."""
    return {"role": "user", "content": text}


def build_system_message() -> dict:
    """Returns the system message dict."""
    return {"role": "system", "content": SYSTEM_PROMPT}