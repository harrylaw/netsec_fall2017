import packets
from playground.network.devices.vnic.connect import getConnector
from asyncio import get_event_loop
from playground.network.packet import PacketType
from asyncio import Protocol


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
                    print("Client: Username '" + self.username + "' is available")
                    new_packet = packets.SignUpRequest()
                    new_packet.username = self.username
                    new_packet.password = self.password
                    new_packet.email = self.email
                    new_packet_se = new_packet.__serialize__()
                    self.state += 1
                    self.transport.write(new_packet_se)
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
            else:
                print("Server: Wrong packet received on server side.")
                break

    def connection_lost(self, exc):
        self.transport = None

    def check_username_availability_in_database(self, username):  # mock database query method
        return True

    def sign_up_to_database(self, username, password, email):  # mock database query method
        return [True, 1]


if __name__ == "__main__":
    loop = get_event_loop()
    loop.set_debug(enabled=True)

    remoteAddress = "20174.1.1.1"
    coro = getConnector().create_playground_connection(lambda: ClientProtocol("harry", "123456", "harry@gmail.com"),
                                                       remoteAddress, 101)
    transport, client = loop.run_until_complete(coro)
    print("Client Connected. Starting UI t:{}. p:{}".format(transport, client))
    loop.run_forever()
    loop.close()
