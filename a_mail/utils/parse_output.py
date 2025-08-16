import re
from pprint import pprint

def parse_output_to_dict(output:str):
    # Step 1: Regex patterns to capture the required fields
    patterns = {
        'my_thoughts': r'"my_thoughts":\s*"(.*?)"',
        'A-mail': r'"A-mail":\s*\{([^}]+)\}',  # Capture everything inside A-mail block
        'mail_type': r'"mail_type":\s*"([^"]+)"',
        'sender': r'"sender":\s*"([^"]+)"',
        'receiver': r'"receiver":\s*"([^"]+)"'
    }
    extracted_data = {}
    # Step 2: Use regex to extract required fields
    for field, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            extracted_data[field] = match.group(1) if field != 'A-mail' else match.group(
                0)  # Include the full A-mail block

    # Step 3: Return the extracted data
    return extracted_data

def replace_mail_type_with_receive(text: str) -> str:
    """将A-mail中的mail_type字段改为'receive'"""
    # 正则替换 mail_type 的值为 "receive"
    modified_text = re.sub(
        r'("mail_type"\s*:\s*")([^"]*)(")',
        r'\1receive\3',
        text
    )
    return modified_text


if __name__ == '__main__':
    # Example usage:
    json_text = """
    """

    result = parse_output_to_dict(json_text)
    pprint(result)
    print(replace_mail_type_with_receive(result["A-mail"]))

