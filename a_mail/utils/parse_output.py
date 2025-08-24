import re
from pprint import pprint

import regex as re 

def parse_output_to_dict(output: str):
    patterns = {
        'my_thoughts': r'"my_thoughts"\s*:\s*"(.*?)"',
        'A-mail': r'"A-mail"\s*:\s*(\{(?:[^{}]++|(?1))*\})',  
        'mail_type': r'"mail_type"\s*:\s*"([^"]+)"',
        'sender': r'"sender"\s*:\s*"([^"]+)"',
        'receiver': r'"receiver"\s*:\s*"([^"]+)"',
    }

    extracted = {}
    for k, p in patterns.items():
        m = re.search(p, output, re.S)
        if m:
            extracted[k] = m.group(1) if k != 'A-mail' else m.group(0)

    return extracted

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

