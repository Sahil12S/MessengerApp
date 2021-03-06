# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import users_pb2 as users__pb2


class UsersStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SendMessage = channel.stream_stream(
        '/Users/SendMessage',
        request_serializer=users__pb2.UserNote.SerializeToString,
        response_deserializer=users__pb2.Warning.FromString,
        )
    self.StreamMessages = channel.unary_stream(
        '/Users/StreamMessages',
        request_serializer=users__pb2.User.SerializeToString,
        response_deserializer=users__pb2.Chat.FromString,
        )
    self.CreateUser = channel.unary_unary(
        '/Users/CreateUser',
        request_serializer=users__pb2.NewUserRequest.SerializeToString,
        response_deserializer=users__pb2.RegistrationResponse.FromString,
        )
    self.GetOnlineUsers = channel.unary_stream(
        '/Users/GetOnlineUsers',
        request_serializer=users__pb2.Empty.SerializeToString,
        response_deserializer=users__pb2.AllOnlineUsers.FromString,
        )
    self.ConnectWithUser = channel.unary_unary(
        '/Users/ConnectWithUser',
        request_serializer=users__pb2.OneOnOneChat.SerializeToString,
        response_deserializer=users__pb2.RegistrationResponse.FromString,
        )
    self.CheckRequest = channel.unary_unary(
        '/Users/CheckRequest',
        request_serializer=users__pb2.User.SerializeToString,
        response_deserializer=users__pb2.User.FromString,
        )


class UsersServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def SendMessage(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StreamMessages(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateUser(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOnlineUsers(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ConnectWithUser(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CheckRequest(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_UsersServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SendMessage': grpc.stream_stream_rpc_method_handler(
          servicer.SendMessage,
          request_deserializer=users__pb2.UserNote.FromString,
          response_serializer=users__pb2.Warning.SerializeToString,
      ),
      'StreamMessages': grpc.unary_stream_rpc_method_handler(
          servicer.StreamMessages,
          request_deserializer=users__pb2.User.FromString,
          response_serializer=users__pb2.Chat.SerializeToString,
      ),
      'CreateUser': grpc.unary_unary_rpc_method_handler(
          servicer.CreateUser,
          request_deserializer=users__pb2.NewUserRequest.FromString,
          response_serializer=users__pb2.RegistrationResponse.SerializeToString,
      ),
      'GetOnlineUsers': grpc.unary_stream_rpc_method_handler(
          servicer.GetOnlineUsers,
          request_deserializer=users__pb2.Empty.FromString,
          response_serializer=users__pb2.AllOnlineUsers.SerializeToString,
      ),
      'ConnectWithUser': grpc.unary_unary_rpc_method_handler(
          servicer.ConnectWithUser,
          request_deserializer=users__pb2.OneOnOneChat.FromString,
          response_serializer=users__pb2.RegistrationResponse.SerializeToString,
      ),
      'CheckRequest': grpc.unary_unary_rpc_method_handler(
          servicer.CheckRequest,
          request_deserializer=users__pb2.User.FromString,
          response_serializer=users__pb2.User.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Users', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
