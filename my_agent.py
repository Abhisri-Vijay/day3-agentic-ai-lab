import json

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL
from my_tools import TOOL_FUNCTIONS, TOOLS


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


SYSTEM_PROMPT = """
You are a helpful ReAct-style agent.

You have two tools:
1. safe_calculator - for arithmetic calculations.
2. read_webpage - for reading course fee information from notice.html.

Use tools when necessary.

For questions about course fees:
1. Read notice.html first.
2. Use the calculator for arithmetic.

If no tool is needed, answer directly.

Do not invent tool results.
"""


def run_agent(user_message: str, max_steps: int = 6):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for step in range(max_steps):
        print(f"\n--- STEP {step + 1} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Stop if no tool call is requested
        if not assistant_message.tool_calls:
            print("\nFINAL ANSWER:")
            print(assistant_message.content)
            return assistant_message.content

        # Record assistant tool request
        messages.append(assistant_message)

        # Execute requested tools
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            print(f"TOOL CALL: {tool_name}")
            print(f"ARGUMENTS: {arguments}")

            tool_function = TOOL_FUNCTIONS.get(tool_name)

            if tool_function is None:
                tool_result = f"Unknown tool: {tool_name}"
            else:
                try:
                    tool_result = tool_function(**arguments)
                except Exception as exc:
                    tool_result = f"Tool execution error: {exc}"

            print(f"OBSERVATION: {tool_result}")

            # Send observation back to the model
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                }
            )

    print("\nSAFETY EXIT: maximum steps reached.")
    return "Agent stopped because the maximum number of steps was reached."


if __name__ == "__main__":
    question = input("Ask the agent: ")
    run_agent(question)