import pytest
import enigma as Enigma


@pytest.fixture()
def enigma() -> Enigma.Enigma:
    # Startup code
    rotor_I = "JGDQOXUSCAMIFRVTPNEWKBLZYH", "Q"
    rotor_II = "NTZPSFBOKMWRCJDIVLAEYUXHGQ", "E"
    rotor_III = "JVIUBHTCDYAKEQZPOSGXNRMWFL", "V"
    UKW = "QYHOGNECVPUZTFDJAXWMKISRBL"
    plugboard = "AMCDSFGHIJTQBNRYLOEKUVZXPW"
    # Create and yield the Enigma machine
    yield Enigma.Enigma(
        rotator1_encoding=rotor_I,
        rotator2_encoding=rotor_II,
        rotator3_encoding=rotor_III,
        reflector_encoding=UKW,
        plugboard_encoding=plugboard,
    )
    # Teardown code here


def test_Mapper_forward_noencoding(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    for i in range(26):
        assert m.forward(i) == i


def test_Mapper_forward_encoding(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    letters = "QWERTYUIOPASDFGHJKLZXCVBNM"
    m.mapping = list(map(lambda x: ord(x) - ord('A'), list(letters)))
    for i in range(26):
        assert m.forward(i, offset=0) == ord(letters[i]) - ord('A')
        assert m.forward(0, offset=i) == ord(letters[i]) - ord('A')


def test_Mapper_backward_noencoding(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    for i in range(26):
        assert m.backward(i) == i


def test_Mapper_backward_encoding(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    letters = "QWERTYUIOPASDFGHJKLZXCVBNM"
    m.mapping = list(map(lambda x: ord(x) - ord('A'), list(letters)))
    for i in range(26):
        value = ord(letters[i]) - ord('A')
        assert m.backward(value, offset=0) == i


def test_Mapper_str(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    letters = "QWERTYUIOPASDFGHJKLZXCVBNM"
    m.mapping = list(map(lambda x: ord(x) - ord('A'), list(letters)))
    assert str(m) == letters


def test_Mapper_load_encoding(enigma: Enigma.Enigma):
    m = enigma.Mapper()
    for letters in ["QWERTYUIOPASDFGHJKLZXCVBNM",
                    "JGDQOXUSCAMIFRVTPNEWKBLZYH",
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
        m.load_encoding(letters)
        for i in range(26):
            assert m.forward(i, offset=0) == ord(letters[i]) - ord('A')
            assert m.backward(ord(letters[i]) - ord('A'), offset=0) == i


def test_Rotator(enigma: Enigma.Enigma):
    # Functionality tested in Mapper; check instantiation
    rotator = enigma.Rotator("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "A")
    assert rotator.mapping == list(range(26))
    assert rotator.notch == 'A'


def test_Reflector(enigma: Enigma.Enigma):
    # Functionality tested in Mapper; check instantiation
    reflector = enigma.Reflector("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert reflector.mapping == list(range(26))


def test_Plugboard(enigma: Enigma.Enigma):
    # Functionality tested in Mapper; check instantiation
    plugboard = enigma.Plugboard("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert plugboard.mapping == list(range(26))


def test_Message_str(enigma: Enigma.Enigma):
    enigma.block_len = 5
    msg = enigma.Message("AFAIRLYLONGMESSAGE")
    assert str(msg) == "AFAIR LYLON GMESS AGE"


def test_Message_repr(enigma: Enigma.Enigma):
    enigma.block_len = 5
    msg = enigma.Message("AFAIRLYLONGMESSAGE")
    assert repr(msg) == "AFAIR LYLON GMESS AGE"


def test_Enigma_increment(enigma: Enigma.Enigma):
    for i in range(52):
        assert enigma.increment(i) == (i + 1) % 26


def test_Enigma_parse_message(enigma: Enigma.Enigma):
    enigma.block_len = 5
    msg = "Hello World A!!!"
    msg_parsed = enigma.parse_message(msg)
    assert msg_parsed == "HELLOWORLDAXXXX"  # Pads to block_len


def test_Enigma_translate(enigma: Enigma.Enigma):
    key = [0, 0, 0]
    enigma.set_key(key)
    assert enigma.translate('H') == 'C'
    assert enigma.translate('E') == 'V'
    assert enigma.translate('L') == 'P'
    assert enigma.translate('L') == 'K'  # duplicate input; different output
    assert enigma.translate('O') == 'W'
    assert enigma.translate('W') == 'K'  # ignore non-alphabetic characters
    assert enigma.translate('O') == 'K'
    assert enigma.translate('R') == 'U'
    assert enigma.translate('L') == 'Z'
    assert enigma.translate('D') == 'N'


def test_Enigma_set_key(enigma: Enigma.Enigma):
    key = [0, 0, 0]
    enigma.set_key(key)
    assert enigma.key == key
    key = [1, 2, 3]
    enigma.set_key(key)
    assert enigma.key == key


def test_Enigma_key_increment(enigma: Enigma.Enigma):
    key = [0, 0, 0]
    enigma.rotator2.notch = 'K'  # K=11
    enigma.rotator3.notch = 'B'
    enigma.set_key(key)
    assert enigma.key == key
    # Increment first rotator to second rotator notch
    for i in range(1, 11):
        enigma.key_increment()
        assert enigma.key == [i, 0, 0]
    # Second notch incremented for remainder of rotator 1 loop
    for i in range(11, 26):
        enigma.key_increment()
        assert enigma.key == [i, 1, 0]
    # Increment the first rotator to the second (and third) rotator notches
    for i in range(0, 11):
        enigma.key_increment()
        assert enigma.key == [i, 1, 0]
    # Second and third rotators increment
    for i in range(11, 26):
        enigma.key_increment()
        assert enigma.key == [i, 2, 1]


def test_Enigma_encode(enigma: Enigma.Enigma):
    key = [0, 0, 0]
    msg = enigma.encode("Hello World", key)
    assert msg.message == ("CVPKW KKUZN").replace(" ", "")


def test_Enigma_decode(enigma: Enigma.Enigma):
    key = [0, 0, 0]
    msg = enigma.encode("CVPKWKKUZN", key)
    assert msg.message == ("HELLO WORLD").replace(" ", "")


def test_e2e(enigma: Enigma.Enigma):
    key = [1, 2, 3]
    msg = "Testing a reasonably long message so that at least the first rotator " \
          "will rotate which requires a message of at least twenty six characters"
    msg_parsed = enigma.parse_message(msg)
    msg_enc = enigma.encode(msg, key)
    # Ensure that the encoded message is not the same as the original message
    assert msg_parsed != msg_enc.message
    # Ensure that no letter is encoded to itself (not possible with Enigma)
    assert not any(map(lambda x: x[0] == x[1],
                       (list(msg_parsed), list(msg_enc.message))))
    msg_dec = enigma.encode(msg_enc.message, key)
    # Ensure that the decoded message is the same as the original message
    assert msg_parsed == msg_dec.message
