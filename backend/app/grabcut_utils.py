# numpy dan OpenCV untuk pemrosesan gambar
import numpy as np
import cv2

# Fungsi untuk membaca dan menyimpan gambar
def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    # Konversi bytes ke array numpy dan baca gambar
    arr = np.frombuffer(image_bytes, np.uint8) # Konversi bytes ke array numpy
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR) # Baca gambar dari array numpy
    if img is None:
        raise ValueError("Tidak dapat membaca gambar.")
    return img

# Fungsi utama untuk menghapus background menggunakan GrabCut
def remove_background_from_bytes(image_bytes: bytes, rect: tuple = None, iter_count: int = 5) -> bytes:
    # Baca gambar dari bytes
    img = read_image_from_bytes(image_bytes) 
    h, w = img.shape[:2] # Dapatkan dimensi gambar

    mask = np.zeros((h, w), np.uint8) # Inisialisasi mask kosong

    # Inisialisasi rectangle jika tidak diberikan
    if rect is None:
        inset = int(min(w, h) * 0.1)
        rect = (inset, inset, w - 2 * inset, h - 2 * inset)

    bgdModel = np.zeros((1, 65), np.float64) # Model background untuk GrabCut
    fgdModel = np.zeros((1, 65), np.float64) # Model foreground untuk GrabCut

    # Jalankan GrabCut
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)

    # Buat mask biner: 1 untuk foreground, 0 untuk background
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # Perbaiki mask dengan operasi morfologi untuk mengurangi noise
    kernel = np.ones((3, 3), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel, iterations=1)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Hapus background
    img_fg = img.copy()
    img_fg[mask2 == 0] = 0  # Set pixel background ke hitam

    # Buat channel alpha dari mask
    alpha = (mask2 * 255).astype("uint8")

    # Gabungkan channel BGR dengan alpha untuk membuat gambar RGBA
    b, g, r = cv2.split(img_fg)
    rgba = cv2.merge([b, g, r, alpha])

    # Encode ke PNG
    is_success, buffer = cv2.imencode(".png", rgba)
    if not is_success:
        raise RuntimeError("Gagal meng-encode gambar PNG.")

    return buffer.tobytes()
