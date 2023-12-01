import threading
import socket
import sys

class Client_Side:
    def __init__(self):
        self.ClientMultiSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = '127.0.0.1'
        self.port =20033
        self.clientName = input("Enter your first name: ")
        print('Waiting for connection response')
        self.threadLists = []
        

    
    def run(self):
        try:
            self.ClientMultiSocket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))
        
        getServerThread = threading.Thread(target=self.getFromServer)
        getServerThread.start()
        self.threadLists.append(getServerThread)
        
        # STARTING THREAD FOR SENDING MESSAGES FROM SERVER
        sendThread = threading.Thread(target=self.sendtoServer)
        sendThread.start()
        self.threadLists.append(sendThread)
        
        
    def sendtoServer(self):
        while True:
            message = '{} {}'.format(self.clientName, input(''))
            try:
                self.ClientMultiSocket.send(message.encode('utf-8'))
            except:
                sys.exit(-1)
                
    def getFromServer(self):
                while True:
                    try:
                        message = self.ClientMultiSocket.recv(1024).decode('utf-8')
                        if message == 'GetUserName':
                            self.ClientMultiSocket.send(self.clientName.encode('utf-8'))
                        elif message == 'exit':
                            sys.exit(-1)
                        
                        
                        elif message == 'GetRoomNames':
                            rooms = ''
                            rooms = input('Enter the room names:')
                            self.ClientMultiSocket.send(rooms.encode('utf-8'))
                        
                        else:
                            print(message,'\n')
                    
                    except Exception as e:
                        print('Server is not acknowledging',e.args)
                        self.ClientMultiSocket.close()
                        sys.exit(-1)
                


if __name__ == '__main__':
    client = Client_Side()
    client.run()
