FROM mitmproxy/mitmproxy
 
WORKDIR /app
COPY modify_traffic.py /app/modify_traffic.py
 
CMD ["mitmdump", "-s", "/app/modify_traffic.py", "--mode", "regular", "--listen-host", "0.0.0.0", "--listen-port", "8080"]
 
