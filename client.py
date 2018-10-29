import sys
import time
import threading

import yaml
from Crypto.Cipher import AES

import grpc

import users_pb2_grpc
import users_pb2


class Client:
    uname = ''
    conversation = ''


    # Initialize connection
    def __init__(self, ip, port):
        """
        Connection is created in this function.
        """
        self.ip = ip
        self.port = port
        self.Connect_to_server()
        print("[SPARTAN] Connected to Spartan Server at port {}.".format(self.port))
        

    # Makes a connection with server.
    def Connect_to_server(self):
        channel = grpc.insecure_channel('{}:{}'.format(self.ip, str(self.port)))
        # Try connecting to server for 10 seconds
        try:
            grpc.channel_ready_future(channel).result(timeout=10)
        except grpc.FutureTimeoutError:
            sys.exit("[SPARTAN] Error connecting to server.")

        self.stub = users_pb2_grpc.UsersStub(channel)

    
    # Registers a new user.
    def NewUser(self, uname):
        self.uname = uname
        self.uname.lower()
        response = self.stub.CreateUser(users_pb2.NewUserRequest(user=self.uname))

        while(not response.isAvailable):
            print("[SPARTAN] User is not registered with service!!")
            sys.exit(0)


    # Set key file
    def setKeyFile(self, name):
        key_file = open(name, "rb")
        self.key = key_file.read()


    # Encrypt Message
    def encryptMessage(self, message):
        cipher = AES.new(self.key, AES.MODE_EAX)
        data = message.encode('utf-8')
        cipher_text, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce, tag, cipher_text
    

    # Decrypt message
    def decryptMessage(self, content):
        cipher = AES.new(self.key, AES.MODE_EAX, content.nonce)
        data = cipher.decrypt_and_verify(content.ciphertext, content.tag)
        return data.decode('ascii')


    # Get list of all online uses.
    def OnlineUsers(self):
        userlist = []
        for resp in self.stub.GetOnlineUsers(users_pb2.Empty()):
            if resp.users.username != self.uname:
                userlist.append(resp.users.username)
        
        print("[SPARTAN] User list: " + ",".join(userlist))


    # Select user to start chat with and check if there is someone requesting to chat.
    def selectUserToChatWith(self):
        resp = self.stub.CheckRequest(users_pb2.User(username=self.uname))
        if resp.username != "NONE":
            tempInput = input("[SPARTAN] {} is requesting to chat with you. Enter 'yes' to accept or different user: ".format(resp.username))
            if tempInput == "yes":
                anotherUser = resp.username
            else:
                anotherUser = tempInput
        else:
            anotherUser = input("[SPARTAN] Enter user whom you want to chat with: ")
        anotherUser.lower()
        if anotherUser != self.uname:
            request = users_pb2.OneOnOneChat(
                user1 = users_pb2.User(username=self.uname),
                user2 = users_pb2.User(username=anotherUser)
            )
            response = self.stub.ConnectWithUser(request)
            if not response.isAvailable:
                print("[SPARTAN] Cannot find the user you specified. Please try again.")
                return self.selectUserToChatWith()
            else:
                print("[SPARTAN] You are now ready to chat with {}.".format(anotherUser))
                self.conversation = self.uname + '-' + anotherUser
                return True
        else:
            print("[SPARTAN] Cannot chat with yourself. Please try again")
            return self.selectUserToChatWith()
            
        
    # Listen for any incoming messages.
    def Listen_for_messages(self):
        for msg in self.stub.StreamMessages(users_pb2.User(username=self.conversation)):
            print('[{}] > {}'.format(msg.sender, self.decryptMessage(msg.content)))

    
    # Create a new message.
    # @param message: message user wants to send.
    # @return: UserNote object.
    def CreateMessage(self, message):
        nonce, tag, cipher_text = self.encryptMessage(message)
        return users_pb2.UserNote(
            username=self.conversation,
            message=users_pb2.Chat(
                sender=self.uname, 
                content=users_pb2.Content(
                    nonce=nonce,
                    tag=tag,
                    ciphertext=cipher_text
                ))
        )


    # Iteratively get messages from user.
    # @yield: UserNote objects
    def GetMessages(self):
        while True:
            message = input()
            if message == '@q':
                break
            msg = self.CreateMessage(message)
            yield msg
            time.sleep(0.2)


    # Starts a new chat,
    def Start_chat(self):
        responses = self.stub.SendMessage(self.GetMessages())
        for resp in responses:
            if len(resp.warning_message) > 0:
                print(resp.warning_message)
            else:
                continue


def main():
    with open("clientConfig.yaml", "r") as file_descriptor:
        data = yaml.load(file_descriptor)
    file_name = data['key']
    ip = data['ip']
    port = data['port']
    c = Client(ip, port)        # step 1
    c.NewUser(sys.argv[1])      # step 2
    c.OnlineUsers()             # step 3
    c.setKeyFile(file_name)
    
    if c.selectUserToChatWith() :    # step 4
        # Start a separate thread for streaming function.
        # Running in separate thread, user will continously get a replies.
        threading.Thread(target=c.Listen_for_messages, args=(), daemon=True).start()
        c.Start_chat()


if __name__ == '__main__':
    main()





#########################################
#   Flow of chat                        #
#---------------------------------------#
#                                       #
# 1. User connects to server.           #
# 2. Registers with a username.         #
# 3. Looks for online users.            #
# 4. Provide username of other person.  #
# 5. Listen for messages.               #
# 6. Send message.                      #
#                                       #
#########################################