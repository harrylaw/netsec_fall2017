"""Ruihui "Harry" Luo's assignment 1[e]"""

import packets
from playground.network.devices.vnic.connect import getConnector
from asyncio import get_event_loop
from playground.network.packet import PacketType
from asyncio import Protocol
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
from playground import Connector, setConnector


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
            if isinstance(packet, packets.CheckUsername) and self.state == 0:
                print("Server: Server receives CheckUsername packet.")
                username_availability = self.check_username_availability_in_database(packet.username)
                new_packet = packets.UsernameAvailability()
                new_packet.username_availability = username_availability
                new_packet_se = new_packet.__serialize__()
                self.state += 1
                self.transport.write(new_packet_se)
                print("Server: Server sends UsernameAvailability packet.")
            elif isinstance(packet, packets.SignUpRequest) and self.state == 1:
                print("Server: Server receives SignUp packet.")
                sign_up_result = self.sign_up_to_database(packet.username, packet.password, packet.email)
                new_packet = packets.SignUpResult()
                if sign_up_result[0]:
                    new_packet.result = True
                    new_packet.user_id = sign_up_result[1]
                else:
                    new_packet.result = False
                    new_packet.user_id = 0
                new_packet_se = new_packet.__serialize__()
                self.transport.write(new_packet_se)
                print("Server: Server sends SignUpResult packet.")
            else:
                print("Server: Wrong packet received on server side.")
                break

    def connection_lost(self, exc):
        self.transport = None

    def check_username_availability_in_database(self, username):  # mock database query method
        return True

    def sign_up_to_database(self, username, password, email):  # mock database query method
        return [True, 1]


class PassThroughLayer1(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        higher_transport = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higher_transport)

    def data_received(self, data):
        print("Server: Data passes up PassThroughLayer1.")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.transport = None
        self.higherProtocol().connection_lost()


class PassThroughLayer2(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        higher_transport = StackingTransport(self.transport)
        self.higherProtocol().connection_made(higher_transport)

    def data_received(self, data):
        print("Server: Data passes up PassThroughLayer2.")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.transport = None
        self.higherProtocol().connection_lost()


if __name__ == "__main__":
    loop = get_event_loop()
    loop.set_debug(enabled=True)

    factory = StackingProtocolFactory(lambda: PassThroughLayer1(), lambda: PassThroughLayer2())
    ptConnector = Connector(protocolStack=factory)
    setConnector("passThrough", ptConnector)
    coro = getConnector("passThrough").create_playground_server(lambda: ServerProtocol(), 101)
    server = loop.run_until_complete(coro)
    print("Server Started at {}".format(server.sockets[0].gethostname()))
    loop.run_forever()
    loop.close()
