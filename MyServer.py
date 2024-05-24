#!/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Zhou Yukai
"""

import sys, signal
import http.server
import socketserver
import os
import mimetypes
import logging
import socket
from datetime import datetime

DEFAULT_HTML="""
    <html>
    <head><title>Welcome</title></head>
    <body>
        <h1>Welcome to My Server</h1>
        <p>Unfortunately, there is no any content to show you.</p>
        <p>Because the index.html file is missing.</p>
    </body>
    </html>
"""
DEFAULT_HOST  = 'localhost'
DEFAULT_PORT  = 8080

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class MyCustomRequestHandler(http.server.BaseHTTPRequestHandler):
    current_working_directory = os.getcwd()
    def do_GET(self): 
        access_allow_dir = self.current_working_directory
        if len(self.path) == 1:

            if os.path.exists(os.path.join(access_allow_dir, 'index.html')):
                self.path = 'index.html'
                file_path = os.path.join(access_allow_dir, self.path)
            else:
               
               self.send_response(200)
               self.send_header('Content-Type', 'text/html')
               self.end_headers()
               self.wfile.write(DEFAULT_HTML.encode())
               return
        else:
            file_path = os.path.join(access_allow_dir, self.path.strip('/'))
            file_path = os.path.realpath(file_path)
            
        
        self.handle_file_request(file_path, access_allow_dir)

            
    def handle_file_request(self,file_path,access_allow_dir):
        access_allow_dir_std = os.path.realpath(access_allow_dir)
        file_path = os.path.realpath(file_path)
        try:
            print(file_path)
            print(access_allow_dir_std)
            if not file_path.startswith(access_allow_dir_std):
               raise ValueError
                
            if os.path.isdir(file_path):
                raise IsADirectoryError
        
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                raise FileNotFoundError
            file_size = os.path.getsize(file_path)
            
            new_modified_time=datetime.fromtimestamp(os.path.getmtime(file_path)).replace(microsecond=0)
          
            new_modified_str=new_modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            if "If-Modified-Since" in self.headers:

                old_modified_time= datetime.strptime(self.headers['If-Modified-Since'], '%a, %d %b %Y %H:%M:%S GMT')
                print("new modified time: ",new_modified_time)
                print("old modified time: ",old_modified_time)
                if new_modified_time <= old_modified_time:
                    
                    self.send_response(304)
                    self.end_headers()
                    return 
                
            self.send_response(200)
            
            MIME_TYPE=mimetypes.guess_type(file_path)[0]
            if MIME_TYPE:
                self.send_header('Content-Type', MIME_TYPE)
            else:
                self.send_header('Content-Type', 'application/octet-stream')
                
            self.setup_cache_control(MIME_TYPE)
          
            self.send_header('Content-Length', str(file_size))
            self.send_header('Last-Modified', new_modified_str)
            self.end_headers()
            
            with open(file_path,'rb') as file:
                    self.wfile.write(file.read())
                    
        except ValueError:
            self.send_error_page(403, " Access denied")
            logging.error("Access to incorrect directory")
          
        except (FileNotFoundError, IOError, IsADirectoryError) as e:
            self.send_error_page(404, "File Not Found")
            logging.error(f"File error on path {file_path}: {str(e)}")
        
        except Exception as e:
            self.send_error_page(500, "Unexpect Error")
            logging.error("Unexpect Error of Server: %s" % str(e))
            
    def setup_cache_control(self,MIME_TYPE):
        if MIME_TYPE in ['image/jpeg', 'image/png', 'text/css', 'application/javascript',
                         'application/pdf']:
            self.send_header('Cache-Control', 'public, max-age=7200')
        elif MIME_TYPE in ['text/html']:
            self.send_header('Cache-Control', 'public, max-age=3600')
        else:
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        
      
    def send_error_page(self,code,message):
        self.send_response(code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        html_contents = f"""
        <html>
            <head><title>{code} {message}</title></head>
            <body><h1>{code} {message}</h1></body>
        </html>
        """
        self.wfile.write(html_contents.encode())
 

class MyServer:
    def __init__(self,host,post,RequestHandler):
        self.server = socketserver.ThreadingTCPServer((host, port), RequestHandler)
        self.server.daemon_threads = True
        self.server.allow_reuse_address = True     
        
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        try:            
            logging.info(f"Server starting on port: {port} and host: {host}")
            print("Ready to serve...")
            while True:
                self.server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server is shutting down.")
            
    def signal_handler(self,signal, frame):
        logging.info('Exiting http server (Ctrl+C pressed)')
        try:
            self.server.server_close()
        finally:
            sys.exit(0)
        


if __name__ == '__main__':
    try:
        if len(sys.argv) > 2:
            host = sys.argv[1]
            port = int(sys.argv[2])
        elif len(sys.argv) == 2:
            host=DEFAULT_HOST
            port =int(sys.argv[1])
        else:
            host = DEFAULT_HOST
            port = DEFAULT_PORT 
        if not (1 <= port <= 65535):
                raise ValueError("Port number must be between 1 and 65535.")
        server = MyServer(host, port, MyCustomRequestHandler)
        server.run()
        
    except ValueError as e:
        print(f"Error type: {e}")
        sys.exit(1)
    except socket.gaierror as e:
        print(f"Unresolvable hostname: {host}, error type: {e}")
        sys.exit(1)
    except socket.error:
        print("Illegal IP address")
        sys.exit(1)
        


        