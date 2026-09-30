# Day 3 Lab Report
## Build a ReAct Agent from Scratch, Break It on Purpose, Then Fix It

### 1. Objective

To build a ReAct-style AI agent from scratch using Python, enable it to use tools, deliberately test failure conditions, and improve its safety and reliability.

### 2. Tools Used

- Python
- OpenAI-compatible API
- safe_calculator
- read_webpage
- AST-based expression parsing
- requests library

### 3. ReAct Workflow

The agent follows:

Reason → Act → Observe → Repeat → Final Answer

The model decides whether a tool is required. The selected tool is executed and its result is added as an observation. The agent then continues until it can provide a final answer or reaches the safety limit.

### 4. Implemented Tools

#### safe_calculator

A safe calculator was implemented using Python's `ast` module. Only approved arithmetic operators are allowed.

#### read_webpage

The webpage reader supports local HTML/text files and HTTP/HTTPS pages. HTML script and style elements are removed before returning text.

### 5. Test Results

| Test | Expected Result | Actual Result |
|---|---|---|
| 15% of AI202 fee | Rs. 2,700 | Rs. 2,700 |
| All three fees after 10% scholarship | Rs. 40,500 | Rs. 40,500 |
| All three fees + hostel lab charges | Rs. 49,500 | Rs. 49,500 |
| Welcome message | Direct response | Successful |
| AI202 fee from notice.html | Rs. 18,000 | Rs. 18,000 |

### 6. Failure Experiments

#### Failure 1: Missing webpage

The notice.html file was temporarily renamed.

The agent repeatedly attempted to read the missing file.

Observation:
File not found errors can cause unnecessary repeated tool calls.

#### Failure 2: Unknown tool

A fake send_email tool was added to the tool schema without adding an implementation to the tool registry.

Observation:
The agent returned "Unknown tool: send_email" instead of crashing.

#### Failure 3: Large webpage

A large webpage was created and the output limit was temporarily increased.

The resulting request became approximately 59,914 tokens while the model limit was 8,000 tokens.

Observation:
The API returned a 413 Request too large error.

### 7. Safety Improvements

The fixed agent implements:

- Maximum step limit
- Safe tool lookup
- Repeated tool-call detection
- Maximum tool-output length
- Character budget
- Model error handling
- Tool execution error handling

### 8. Fixed Agent Test

The fixed agent was tested using:

"Read big.html and tell me the AI202 course fee."

Result:

AI202 course fee = Rs. 18,000

The large webpage no longer caused the previous request-size failure.

### 9. Observation Table

| Experiment | Observation |
|---|---|
| Normal ReAct execution | Agent successfully used tools and generated answers |
| Missing file | Repeated failed tool calls were observed |
| Unknown tool | Safe registry returned an unknown-tool message |
| Large webpage | Excessive context caused request-size failure |
| Output truncation | Large tool output was controlled |
| Repeated-call detection | Identical tool calls were detected |
| Fixed agent | Agent completed the tests safely |

### 10. Discussion

1. ReAct stands for Reasoning and Acting. It combines reasoning with tool-based actions and observations.

2. Tool outputs must be limited because excessive output can increase context size and cause API failures.

3. Unknown tools should be handled safely so that invalid requests do not crash the program.

4. The seen_calls mechanism helps prevent repeated identical tool calls.

5. AST parsing is safer than eval() because only explicitly allowed operations are evaluated.

### 11. Final Result

A ReAct-style AI agent was successfully implemented using Python. The agent can reason about user queries, select appropriate tools, process observations, and generate final answers. Failure modes including missing files, unknown tools, repeated calls, and oversized webpage content were tested. Safety mechanisms were then implemented to improve the reliability of the agent.

### 12. Conclusion

The experiment demonstrated how a tool-using ReAct agent can be built from scratch and made safer by controlling tool execution, repeated actions, and context size.