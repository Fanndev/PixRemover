# app/grabcut_utils.py
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
    Melakukan background removal menggunakan GrabCut + perbaikan smoothing.
    """
    img = read_image_from_bytes(image_bytes)
    h, w = img.shape[:2]

    # Buat mask awal
    mask = np.zeros((h, w), np.uint8)

    # Jika tidak ada bounding box manual, gunakan hampir seluruh gambar
    if rect is None:
        inset = int(min(w, h) * 0.1)  # area tepi 10% sebagai background
        rect = (inset, inset, w - 2 * inset, h - 2 * inset)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # Jalankan GrabCut
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)

    # Konversi mask ke biner (0 = background, 1 = foreground)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # 🔹 Tambahkan smoothing di tepi (Gaussian blur)
    mask2 = cv2.GaussianBlur(mask2.astype("float32"), (5, 5), 0)
    mask2 = (mask2 > 0.5).astype("uint8")

    # 🔹 Hapus noise kecil (morphological open/close)
    kernel = np.ones((3, 3), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel, iterations=1)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Buat alpha channel berdasarkan mask
    alpha = (mask2 * 255).astype("uint8")

    # Terapkan mask ke gambar
    img_fg = img * mask2[:, :, np.newaxis]

    # Ubah ke RGBA (R, G, B, A)
    b, g, r = cv2.split(img_fg)
    rgba = cv2.merge([r, g, b, alpha])

    # Encode hasil ke PNG bytes
    is_success, buffer = cv2.imencode(".png", rgba)
    if not is_success:
        raise RuntimeError("Gagal meng-encode gambar PNG.")

    return buffer.tobytes()
