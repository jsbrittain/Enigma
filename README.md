# Enigma machine

Python implementation of the Enigma cryptographic machine used by Germany in WWII.

This repository is available for general interest, but was constructed as a hobby
project / learning experience so will
not be actively maintained. The implementation consists of a three-rotator setup with
reflector and plugboard, but
can be easily extended (or constrained) to model other systems. The default settings are
described at the top of the `enigma.py` file, being taken from the *German
Railway (Rocket)* specification listed on [Wikipedia](https://en.wikipedia.org/wiki/Enigma_rotor_details).
The default settings also include an arbitrary set of plugboard steckers.


## Quickstart

Usage from the command line (using the default setup):
```
python enigma.py "Message to be encrypted"
```
will produce `TVBWJ XPZYE MGQKX JSSYK`.

Likewise, entering the encrypted message will recover the original:
```
python enigma.py "TVBWJ XPZYE MGQKX JSSYK"
```
produces `MESSA GETOB EENCR YPTED` (formatting removed and grouped in 5-character blocks).

Like the original, non-alphabetic characters are not supported, so numbers must be spelled out.

## Resources

If you are interested in learning more about the Enigma machine, here are some excellent
resources that helped during this project:
- [A superb video explanation](https://www.youtube.com/watch?v=ybkkiGtJmkM)
- [Wikipedia](https://en.wikipedia.org/wiki/Enigma_machine)
- I also highly recommend a visit to [Bletchley Park](https://bletchleypark.org.uk/), UK, if able.

Some more assorted resources, including information on the Bombe and Checking Machine's
used to decrypt enigma messages:
- [Bombe Simulation Tutorial](https://www.lysator.liu.se/%7Ekoma/turingbombe/TuringBombeTutorial.pdf)

## Options

Command line arguments allow you to adjust various settings. It is also encouraged to
explore the python scripts to make more substantial changes.
| Argument | Description |
| -------- | ----------- |
| `-k x y z` <br> `--key x y z` | Rotator settings, 3-digits [each 0-25] separated by spaces, e.g. `-k 0 1 2`. Note that these are the *starting* settings, since the rotators increment upon keypress. |
| `--r1e ENCODING` <br> `--r2e ENCODING` <br> `--r3e ENCODING` | Specifies the rotator 1, 2 or 3 encoding, e.g. `--r1e ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `--r1n NOTCH` <br> `--r2n NOTCH` <br> `--r3e NOTCH` | Specifies the rotator 1, 2 or 3 notch position, e.g. `--r1n K` |
| `--ref ENCODING` | Specifies the reflector encoding, e.g. `--ref ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `--plug ENCODING` | Specifies the plugboard encoding, e.g. switching `DC`, `EF` and `GH`: `--ref ABDCFEHGIJKLMNOPQRSTUVWXYZ` |
| `-v` <br> `--verbose` | Verbose mode displays parsed/formatted input with encoded and decoded messages |
| `-vv` <br> `--veryverbose` | Very verbose mode additionally displays all Enigma machine settings |

The code comes with a modest test-suite to ensure that any modifications to the code
maintain functionality.

## From within Python

```python
import enigma as Enigma

key = [0, 1, 2]
message = "Hello World"

e = Enigma.Enigma()  # When run without options this will generate random encodings
msg_encoded = e.encode(message, key)  # Encode
print(msg_encoded)

msg_decoded = e.encode(msg_encoded.message, key)  # Decode
print(msg_decoded)

```
