import urllib.parse


class URLParser:
    def parse_from_line(self, steam_address: str, line: str) -> str:
        line = line.strip()
        line = line.split(":")[0]
        line = line.replace('"', "")
        line = line.replace(" ", "%20")
        line = line.replace("|", "%7C")
        line = line.replace("(", "%28")
        line = line.replace(")", "%29")
        result = f"{steam_address}/{line}"
        return result

    def parse(self, steam_address: str, weapon: str, skin_name: str, condition: str):
        initial_url = f"{weapon} | {skin_name} ({condition})"
        # initial_url = initial_url.replace(" ", "%20")
        # initial_url = initial_url.replace("|", "%7C")
        # initial_url = initial_url.replace("(", "%28")
        # initial_url = initial_url.replace(")", "%29")
        initial_url = urllib.parse.quote_plus(initial_url)
        initial_url = initial_url.replace("+", "%20")
        return f"{steam_address}/{initial_url}"