import socket
import threading
with open('menu.txt', 'r') as menu_file:
                mainMenu = menu_file.read()
clientConnections = []     
deviceName = []    
roomInfo = {} 
eachClientConnectionn = {}    
eachClientElements = {}
                
class Room:
    def __init__(self, name):
        self.allACientConnections = []
        self.allClientNames = []
        self.roomName = name

class User:
    def __init__(self, name):
        self.name = name
        self.everyonejoinrooms = []
        self.thisRoom = ''
        
        
def listRoomsWithMembers(username, room_name):
    name = eachClientConnectionn[username]
    print(len(roomInfo))
    if len(room_name) == 0:
        name.send('Roomname should not be empty. Enter a valid name'.encode('utf-8'))
    elif len(roomInfo) == 0:
        name.send('There are no rooms created.'.encode('utf-8'))
    else:
        name.send(' '.encode('utf-8'))
        reply = f"\n\nMembers of Room '{room_name}':\n"
        if roomInfo[room_name].roomName == room_name:
                found_room = True
                for member in roomInfo[room_name].allClientNames:
                    reply += '\n' + member
                    

        if not found_room:
            reply = f"There was no room with such name. '{room_name}'"
        name.send(f'{reply}'.encode('utf-8'))
        
def multi_threaded_client(connection):
    connection.send(str.encode('Server is operational.:'))
    while True:
        data = connection.recv(2048)
        response = 'Server message: ' + data.decode('utf-8')
        if not data:
            break
        connection.sendall(str.encode(response))
        

def listAllClients(userName):
    clientConn = eachClientConnectionn[userName]
    reply = "\n\nList of Users:\n"
    for client in deviceName:
        reply += '\n'+ str(client)
    reply += '\n'
    clientConn.send(f'{reply}'.encode('utf-8'))
    
#Switching from one room to another           
def switchToRoom(username, roomname):
    user = eachClientElements[username]
    name = eachClientConnectionn[username]
    room = roomInfo[roomname]
    if roomname == user.thisRoom:
        name.send('youve been switched successfully to the room'.encode('utf-8'))
    elif room not in user.everyonejoinrooms:
        name.send('Members only authorized, in order to switch the room please join the room'.encode('utf-8'))
    else:
        user.thisRoom = roomname
        name.send(f'Switched to {roomname}'.encode('utf-8'))
        
#LEAVING CURRENTLY JOINED ROOM
def leaveRoom(username):
    user = eachClientElements[username]
    name = eachClientConnectionn[username]
    if user.thisRoom == '':
        name.send('You are not part of any room'.encode('utf-8'))
    else:
        roomname = user.thisRoom
        room = roomInfo[roomname]
        user.thisRoom = ''
        user.everyonejoinrooms.remove(room)
        roomInfo[roomname].allACientConnections.remove(name)
        roomInfo[roomname].allClientNames.remove(username)
        sendMessageToRoom(f'{username} left the room', roomname)
        name.send('You left the room'.encode('utf-8'))
        print(f'{username} has  left room {roomname}')
        
        
def listAllRooms(userName):
    clientConn = eachClientConnectionn[userName]
    reply = "\nRooms:\n"
    for room in roomInfo:
        print(roomInfo[room].roomName)
        reply += '\n'+ roomInfo[room].roomName
        print(roomInfo[room].allClientNames)
    reply += '\n'
    clientConn.send(f'{reply}'.encode('utf-8'))
        

#JOINING OR CREATING NEW ROOM IF DOES NOT EXISTS
def joinOrCreateRoomIfNotExist(username, room_name):
    name = eachClientConnectionn[username]
    user = eachClientElements[username]
    if len(room_name) == 0:
        name.send('Room name cannot be empty. Enter a valid name')
    elif room_name not in roomInfo:
        room = Room(room_name)
        roomInfo[room_name] = room
        room.allACientConnections.append(name)
        room.allClientNames.append(username)

        user.thisRoom = room_name
        user.everyonejoinrooms.append(room)
        name.send(f'{room_name} created'.encode('utf-8'))
        print(f'{username} has created room {room_name}')
    else:
        room = roomInfo[room_name]
        if room_name in user.everyonejoinrooms:
            name.send('You are already in the room'.encode('utf-8'))
        else:
            room.allACientConnections.append(name)
            room.allClientNames.append(username)
            user.thisRoom = room_name
            user.everyonejoinrooms.append(room)
            sendMessageToRoom(f'{username} joined the room', room_name)
            print(f'{username} has joined room {room_name}')


#REMOVING CLIENT FROM SERVER
def removingClient(username):
    deviceName.remove(username)
    client = eachClientConnectionn[username]
    user = eachClientElements[username]
    user.thisRoom = ''
    for room in user.everyonejoinrooms:
        room.allACientConnections.remove(client)
        room.allClientNames.remove(username)
        sendMessageToRoom(f'{username} left the room', room.roomName)

#SENDING PRIVATE MESSAGE TO OTHER USER
def sendPrivateMessage(message):
    args = message.split(" ")
    user = args[2]
    sender = eachClientConnectionn[args[0]]
    if user not in eachClientConnectionn:
        sender.send('User not found'.encode('utf-8'))
    else:
        reciever = eachClientConnectionn[user]
        msg = ' '.join(args[3:])
        reciever.send(f'[private message] {args[0]}: {msg}'.encode('utf-8'))
        sender.send(f'[private message] {args[0]}: {msg}'.encode('utf-8'))
                      
#SENDING MESSAGE IN A ROOM 
def sendMessageToRoom(message, ROOM_NAME):
    for client in roomInfo[ROOM_NAME].allACientConnections:
        msg = '['+ROOM_NAME+'] '+' '+ message
        client.send(msg.encode('utf-8'))
     
def send_message(username, cmd):
    if not cmd.startswith("$send_room"):
        return "Invalid command. Please use the format: $send_room room_name message"

    # Extract room name and message from the command
    _, room_name, *message_parts = cmd.split()
    message = ' '.join(message_parts)

    if room_name not in roomInfo:
        return "Room doesn't exist."

    room = roomInfo[room_name]
    sender = eachClientConnectionn.get(username)

    if sender not in room.allClientConnections:
        return "This room does not belong to you.."

    formatted_message = f'[{room_name}] {username}: {message}'

    for client in room.allClientConnections:
        client.send(formatted_message.encode('utf-8'))

    return "Message delivered successfully."

        
def closeConnection(username, client):
    name = eachClientConnectionn[username]
    name.send('You are disconnected from the server.'.encode('utf-8'))
    print(f'{username} disconnected from the server')

    # Clean up resources and remove client from lists
    clientConnections.remove(client)
    if username in deviceName:
        removingClient(username)
    quit()
    
#BROADCAST TO ALL
def broadcastMessageFromClient(user,message):
    message = '[Broadcast message from '+user+'] '+ " ".join(message[1:])
    for client in clientConnections:
        client.send(str(message).encode('utf-8')) 

def clientCommands(Client):
    clientName = ''
    userCommandArray = [] 

    commands = {
        '$listAll': lambda: (listAllRooms(clientName), listAllClients(clientName)),
        '$list': lambda: listRoomsWithMembers(userCommandArray[0], ' '.join(userCommandArray[2:])),
        '$create': lambda: joinOrCreateRoomIfNotExist(userCommandArray[0], ' '.join(userCommandArray[2:])),
        '$join': lambda: joinOrCreateRoomIfNotExist(userCommandArray[0], ' '.join(userCommandArray[2:])),
        '$switch': lambda: switchToRoom(userCommandArray[0], userCommandArray[2]),
        '$leave': lambda: leaveRoom(userCommandArray[0]),
        '$private_message': lambda: sendPrivateMessage(userCommand),
        '$broadcast_everyone': lambda: broadcastMessageFromClient(clientName, userCommandArray[1:]),
        '$menu': lambda: clientConn.send(mainMenu.encode('utf-8')),
        '$broadcast_room': lambda: send_message(clientName, userCommandArray),
        '$bye': lambda: closeConnection(clientName, Client)
    }

    while True:
        try:
            userCommand = Client.recv(1024).decode('utf-8')
            userCommandArray = userCommand.split(" ")
            clientConn = eachClientConnectionn[userCommandArray[0]]
            clientName = userCommandArray[0]

            for command, action in commands.items():
                if command in userCommand:
                    action()
                    break
            else:
                if eachClientElements[userCommandArray[0]].thisRoom == '':
                    clientConn.send('Please join a room to send message.'.encode('utf-8'))
                else:
                    msg = ' '.join(userCommandArray[1:])
                    room = eachClientElements[userCommandArray[0]].thisRoom
                    sendMessageToRoom(f'[{userCommandArray[0]}] {msg}',room)

        except Exception as e:
            print("Exception has occurred:", e)
            clientConnections.remove(Client)
            print(f'{clientName} left the room\n')
            if clientName in deviceName:
                removingClient(clientName)
            clientConn.close()
           
            break

def main():
    ServerSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ServerSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '127.0.0.1'
    port = 20033
    ThreadCount = 0
    ServerSideSocket.bind((host, port))
    
    ('Socket is listening..')
    ServerSideSocket.listen()
    print('\nServer has Started at port:' + str(port))

    
    
    
    while True:
        try:
            #Accepting client request
            Client, address = ServerSideSocket.accept()
       
         
            Client.send('GetUserName'.encode('utf-8'))
            username = Client.recv(1024).decode('utf-8')
            print(username)
            
            #ADDING CLIENT NAME TO CLIENT LIST
            deviceName.append(username)
            clientConnections.append(Client)
            
            #STORING USER OBJECT AND CONNECTION OBJECT FOR FUTURE USE
            eachClientElements[username] = User(username)
            eachClientConnectionn[username] = Client
            
            print(f'\nClient connected on {address} with username:{username}')
            Client.send(f'Hi {username}! You have successfully connected to the server!\n'.encode('utf-8'))
            
           
            Client.send(mainMenu.encode('utf-8'))
            #Assigning a separate thread for each client
            clientThread = threading.Thread(target=clientCommands, args=(Client,))
            clientThread.start()
            ThreadCount += 1
            print('Thread /Client Number: ' + str(ThreadCount))
        except Exception as e:
            print('Exception occured: '+ str(e))
            
            
if __name__ == "__main__":
    main()