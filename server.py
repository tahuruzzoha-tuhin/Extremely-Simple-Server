import http.server
import socketserver
import sqlite3
import json
import urllib.parse

PORT = 8000

# SQLite3 database initialization
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT)''')
conn.commit()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            tasks = c.execute("SELECT * FROM tasks").fetchall()
            self.wfile.write(json.dumps(tasks).encode('utf-8'))
            return
        elif self.path.startswith('/delete/'):
            task_id = int(self.path.split('/')[-1])
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


    def do_POST(self):
        if self.path == '/add':
            content_length = int(self.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))
            task = post_data['task'][0]
            c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
            conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        elif self.path.startswith('/delete/'):
            task_id = int(self.path.split('/')[-1])
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

        elif self.path.startswith('/edit/'):
            task_id = int(self.path.split('/')[-1])
            content_length = int(self.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))
            updated_task = post_data['task'][0]
            c.execute("UPDATE tasks SET task=? WHERE id=?", (updated_task, task_id))
            conn.commit()
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("Server started at port", PORT)
    httpd.serve_forever()
