import json

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL
from my_tools import TOOL_FUNCTIONS, TOOLS


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


SYSTEM_PROMPT = """
You are a safe ReAct-style agent.

Available tools:
1. safe_calculator
2. read_webpage

Use tools only when necessary.

For course-fee questions, read notice.html first.
Do not invent tool results.
If a tool fails, do not repeatedly call the same tool with the same arguments.
"""


MAX_STEPS = 6
MAX_TOOL_CHARS = 1500
CHAR_BUDGET = 30000


def run_agent(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    seen_calls = set()
    total_chars = 0

    for step in range(MAX_STEPS):
        print(f"\n--- STEP {step + 1} ---")

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as exc:
            print(f"\nMODEL ERROR: {exc}")
            return f"Agent stopped because of model error: {exc}"

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            print("\nFINAL ANSWER:")
            print(assistant_message.content)
            return assistant_message.content

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            call_signature = (
                tool_name,
                json.dumps(arguments, sort_keys=True),
            )

            print(f"TOOL CALL: {tool_name}")
            print(f"ARGUMENTS: {arguments}")

            # Detect repeated identical tool calls
            if call_signature in seen_calls:
                tool_result = (
                    "Repeated identical tool call detected. "
                    "Stop retrying this tool call."
                )
                print(f"OBSERVATION: {tool_result}")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                )
                continue

            seen_calls.add(call_signature)

            # Safe tool lookup
            tool_function = TOOL_FUNCTIONS.get(tool_name)

            if tool_function is None:
                tool_result = f"Unknown tool: {tool_name}"
            else:
                try:
                    tool_result = tool_function(**arguments)
                except Exception as exc:
                    tool_result = f"Tool execution error: {exc}"

            # Limit individual observation size
            tool_result = str(tool_result)[:MAX_TOOL_CHARS]

            total_chars += len(tool_result)

            # Total observation budget
            if total_chars > CHAR_BUDGET:
                tool_result = (
                    "Tool output budget exceeded. "
                    "The observation was truncated for safety."
                )

            print(f"OBSERVATION: {tool_result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

    print("\nSAFETY EXIT: maximum steps reached.")
    return "Agent stopped because the maximum number of steps was reached."


if __name__ == "__main__":
    question = input("Ask the agent: ")
    run_agent(question)