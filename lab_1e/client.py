"""Ruihui "Harry" Luo's assignment 1[e]"""

import packets
from playground.network.devices.vnic.connect import getConnector
from asyncio import get_event_loop
from playground.network.packet import PacketType
from asyncio import Protocol
from playground.network.common import StackingProtocol, StackingTransport, StackingProtocolFactory
from playground import Connector, setConnector


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
        self.sign_up()

    def data_received(self, data):
        self.deserializer.update(data)
        for packet in self.deserializer.nextPackets():
            if isinstance(packet, packets.UsernameAvailability) and self.state == 0:
                print("Client: Client receives UsernameAvailability packet.")
                if packet.username_availability:
                    print("Client: Username '" + self.username + "' is available.")
                    new_packet = packets.SignUpRequest()
                    new_packet.username = self.username
                    new_packet.password = self.password
                    new_packet.email = self.email
                    new_packet_se = new_packet.__serialize__()
                    self.state += 1
                    self.transport.write(new_packet_se)
                    print("Client: Client sends SignUpRequest packet.")
                else:
                    print("Client: Username '" + self.username + "' is unavailable.")
            elif isinstance(packet, packets.SignUpResult) and self.state == 1:
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
        packet = packets.CheckUsername()
        packet.username = self.username
        packet_se = packet.__serialize__()
        self.transport.write(packet_se)
        print("Client: Client sends CheckUsername packet.")


class PassThroughLayer1(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(self.transport)

    def data_received(self, data):
        print("Client: Data passes up PassThroughLayer1.")
        self.higherProtocol().data_received(data)

    def connection_lost(self, exc):
        self.transport = None
        self.higherProtocol().connection_lost()


class PassThroughLayer2(StackingProtocol):
    def __init__(self):
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        self.higherProtocol().connection_made(self.transport)

    def data_received(self, data):
        print("Client: Data passes up PassThroughLayer2.")
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
    remote_address = "20174.1.1.1"
    coro = getConnector("passThrough").create_playground_connection(lambda: ClientProtocol("harry", "123456", "harry@gmail.com"),
                                                                    remote_address, 101)
    transport, client = loop.run_until_complete(coro)
    print("Client Connected. Starting UI t:{}. p:{}.".format(transport, client))
    loop.run_forever()
    loop.close()
