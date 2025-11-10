import io
import numpy as np
import cv2
from PIL import Image

def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Baca file gambar dari bytes dan ubah ke format OpenCV (BGR)."""
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Tidak dapat membaca gambar.")
    return img

def remove_background_from_bytes(image_bytes: bytes, rect: tuple = None, iter_count: int = 5) -> bytes:
    """
    Melakukan background removal menggunakan GrabCut
    dengan menjaga warna asli (tanpa perubahan kontras/saturasi).
    """
    img = read_image_from_bytes(image_bytes)
    h, w = img.shape[:2]

    mask = np.zeros((h, w), np.uint8)

    if rect is None:
        inset = int(min(w, h) * 0.1)
        rect = (inset, inset, w - 2 * inset, h - 2 * inset)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)

    # Biner mask
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # Bersihkan tepi & noise
    kernel = np.ones((3, 3), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel, iterations=1)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Gunakan mask langsung tanpa GaussianBlur agar warna tidak bocor
    img_fg = img.copy()
    img_fg[mask2 == 0] = 0  # hilangkan background

    # Buat alpha channel dari mask
    alpha = (mask2 * 255).astype("uint8")

    # ⚡ Fix urutan warna — OpenCV BGR, bukan RGB
    b, g, r = cv2.split(img_fg)
    rgba = cv2.merge([b, g, r, alpha])

    # Encode ke PNG
    is_success, buffer = cv2.imencode(".png", rgba)
    if not is_success:
        raise RuntimeError("Gagal meng-encode gambar PNG.")

    return buffer.tobytes()
