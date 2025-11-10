from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from .grabcut_utils import remove_background_from_bytes

app = FastAPI(title="ClearCut - Background Removal API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Main endpoint for background removal
@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    x: int | None = Query(None),
    y: int | None = Query(None),
    w: int | None = Query(None),
    h: int | None = Query(None),
    iter_count: int = Query(5, ge=1, le=50),
):
    """Endpoint utama background removal."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus berupa gambar.")

    # Baca gambar
    image_bytes = await file.read()
    rect = None
    if None not in (x, y, w, h):
        rect = (x, y, w, h)

    # fungsi untuk menghapus background
    try:
        png_bytes = remove_background_from_bytes(image_bytes, rect=rect, iter_count=iter_count)
        return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))