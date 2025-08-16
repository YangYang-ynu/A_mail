from typing import Annotated

def talk_with_human(
    question: Annotated[str, "The question to ask the user"]
) -> str:
    """Ask the user a question and get their response"""
    print(f"\n🤖 Question: {question}")
    try:
        return input("👤 Answer: ")
    except KeyboardInterrupt:
        return "User cancelled the operation"


def perform_addition(
    numbers: Annotated[list, "List of numbers to be added"]
) -> str:
    """Perform addition operation"""
    try:
        result = sum(float(num) for num in numbers)
        return str(result)
    except Exception as e:
        return f"Addition error: {str(e)}"

def perform_subtraction(
    minuend: Annotated[str, "Minuend"],
    subtrahend: Annotated[str, "Subtrahend"]
) -> str:
    """Perform subtraction operation"""
    try:
        result = float(minuend) - float(subtrahend)
        return str(result)
    except Exception as e:
        return f"Subtraction error: {str(e)}"

def perform_multiplication(
    numbers: Annotated[list, "List of numbers to be multiplied"]
) -> str:
    """Perform multiplication operation"""
    try:
        result = 1.0
        for num in numbers:
            result *= float(num)
        return str(result)
    except Exception as e:
        return f"Multiplication error: {str(e)}"

def perform_division(
    dividend: Annotated[str, "Dividend"],
    divisor: Annotated[str, "Divisor"]
) -> str:
    """Perform division operation"""
    try:
        if float(divisor) == 0:
            return "Error: Divisor cannot be zero"
        result = float(dividend) / float(divisor)
        return str(result)
    except Exception as e:
        return f"Division error: {str(e)}"

# Maintain the agent_tools dictionary
agent_tools = {
    "calculator_coordinator": [talk_with_human],
    "addition_expert": [perform_addition],
    "subtraction_expert": [perform_subtraction],
    "multiplication_expert": [perform_multiplication],
    "division_expert": [perform_division]
}
print( 1*96.3/58.21365895+9*3.659-9.365)