from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString
import re

PORT = 8232
BASE_URL = "http://news.ycombinator.com"
SIX_LETTERS_WORDS_RE = re.compile(r"(?<!\w)(\w{6})(?!\w)")


def add_tm_symbol(source):
    return SIX_LETTERS_WORDS_RE.sub(r"\1™", source)


class HnProxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = BASE_URL + self.path
        response = urlopen(url)

        self.send_response(response.status)
        for header in list(response.headers):
            self.send_header(header, response.headers.get(header))
        self.end_headers()
        if response.headers.get_content_type() != "text/html":
            self.wfile.write(response.read())
        else:
            soup = BeautifulSoup(response.read())
            for tag in soup.find_all():
                for child in tag.children:
                    if isinstance(child, NavigableString):
                        child.replace_with(add_tm_symbol(child))

            self.wfile.write(soup.encode(response.headers.get_content_charset()))


if __name__ == "__main__":

    with TCPServer(("", PORT), HnProxy) as server:
        print("serving at ", PORT)
        server.serve_forever()
