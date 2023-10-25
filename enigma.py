import math
import random
import argparse
from typing import List

# Rotor wirings from https://en.wikipedia.org/wiki/Enigma_rotor_details

# German Railway (Rocket)
# (Notch positions have been made up arbitrarily)
rotor_I = "JGDQOXUSCAMIFRVTPNEWKBLZYH", "Q"
rotor_II = "NTZPSFBOKMWRCJDIVLAEYUXHGQ", "E"
rotor_III = "JVIUBHTCDYAKEQZPOSGXNRMWFL", "V"
UKW = "QYHOGNECVPUZTFDJAXWMKISRBL"  # reflector
ETW = "QWERTZUIOASDFGHJKPYXCVBNML"  # input / keyboard layout? (unused)
plugboard = "AMCDSFGHIJTQBNRYLOEKUVZXPW"  # (arbitrary) plugboard settings


class Enigma:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    block_len = 5
    ordA = ord('A')

    class Mapper:
        def __init__(self) -> None:
            self.mapping = list(range(len(Enigma.alphabet)))

        def forward(self, number: int, offset: int = 0) -> int:
            return self.mapping[Enigma.increment(number, offset)]

        def backward(self, number: int, offset: int = 0) -> int:
            return Enigma.increment(self.mapping.index(number), -offset)

        def __str__(self) -> str:
            return ''.join(chr(x + Enigma.ordA) for x in self.mapping)

        def load_encoding(self, encoding: str) -> None:
            self.mapping = [ord(c) - Enigma.ordA for c in encoding]

    class Rotator(Mapper):
        def __init__(self, encoding="", notch="") -> None:
            super().__init__()
            if encoding:  # use the given encoding
                self.load_encoding(encoding)
            else:  # generate a random encoding
                random.shuffle(self.mapping)
            if notch:
                self.notch = notch
            else:
                self.notch = random.choice(list(Enigma.alphabet))

    class Reflector(Mapper):
        def __init__(self, encoding="") -> None:
            super().__init__()
            # Mapping must be symmetric to enable encoding and decoding
            if encoding:  # use the given encoding
                self.load_encoding(encoding)
            else:
                # Simple reversal pattern
                self.mapping = list(range(25, -1, -1))
                # Generate a random encoding
                letters = list(Enigma.alphabet)
                random.shuffle(letters)
                while len(letters) > 0:
                    i_from = ord(letters[0]) - Enigma.ordA
                    i_to = ord(letters[1]) - Enigma.ordA
                    self.mapping[i_from] = i_to
                    self.mapping[i_to] = i_from
                    letters = letters[2:]

    class Plugboard(Mapper):
        def __init__(self, encoding="") -> None:
            # Plugboard maps some letter to a different letter
            #  (but not all letters are mapped; 7-9 pairs)
            super().__init__()
            if encoding:
                self.mapping = [ord(c) - Enigma.ordA for c in encoding]
            else:
                # Generate a random encoding
                letters = list(Enigma.alphabet)
                random.shuffle(letters)
                for _ in range(0, random.randint(7, 9)):
                    i_from = ord(letters[0]) - Enigma.ordA
                    i_to = ord(letters[1]) - Enigma.ordA
                    self.mapping[i_from] = i_to
                    self.mapping[i_to] = i_from
                    letters = letters[2:]

    class Message():
        """"Message class used to store and format printing of encoded messages"""
        def __init__(self, message: str) -> None:
            self.message = message

        def __str__(self) -> str:
            return ' '.join(
                   [self.message[i:i + Enigma.block_len]
                    for i in range(0, len(self.message), Enigma.block_len)])

        def __repr__(self):
            return self.__str__()

    @classmethod
    def increment(cls, value: int, increment: int = 1) -> int:
        return (value + increment) % len(Enigma.alphabet)

    def __init__(
        self,
        rotator1_encoding=("", ""),
        rotator2_encoding=("", ""),
        rotator3_encoding=("", ""),
        reflector_encoding: str = "",
        plugboard_encoding: str = "",
        key=[0, 0, 0],
    ) -> None:
        self.key = key.copy()
        self.rotator1 = Enigma.Rotator(*rotator1_encoding)
        self.rotator2 = Enigma.Rotator(*rotator2_encoding)
        self.rotator3 = Enigma.Rotator(*rotator3_encoding)
        self.reflector = Enigma.Reflector(reflector_encoding)
        self.plugboard = Enigma.Plugboard(plugboard_encoding)

    def parse_message(self, message: str) -> str:
        msgs: List[str] = []
        for i in range(len(message)):
            letter = message[i].upper().strip()
            if not letter or letter not in self.alphabet:
                continue
            msgs.append(letter)
        msg = ''.join(msgs)
        # Pad message to block length
        msg = msg.ljust(math.ceil(len(msg) / Enigma.block_len) * Enigma.block_len, 'X')
        return msg

    def translate(self, letter: str) -> str:
        letter = letter.upper().strip()
        number = ord(letter) - Enigma.ordA  # Letter to numeric
        number = self.plugboard.forward(number)
        number = self.rotator1.forward(number, self.key[0])
        number = self.rotator2.forward(number, self.key[1])
        number = self.rotator3.forward(number, self.key[2])
        number = self.reflector.forward(number)
        number = self.rotator3.backward(number, self.key[2])
        number = self.rotator2.backward(number, self.key[1])
        number = self.rotator1.backward(number, self.key[0])
        number = self.plugboard.backward(number)
        self.key_increment()
        return chr(number + Enigma.ordA)  # Numeric to letter

    def set_key(self, key: List[int]) -> None:
        self.key = key

    def key_increment(self) -> None:
        # If the first rotator key is at the second rotator notch, then increment the
        # second rotator (happens at the same time as the first rotator increment)
        if chr(self.key[0] + Enigma.ordA) == self.rotator2.notch:
            # If the second rotator is at the third rotator notch, then also increment
            # the third rotator
            if chr(self.key[1] + Enigma.ordA) == self.rotator3.notch:
                self.key[2] = Enigma.increment(self.key[2])
            self.key[1] = Enigma.increment(self.key[1])
        # Always increment the first rotator
        self.key[0] = Enigma.increment(self.key[0])

    def encode(self, message, starting_key) -> Message:
        if starting_key:
            self.key = starting_key.copy()
        message = self.parse_message(message)
        msg = []
        for i in range(0, len(message)):
            msg.append(self.translate(message[i]))
        return Enigma.Message(''.join(msg))


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Enigma encoder/decoder')
    parser.add_argument('message', nargs='?', type=str, default="Hello World",
                        help='message to encode')
    parser.add_argument('-k', '--key', nargs=3, type=int, default=[0, 0, 0],
                        help='starting key (3 digits [0-25])')
    parser.add_argument('--r1e', type=str, default=rotor_I[0],
                        help='rotator 1 encoding')
    parser.add_argument('--r1n', type=str, default=rotor_I[1],
                        help='rotator 1 notch')
    parser.add_argument('--r2e', type=str, default=rotor_II[0],
                        help='rotator 2 encoding')
    parser.add_argument('--r2n', type=str, default=rotor_II[1],
                        help='rotator 2 notch')
    parser.add_argument('--r3e', type=str, default=rotor_III[0],
                        help='rotator 3 encoding')
    parser.add_argument('--r3n', type=str, default=rotor_III[1],
                        help='rotator 3 notch')
    parser.add_argument('--ref', type=str, default=UKW,
                        help='reflector encoding')
    parser.add_argument('--plug', type=str, default=plugboard,
                        help='plugboard encoding')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')
    parser.add_argument('-vv', '--veryverbose', action='store_true',
                        help='very verbose output')
    args = parser.parse_args()

    # Create Enigma machine
    e = Enigma(
        rotator1_encoding=(args.r1e, args.r1n),
        rotator2_encoding=(args.r2e, args.r2n),
        rotator3_encoding=(args.r3e, args.r3n),
        reflector_encoding=args.ref,
        plugboard_encoding=args.plug,
    )
    if args.veryverbose:
        print("Rotator 1: " + str(e.rotator1))
        print("Rotator 2: " + str(e.rotator2))
        print("Rotator 3: " + str(e.rotator3))
        print("Reflector: " + str(e.reflector))
        print("Plugboard: " + str(e.plugboard))
        print("Key: " + str(args.key))
    msg_parsed = e.parse_message(args.message)
    if args.verbose or args.veryverbose:
        print("Parsed message: " + msg_parsed)
    msg_enc = e.encode(args.message, args.key)
    if args.verbose or args.veryverbose:
        print(f"Encoded message: {msg_enc}")
    # Decode message again as a sanity check
    msg_dec = e.encode(msg_enc.message, args.key)
    if args.verbose or args.veryverbose:
        print(f"Decoded message: {msg_dec}")
    if msg_parsed == msg_dec.message:
        print(msg_enc)
    else:
        print("FAILURE: Decoded message does not match original message!")
        print("         Please check your settings (e.g. this can be due to a "
              "non-symmetric reflector).")
