
# For debugging with VS code. Open the palette (ctrl + shift + p) ->
# python: select interpreter, path to ~/imdb_test/env/bin/python
from imdb_test.src.Webscraper import imdb_webscraper as ws

url_list = ws.make_url()
first_page = url_list[0]
soup_list = ws.parse_html([first_page])
container = soup_list[0][16]

test = ws.clean_html(container)
test