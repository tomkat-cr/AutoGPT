# Source: https://github.com/SebRinnebach/autodebug/blob/main/autodebug.py

from __future__ import annotations

import openai
import os
import subprocess
# import sys

from ..registry import ability


openai.api_key = os.environ.get("OPENAI_API_KEY")


def run_python_file(filename: str) -> tuple[bool, str]:
    try:
        output = subprocess.check_output(["python3", filename])
        return True, output
    except subprocess.CalledProcessError as e:
        return False, e.output


def fix_python_code(code: str, error_output: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a genius programmer that helps fix Python code." +
                " You reflect on every mistake that you make and learn from it."
            },
            {
                "role": "user",
                "content": "Here is Python code and an error message as it showed" +
                f" up in Terminal:\n\n{code}\n\n{error_output}\n\nPlease provide" +
                " only the complete fixed Python code without any additional" +
                " text or explanations. Please make sure that you don't add any" +
                " other text, just post back the code. It is very important that" +
                " you do that, because otherwise you will interfere with a" +
                " very important task of mine."
            }
        ]
    )
    return response['choices'][0]['message']['content']


def auto_debug_python(target_file: str) -> str:
    response: str = ""
    max_attempts: int = 5
    for attempt in range(1, max_attempts + 1):
        success, output = run_python_file(target_file)
        if success:
            response += "The Python script ran successfully!"
            break
        else:
            response += (f"Attempt {attempt}: Error encountered while running" +
                         " the script:\n")
            response += (output.decode("utf-8") + "\n")

            with open(target_file, "r") as f:
                original_code = f.read()

            fixed_code = fix_python_code(original_code, output.decode("utf-8"))
            response += (f"GPT-4 suggested fix:\n{fixed_code}\n")

            with open(target_file, "w") as f:
                f.write(fixed_code)

    if not success:
        response += ("Maximum number of attempts reached. Please try fixing the" +
                     " script manually or run AutoDebug again.")
    return response


@ability(
    name="python_autodebug",
    description="Automatically debug and fix Python scripts.",
    parameters=[
        {
            "name": "target_file",
            "description": "Python file path",
            "type": "string",
            "required": True,
        },
    ],
    output_type="list[str]",
)
async def python_autodebug(agent, task_id: str, target_file: str) -> str:
    """Automatically debug and fix Python scripts.

    Args:
        target_file (str): Python file path.

    Returns:
        str: suggestions to fi the Python code.
    """
    result = auto_debug_python(target_file)
    return result
