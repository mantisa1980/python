import asyncio
import websockets
import subprocess

# Function to tail the syslog file and send new lines to WebSocket clients
async def tail_syslog_and_send_messages(websocket, path):
    try:
        tail_command = ["tail", "-f", "/var/log/syslog"]
        #grep_command = ["grep", "-v", "FILTER PATTERN"]
        grep_command1 = ["grep", "-E" ,"-v", "ArkWeb"]
        grep_command2 = ["grep", "-E", "-v", "AF_INET"]
        tail_process = subprocess.Popen(tail_command, stdout=subprocess.PIPE)
        grep_process1 = subprocess.Popen(grep_command1, stdin=tail_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        grep_process2 = subprocess.Popen(grep_command2, stdin=grep_process1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        fin_process = grep_process2
        while True:
            line = fin_process.stdout.readline()
            if not line:
                break
            await websocket.send(line.strip())

    except Exception as e:
        print(f"Error: {e}")

# Create a WebSocket server listening on all available network interfaces
def websocket_main():
    #start_server = websockets.serve(tail_syslog_and_send_messages, "0.0.0.0", 8765)
    start_server = websockets.serve(tail_syslog_and_send_messages, "0.0.0.0", 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    pass

if __name__ == "__main__":
    websocket_main()
