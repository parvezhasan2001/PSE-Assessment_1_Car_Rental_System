# utils/qrcode_utils.py
import os
import re
import qrcode

def _sanitize_filename(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', s)

def make_qr_png(data: str, outdir: str = "qrcodes", filename: str | None = None) -> str:
    os.makedirs(outdir, exist_ok=True)
    if filename is None:
        filename = _sanitize_filename(f"{data}.png")
    path = os.path.join(outdir, filename)
    img = qrcode.make(data)
    img.save(path)
    return path

def print_qr_ascii(data: str) -> None:
    """Pure-Python ASCII QR (no extra deps)."""
    qr = qrcode.QRCode(border=1)
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    black = "██"
    white = "  "
    for row in matrix:
        print("".join(black if cell else white for cell in row))
