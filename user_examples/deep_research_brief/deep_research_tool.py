
import sqlite3
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from duckduckgo_search import DDGS  # Requires installation: pip install duckduckgo-search
import time
import logging

# --- Database Configuration ---
DB_NAME = "process_data.db"
REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)  # Ensure the reports directory exists

# --- Logging Configuration (for retries and error handling) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Database Initialization ---
def init_db():
    """Initialize the database and create required tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create conversation records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')

    # Create research reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    logger.info(f"Database '{DB_NAME}' initialized.")


# --- Tool Function Implementations ---

# 1. ask_human (simulated as input)
def talk_with_user(prompt: str = "") -> str:
    """
    Simulate asking the user a question and getting input.
    In real applications, this might be a more complex interaction interface.
    """
    if prompt:
        print(prompt)
    user_input = input("User: ")
    return user_input


# 2. write_conversation
def write_conversation(conversation_str: str) -> int:
    """
    Store the conversation string into the database.
    Returns the ID of the inserted record.
    """
    init_db()  # Ensure database is initialized
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (content) VALUES (?)", (conversation_str,))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Conversation written with ID: {report_id}")
    return report_id


# 3. get_conversations
def get_conversations(conversation_ids: list[int]) -> list[str]:
    """
    Query conversation records by ID list.
    Returns a list of conversation contents.
    """
    init_db()  # Ensure database is initialized
    if not conversation_ids:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Use placeholders to prevent SQL injection
    placeholders = ','.join('?' * len(conversation_ids))
    query = f"SELECT content FROM conversations WHERE id IN ({placeholders})"
    cursor.execute(query, conversation_ids)

    results = cursor.fetchall()
    conn.close()

    # fetchall returns tuples like [(content1,), (content2,), ...]
    return [row[0] for row in results]


# 4. duckduckgo_search (with retry mechanism)
def duckduckgo_search(query: str, max_retries: int = 3, backoff_factor: float = 1.0) -> list[dict]:
    """
    Perform a search using the duckduckgo-search library, with retry mechanism.
    """
    init_db()  # Ensure database is initialized (not strictly needed here but kept for consistency)
    results = []
    for attempt in range(max_retries + 1):
        try:
            with DDGS() as ddgs:
                # DDGS.text() returns a generator; convert to list
                results = list(ddgs.text(query, max_results=10))
            logger.info(f"Search successful for query: {query}")
            return results  # Return results on success
        except Exception as e:
            logger.warning(f"Search attempt {attempt + 1} failed for query '{query}': {e}")
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"All search attempts failed for query '{query}'.")
                # Can choose to raise exception or return empty list
                # raise e
    return results  # Return last attempt's result (could be empty)


def write_report(content: str) -> int:
    """
    Write research results into the database.
    Returns the ID of the inserted record.
    """
    init_db()  # Ensure database is initialized
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO research_reports (content) VALUES (?)", (content,))
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Research report written with ID: {report_id}")
    return report_id


def get_research_raw_info(report_ids: list[int]) -> list[str]:
    """
    Query research report content by ID list.
    Returns a list of report contents.
    """
    init_db()  # Ensure database is initialized
    if not report_ids:
        return []

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Use placeholders to prevent SQL injection
    placeholders = ','.join('?' * len(report_ids))
    query = f"SELECT content FROM research_reports WHERE id IN ({placeholders})"
    cursor.execute(query, report_ids)

    results = cursor.fetchall()
    conn.close()

    # fetchall returns tuples like [(content1,), (content2,), ...]
    return [row[0] for row in results]


def write_final_report(title: str, content: str) -> str:
    """
    Write the final report to a file.
    Returns the file path where the report is stored.
    """
    init_db()  # Ensure database is initialized (not strictly needed here but kept for consistency)
    # Simple filename sanitization to avoid illegal characters
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
    filename = f"{safe_title}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Final report written to: {filepath}")
    return filepath


# --- Initialize Database ---
init_db()

agent_tools_map = {
    "user_clarifier": [
        talk_with_user,
        write_conversation
    ],
    "research_topic_generator": [
        get_conversations
    ],
    "lead_researcher": [
        # No direct tool functions; collaborates via communication with other agents
    ],
    "sub_researcher": [
        duckduckgo_search,
        write_report
    ],
    "report_generation": [
        get_research_raw_info,
        write_final_report
    ],

}

# Example: How to access
# print(agent_tools_map["user_clarifier"])
# Output: ['ask_human', 'write_conversation']

if __name__ == '__main__':
    # Example usage
    print("--- Example: ask_human ---")
    user_response = talk_with_user("Please enter your question: ")  # Uncomment to run interactively
    print(f"You entered: {user_response}")

    print("\n--- Example: write_conversation & get_conversations ---")
    conv_id = write_conversation("User: Hello\nSystem: Hi! How can I help you?\nUser: I want to learn about AI.")
    print(f"Conversation written with ID: {conv_id}")
    retrieved_conv = get_conversations([conv_id])
    print(f"Retrieved conversation: {retrieved_conv}")

    print("\n--- Example: duckduckgo_search ---")
    search_results = duckduckgo_search("Python programming", max_retries=2)
    print(f"Found {len(search_results)} results (titles):")
    for i, res in enumerate(search_results[:3]):  # Print first 3 result titles
        print(f"  {i + 1}. {res.get('title', 'N/A')}")

    print("\n--- Example: fetch_page_content ---")
    if search_results:
        url_to_fetch = search_results[0].get('href', '')
        if url_to_fetch:
            page_content = fetch_page_content(url_to_fetch, max_retries=1, timeout=5)
            print(f"First 200 characters of webpage content: {page_content[:200]}..." if page_content else "Failed to fetch webpage content")

    print("\n--- Example: write_report & get_research_raw_info ---")
    report_content = "Summary of Python research:\n1. Python is an interpreted language.\n2. It is widely used in web development, data science, etc."
    report_id = write_report(report_content)
    print(f"Research report written with ID: {report_id}")
    retrieved_report = get_research_raw_info([report_id])
    print(f"Retrieved research report: {retrieved_report}")

    print("\n--- Example: write_final_report ---")
    final_report_path = write_final_report("Python Research Report", report_content)
    print(f"Final report saved at: {final_report_path}")
