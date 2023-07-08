import requests
from bs4 import BeautifulSoup

def check_is_valid_code(url: str) -> bool:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        script_tag = soup.find("script", string=lambda t: "isValidCode" in str(t))
        is_valid_code = script_tag.text.split("isValidCode")[1]
        is_valid_code_value = is_valid_code[is_valid_code.find(":") + 1:is_valid_code.find(",")].strip()

        return is_valid_code_value.lower() == "true"
    except Exception as e:
        return False

