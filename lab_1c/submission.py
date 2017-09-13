"""Ruihui "Harry" Luo's assignment 1[c]"""

from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BOOL
from playground.asyncio_lib.testing import TestLoopEx
from playground.network.testing import MockTransportToStorageStream, MockTransportToProtocol
from asyncio import Protocol, set_event_loop


class CheckUsername(PacketType):
    DEFINITION_IDENTIFIER = "Lab_1b.Ruihui_Luo.CheckUsername"
    DEFINITION_VERSION = "1.0"
    FIELDS = [("username", STRING)]


class UsernameAvailability(PacketType):
    DEFINITION_IDENTIFIER = "Lab_1b.Ruihui_Luo.UsernameAvailability"
    DEFINITION_VERSION = "1.0"
    FIELDS = [("username_availability", BOOL)]


class SignUpRequest(PacketType):
    DEFINITION_IDENTIFIER = "Lab_1b.Ruihui_Luo.SignUpRequest"
    DEFINITION_VERSION = "1.0"
    FIELDS = [("username", STRING), ("password", STRING), ("email", STRING)]


class SignUpResult(PacketType):
    DEFINITION_IDENTIFIER = "Lab_1b.Ruihui_Luo.SignUpResult"
    DEFINITION_VERSION = "1.0"
    FIELDS = [("result", BOOL), ("user_id", UINT32)]


class ClientProtocol(Protocol):
    def __init__(self, username, password, email):
        self.transport = None
        self.deserializer = PacketType.Deserializer()
        self.state = 0
        self.username = username
        self.password = password
        self.email = email

    def connection_made(self, transport):
        self.transport = transport
        print("Client: Connected to client.")

    def data_received(self, data):
        self.deserializer.update(data)
        for packet in self.deserializer.nextPackets():
            if isinstance(packet, UsernameAvailability) and self.state == 0:
                print("Client: Client receives UsernameAvailability packet.")
                if packet.username_availability:
                    print("Client: Username '" + self.username + "' is available")
                    new_packet = SignUpRequest()
                    new_packet.username = self.username
                    new_packet.password = self.password
                    new_packet.email = self.email
                    new_packet_se = new_packet.__serialize__()
                    self.state += 1
                    self.transport.write(new_packet_se)
                else:
                    print("Client: Username '" + self.username + "' is unavailable.")
            elif isinstance(packet, SignUpResult) and self.state == 1:
                print("Client: Client receives SignUpResult packet.")
                if packet.result:
                    print("Client: Signed up successfully. Username is '" + self.username + "'.")
                else:
                    print("Client: Failed to sign up.")
            else:
                print(type(packet))
                print("Client: Wrong packet received on client side.")
                break

    def connection_lost(self, exc):
        self.transport = None

    def sign_up(self):
        packet = CheckUsername()
        packet.username = self.username
        packet_se = packet.__serialize__()
        self.transport.write(packet_se)


class ServerProtocol(Protocol):
    def __init__(self):
        self.transport = None
        self.deserializer = PacketType.Deserializer()
        self.state = 0

    def connection_made(self, transport):
        self.transport = transport
        print("Server: Connected to server.")

    def data_received(self, data):
        self.deserializer.update(data)
        for packet in self.deserializer.nextPackets():
            if isinstance(packet, CheckUsername) and self.state == 0:
                print("Server: Server receives CheckUsername packet.")
                username_availability = self.check_username_availability_in_database(packet.username)
                new_packet = UsernameAvailability()
                new_packet.username_availability = username_availability
                new_packet_se = new_packet.__serialize__()
                self.state += 1
                self.transport.write(new_packet_se)
            elif isinstance(packet, SignUpRequest) and self.state == 1:
                print("Server: Server receives SignUp packet.")
                sign_up_result = self.sign_up_to_database(packet.username, packet.password, packet.email)
                new_packet = SignUpResult()
                if sign_up_result[0]:
                    new_packet.result = True
                    new_packet.user_id = sign_up_result[1]
                else:
                    new_packet.result = False
                    new_packet.user_id = 0
                new_packet_se = new_packet.__serialize__()
                self.transport.write(new_packet_se)
            else:
                print("Server: Wrong packet received on server side.")
                break

    def connection_lost(self, exc):
        self.transport = None

    def check_username_availability_in_database(self, username):  # mock database query method
        return True

    def sign_up_to_database(self, username, password, email):  # mock database query method
        return [True, 1]


def basic_unit_test():
    set_event_loop(TestLoopEx())
    client = ClientProtocol("harry", "123456", "harry@gmail.com")
    server = ServerProtocol()

    transport_to_server = MockTransportToProtocol(client)
    transport_to_client = MockTransportToProtocol(server)
    transport_to_server.setRemoteTransport(transport_to_client)
    transport_to_client.setRemoteTransport(transport_to_server)
    client.connection_made(transport_to_server)
    server.connection_made(transport_to_client)

    client.sign_up()


if __name__ == "__main__":
    basic_unit_test()
