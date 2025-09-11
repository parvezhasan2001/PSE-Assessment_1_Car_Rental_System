# utils/qrcode_utils.py
import os, re, qrcode, qrcode_terminal

def _safe(name: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', name)

def print_qr_ascii(token: str, outdir: str = "qrcodes", filename: str | None = None, show_ascii: bool = True) -> str:
    """
    Save a QR PNG and (optionally) print ASCII in terminal.
    """
    os.makedirs(outdir, exist_ok=True)
    filename = filename or _safe(f"{token}.png")
    path = os.path.join(outdir, filename)
    qrcode.make(token).save(path)     # PNG generation
    if show_ascii:
        qrcode_terminal.draw(token)   # ASCII in one call
    return path
