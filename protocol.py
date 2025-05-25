"""
    Bar Assulin ~ 25/5/2025
    protocol - for text, byts and objects
"""


import pickle

END_SIGN = b"#"
FLAG_TEXT = b"T"
FLAG_PICKLE = b"P"


def send_protocol(message, sock):
    """
    Send an object or string over `sock` with length-prefix framing and a 1-byte flag:
      - b'T' for UTF-8 text
      - b'P' for pickled Python objects
    Format on the wire:
      <FLAG><length><END_SIGN><payload bytes>
    """
    # Determine payload bytes and flag
    try:
        if isinstance(message, (bytes, bytearray)):
            flag = FLAG_TEXT
            payload = bytes(message)
        elif isinstance(message, str):
            flag = FLAG_TEXT
            payload = message.encode("utf-8")
        else:
            flag = FLAG_PICKLE
            payload = pickle.dumps(message)

        # Build header: length of payload as ASCII
        length_str = str(len(payload)).encode("ascii")
        packet = flag + length_str + END_SIGN + payload

        try:
            sock.sendall(packet)
            return True
        except Exception as e:
            print(f"[send_protocol] send error: {e!r}")
            return False
    except Exception as err:
        print(err)


def recv_protocol(sock):
    """
    Receive one framed message from `sock`:
      1) Read 1 byte for the flag
      2) Read until END_SIGN to get the ASCII length
      3) Read exactly that many payload bytes
      4) Decode or unpickle based on the flag
    Returns: str or Python object
    """
    try:
        # 1) flag
        flag = sock.recv(1)
        if not flag:
            raise ConnectionError("Socket closed while reading flag")

        # 2) length prefix
        length_bytes = bytearray()
        while True:
            b = sock.recv(1)
            if not b:
                raise ConnectionError("Socket closed while reading length")
            if b == END_SIGN:
                break
            length_bytes.extend(b)
        length = int(length_bytes.decode("ascii"))

        # 3) payload
        payload = bytearray()
        while len(payload) < length:
            chunk = sock.recv(length - len(payload))
            if not chunk:
                raise ConnectionError("Socket closed during payload recv")
            payload.extend(chunk)

        # 4) interpret
        if flag == FLAG_TEXT:
            return payload.decode("utf-8")
        elif flag == FLAG_PICKLE:
            return pickle.loads(bytes(payload))
        else:
            raise ValueError(f"Unknown flag byte: {flag!r}")
    except Exception as err:
        print(err)
