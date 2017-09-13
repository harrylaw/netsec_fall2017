"""Ruihui "Harry" Luo's assignment 1[b]"""

from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BOOL


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


def basic_unit_test():
    packet1 = CheckUsername()
    packet1.username = "harry"
    packet1_se = packet1.__serialize__()
    packet1_dese = CheckUsername.Deserialize(packet1_se)
    assert packet1 == packet1_dese

    packet2 = UsernameAvailability()
    packet2.username_availability = True
    packet2_se = packet2.__serialize__()
    packet2_dese = UsernameAvailability.Deserialize(packet2_se)
    assert packet2 == packet2_dese

    packet3 = SignUpRequest()
    packet3.username = "harry"
    packet3.password = "123456"
    packet3.email = "harry@gmail.com"
    packet3_se = packet3.__serialize__()
    packet3_dese = SignUpRequest.Deserialize(packet3_se)
    assert packet3 == packet3_dese

    packet4 = SignUpResult()
    packet4.result = True
    packet4.user_id = 1
    packet4_se = packet4.__serialize__()
    packet4_dese = SignUpResult.Deserialize(packet4_se)
    assert packet4 == packet4_dese


if __name__ == "__main__":
    basic_unit_test()
