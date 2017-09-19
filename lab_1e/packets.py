"""Ruihui "Harry" Luo's assignment 1[e]"""

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



