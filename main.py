import os, json, socket

path = input('Enter the path of the json: ')
if not os.path.exists(path):
    raise Exception('Could not find this file')

port = input('Enter a port: ')
try:
    port = int(port)
except:
    raise Exception('The port must be a number')

ip = '127.0.0.1'

script = '''import System;import Fiddler;class Handlers {static function OnBeforeResponse(oSession: Session) {if (oSession.PathAndQuery.StartsWith("/fortnite/api/matchmaking/session/")) {'''
script += f'''var json = Fiddler.WebFormats.JSON.JsonDecode(oSession.GetResponseBodyAsString()).JSONObject;json["serverAddress"] = "{ip}";json["serverPort"] = {port};'''
script += '''oSession.utilSetResponseBody(Fiddler.WebFormats.JSON.JsonEncode(json));}}}'''

open('matchmaking_fiddler.cs', 'w+').write(script)

clients = {}
packets = json.loads(open(path).read())
length = len(packets)

# Start the Server and wait for the Client to send packets!
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

print('\nWaiting for a Client to send packets..\n')
while True: # Wait for the packets
    data, addr = sock.recvfrom(1024)
    if not f'{addr[0]}:{addr[1]}' in clients:
        clients[f'{addr[0]}:{addr[1]}'] = 0

    clients[f'{addr[0]}:{addr[1]}'] += 1

    if clients[f'{addr[0]}:{addr[1]}'] > length:
        pass # Should not happen
    else:
        for packet in packets[clients[f'{addr[0]}:{addr[1]}']:]:
            if packet['from_server']:
                sock.sendto(bytes.fromhex(packet['payload']), addr)
            if not packet['from_server']:
                break
            clients[f'{addr[0]}:{addr[1]}'] += 1