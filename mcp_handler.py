"""
mcp_handler.py
--------------
Filesystem MCP Server simulation.
Each function is an MCP tool the LLM can call via tool_use.
The LLM never sees file contents directly — it must invoke these tools.
"""

import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# TOOL 1 — Read Leave Policy

def read_leave_policy() -> str:
    try:
        filepath = os.path.join(DATA_DIR, "leave_policy.txt")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "ERROR: leave_policy.txt not found in /data directory."
    except Exception as e:
        return f"ERROR reading leave policy: {str(e)}"



# TOOL 2 — Read Onboarding Checklist

def read_onboarding_checklist() -> str:
    try:
        filepath = os.path.join(DATA_DIR, "onboarding_checklist.txt")
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "ERROR: onboarding_checklist.txt not found in /data directory."
    except Exception as e:
        return f"ERROR reading onboarding checklist: {str(e)}"


# TOOL 3 — Read Employee Record

def read_employee_record(employee_id: str) -> str:
    try:
        filepath = os.path.join(DATA_DIR, "employee_record.json")
        with open(filepath, "r", encoding="utf-8") as f:
            record = json.load(f)
        if record.get("employee_id", "").upper() == employee_id.strip().upper():
            return json.dumps(record, indent=2)
        return f"ERROR: No employee found with ID '{employee_id}'."
    except FileNotFoundError:
        return "ERROR: employee_record.json not found in /data directory."
    except Exception as e:
        return f"ERROR reading employee record: {str(e)}"


# TOOL 4 — Update Leave Balance

def update_leave_balance(employee_id: str, leave_type: str, days: int, reason: str = "") -> str:
    valid_types = ["casual_leave", "sick_leave", "earned_leave"]
    leave_type = leave_type.strip().lower().replace(" ", "_")

    if leave_type not in valid_types:
        return f"ERROR: Invalid leave type '{leave_type}'. Must be one of: {', '.join(valid_types)}"

    try:
        filepath = os.path.join(DATA_DIR, "employee_record.json")
        with open(filepath, "r", encoding="utf-8") as f:
            record = json.load(f)

        if record.get("employee_id", "").upper() != employee_id.strip().upper():
            return f"ERROR: Employee ID '{employee_id}' not found."

        current_balance = record["leave_balance"].get(leave_type, 0)
        if not isinstance(current_balance, (int, float)):
            current_balance = 0

        if days <= 0:
            return "ERROR: Days must be a positive integer."

        if days > current_balance:
            return (
                f"ERROR: Insufficient {leave_type.replace('_', ' ').title()}. "
                f"Requested: {days} days, Available: {current_balance} days."
            )

        # Deduct balance
        record["leave_balance"][leave_type] = current_balance - days

        # Update monthly_usage for current month
        current_month = str(date.today())[:7]  # e.g. "2025-04"
        if "monthly_usage" not in record:
            record["monthly_usage"] = {}
        if current_month not in record["monthly_usage"]:
            record["monthly_usage"][current_month] = {"casual_leave": 0, "sick_leave": 0, "earned_leave": 0}
        record["monthly_usage"][current_month][leave_type] = (
            record["monthly_usage"][current_month].get(leave_type, 0) + days
        )

        # Append to leave history
        record.setdefault("leave_history", []).append({
            "type": leave_type,
            "days": days,
            "date_applied": str(date.today()),
            "reason": reason or "Not specified",
            "status": "approved"
        })

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        updated_balance = record["leave_balance"][leave_type]
        return (
            f"Leave applied successfully!\n"
            f"  Type    : {leave_type.replace('_', ' ').title()}\n"
            f"  Deducted: {days} day(s)\n"
            f"  Balance : {updated_balance} day(s) remaining (yearly)\n"
            f"  Reason  : {reason or 'Not specified'}"
        )

    except Exception as e:
        return f"ERROR updating leave balance: {str(e)}"


# DISPATCHER — Routes LLM tool calls to MCP functions

def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    try:
        if tool_name == "read_leave_policy":
            return read_leave_policy()

        elif tool_name == "read_onboarding_checklist":
            return read_onboarding_checklist()

        elif tool_name == "read_employee_record":
            employee_id = tool_args.get("employee_id", "EMP123")
            return read_employee_record(str(employee_id))

        elif tool_name == "update_leave_balance":
            employee_id = str(tool_args.get("employee_id", "EMP123"))
            leave_type = str(tool_args.get("leave_type", ""))
            reason = str(tool_args.get("reason", ""))

            # Safe int conversion for days
            raw_days = tool_args.get("days", 0)
            try:
                days = int(raw_days)
            except (ValueError, TypeError):
                return f"ERROR: 'days' must be a valid integer, got: '{raw_days}'"

            return update_leave_balance(employee_id, leave_type, days, reason)

        else:
            return f"ERROR: Unknown tool '{tool_name}'. No MCP handler found."

    except Exception as e:
        return f"ERROR in dispatch_tool for '{tool_name}': {str(e)}"