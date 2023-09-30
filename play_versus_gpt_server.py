from http.server import SimpleHTTPRequestHandler
import socketserver
from urllib.parse import unquote_plus
import openai


model = "gpt-3.5-turbo-instruct"
with open("openai_api_key.txt", "r") as f:
	openai.api_key = f.readline().replace("\n", "")

with open("pgn_headers.txt", "r") as f:
  pgn_header = f.read()

PORT = 8000

class CustomHandler(SimpleHTTPRequestHandler):
  def do_POST(self):
    def send_response(return_string):
      print("Sending response")
      self.send_response(200)
      self.send_header("Content-type", "text/plain")
      self.end_headers()
      self.wfile.write(bytes(return_string, "utf-8"))

    content_length = int(self.headers["Content-Length"])
    post_data = self.rfile.read(content_length)
    post_data_str = post_data.decode("utf-8")
    key_values = post_data_str.split("&")
    
    if self.path == "/make_move":
      print("posted to make_move")
      have_pgn = False
      for key_value in key_values:
        key, value = key_value.split("=")
        if key == "pgn":
          pgn = unquote_plus(value)
          have_pgn = True
          break
      
      if not have_pgn:
        send_response("Error")
        return
      
      completion = openai.Completion.create(model=model, prompt=pgn_header + pgn, max_tokens = 7)
      completion_text = completion["choices"][0]["text"]
      move = completion_text.strip().split()[0]
      print("GPT response: " + completion_text)

      send_response(move)

httpd = socketserver.TCPServer(("", PORT), CustomHandler)
httpd.allow_reuse_address = True
print("serving at port", PORT)
httpd.serve_forever()
