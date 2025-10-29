import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Client will try to find API key automatically
client = genai.Client()


def generate_prompt():
    """
    Revised prompt asking for standard Markdown code block,
    which is more reliable than custom tags.
    """
    return f"""write the python code to calculate
a loan payment with the following inputs: interest,
term, present value. return code only wrapped in a Markdown code block (triple backticks). Do not add any extra text or explanation outside the code block.
"""


response = client.models.generate_content(
    model="gemini-2.5-flash", contents=generate_prompt()
)

# Use regex to find ANY content between triple backticks,
# including the content between the optional language identifier (like `python`)
# The `[\w\W]*?` pattern is robust because it matches any character, including newlines.
# The 's' flag (re.DOTALL) ensures '.' matches newlines as well, which is often cleaner:
match = re.search(r"```.*?([\w\W]*?)```", response.text, re.DOTALL)

# Robust error handling is essential!
if match:
    # Group 1 contains the code inside the fences. We strip it to remove
    # any leading/trailing whitespace or newlines.
    code_content = match.group(1).strip()

    # If the model included a language identifier (like 'python') as the first line,
    # we need to remove it. We check if the first line starts with a letter.
    first_line = code_content.split("\n")[0].strip()
    if first_line and re.match(r"^[a-zA-Z]+$", first_line):
        code_content = "\n".join(code_content.split("\n")[1:])

    print("--- Extracted Code ---")
    print(code_content)

    # Write the cleaned content to the file
    with open("loan_payment.py", "w") as f:
        f.write(code_content)
else:
    print("Error: Failed to find code block (```...```) in the response.")
    print("\nRaw Response:")
    print(response.text)
