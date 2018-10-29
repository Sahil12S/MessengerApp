from concurrent import futures
import time
import sys

import grpc

import users_pb2
import users_pb2_grpc

import yaml

from classes import lrucache


# read config.yaml
with open("serverConfig.yaml", "r") as file_descriptor:
    DATA = yaml.load(file_descriptor)

_ONE_DAY_IN_SECONDS_ = 60 * 60 * 24
LRU_CACHE_SIZE = DATA['max_num_messages_per_user']
LRU_CACHE_LIFE = _ONE_DAY_IN_SECONDS_         # in seconds
RATE_LIMIT = DATA['max_call_per_30_seconds_per_user']             # number of messages you can send in 10 seconds
RATE_LIMIT_TIME = 30

class UsersService(users_pb2_grpc.UsersServicer):
    def __init__(self):
        """
        This is default functions which initializes few variables on when called.
        """
        self.message_list = {}
        self.user = ''
        self.registeredUsers = []
        self.userRequesting = {}
        self.unreadMessageCount = {}    # dict of dict. {key(user), {key(otherUser in coversation), count of unread msgs}}
        self.number_of_messages_sent = {}
        for usr in DATA['users']:
            self.registeredUsers.append(users_pb2.User(username=usr))
            self.unreadMessageCount[usr] = {}
            self.number_of_messages_sent[usr] = []


    # CreateUser creates a new user.
    # @param request: a string request with username.
    # @return: returns true if user created, false otherwise.
    def CreateUser(self, request, context):
        """
        This function is called whenever a new user registers for chat.
        """
        # Create user object of the request
        user = users_pb2.User(username=request.user)
        if user not in self.registeredUsers:
            return users_pb2.RegistrationResponse(isAvailable = False)
        return users_pb2.RegistrationResponse(isAvailable = True)


    # Get list of online users.
    # @param request: Empty request.
    # @return: stream of online users.
    def GetOnlineUsers(self, request, context):
        """
        This function streams list of all online users.
        """
        for user in self.registeredUsers:
            yield users_pb2.AllOnlineUsers(users=user)


    # Connect with an online user to start conversation.
    # @param request: object of usernames who wants to have conversation.
    # @return: True if successfully created, false otherwise.
    def ConnectWithUser (self,request, context):
        conversing_users = [request.user1.username, request.user2.username]
        self.userRequesting[request.user2.username] = users_pb2.User(username=request.user1.username)
        conversing_users.sort()
        new_key = conversing_users[0] + "-" + conversing_users[1]
        
        for online_user in self.registeredUsers:
            if (online_user.username == request.user2.username):
                if new_key not in self.message_list:
                    self.message_list[new_key] = lrucache.Cache(LRU_CACHE_SIZE)

                return users_pb2.RegistrationResponse(isAvailable=True)
        return users_pb2.RegistrationResponse(isAvailable=False)


    # Check if anyone wants to chat with someone.
    def CheckRequest (self, request, context):
        if request.username in self.userRequesting:
            return self.userRequesting[request.username]
        else:
            return users_pb2.User(username="NONE")



    # Check if user crossed the message limit within the time frame.
    # @return: True if users is within limit. False if limit is crossed.
    def checkLimit(self, user, receive_time):
        """
        Check the rate limit
        """
        l = len(self.number_of_messages_sent[user])

        if l == 0:
            self.number_of_messages_sent[user].append(receive_time)
            return True     # true if is under limit
        
        i = 0
        while i < l:
            diff = receive_time - self.number_of_messages_sent[user][i]
            if l == RATE_LIMIT:
                if diff <= RATE_LIMIT_TIME:
                    return False
                else:
                    i += 1
            else:
                if diff > RATE_LIMIT_TIME:
                    i += 1
                else:
                    break

        self.number_of_messages_sent[user] = self.number_of_messages_sent[user][i:]
        self.number_of_messages_sent[user].append(receive_time)
        return True



    # SendMessge to allow client to send a request.
    # @param request: stream of UserNote objects
    # @return: stream of empty objet
    def SendMessage(self, request, context):
        """
        This function is called when a user sends a message.
        """
        for new_msg in request:
            users = new_msg.username.split("-")
            sender = users[0]
            receiver = users[1]

            users.sort()
            key = users[0] + "-" + users[1]
            
            receive_time = time.time()
            isUnderLimit = self.checkLimit(sender, receive_time)

            if isUnderLimit:
                self.message_list[key].set(receive_time, new_msg.message)
                if self.unreadMessageCount[sender][receiver] < 5:
                    self.unreadMessageCount[sender][receiver] += 1
                if self.unreadMessageCount[receiver][sender] < 5:
                    self.unreadMessageCount[receiver][sender] += 1
                
                yield users_pb2.Warning(warning_message="")
            else:
                yield users_pb2.Warning(warning_message="[SPARTAN]: WARNING!! You crossed limit of " + str(RATE_LIMIT) + " messages in " + str(RATE_LIMIT_TIME) + " seconds")


    # StreamMessage keeps running and stream all new messages to client.
    # @param request: emptry request
    # @return: stream of UserNote objcets
    def StreamMessages(self, request, context):
        """
        This function is called to continously stream new messages.
        """
        users = request.username.split("-")
        streamer = users[0]
        otherUser = users[1]
        users.sort()
        key = users[0] + "-" + users[1]
        try:
            while True:
                num_of_older_msg_deleted = self.message_list[key].deleteOlder(LRU_CACHE_LIFE)
                try:
                    self.unreadMessageCount[streamer][otherUser] = max(0, self.unreadMessageCount[streamer][otherUser] - num_of_older_msg_deleted)
                except KeyError:
                    self.unreadMessageCount[streamer][otherUser] = 0

                try:
                    self.unreadMessageCount[otherUser][streamer] = max(0, self.unreadMessageCount[otherUser][streamer] - num_of_older_msg_deleted)
                except KeyError:
                    self.unreadMessageCount[otherUser][streamer] = 0

                new_messages = self.message_list[key].display()

                while self.unreadMessageCount[streamer][otherUser] > 0:
                    index = len(new_messages) - self.unreadMessageCount[streamer][otherUser]
                    try:
                        new_message = new_messages[index]
                    except KeyError:
                        continue
                    if self.unreadMessageCount[streamer][otherUser] > 0:
                        self.unreadMessageCount[streamer][otherUser] -= 1
                    yield new_message
                time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit(0)




def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServicer_to_server(UsersService(), server)
    
    ip = '127.0.0.1'
    port = DATA['port']
    print('Spartan server started on port {}. . . '.format(port))

    server.add_insecure_port('{}:{}'.format(ip, port))
    server.start()
    
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS_)
    except KeyboardInterrupt:
        server.stop(0)

    

if __name__ == '__main__':
    main()
