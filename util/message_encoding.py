
def decode_message(parts: list[bytes]) -> list[str]:
    return [part.decode() for part in parts]

def encode_message(parts: list[str]) -> list[bytes]:
    return [part.encode() for part in parts]