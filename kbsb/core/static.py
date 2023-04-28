# copyright Chessdevil Consulting BVBA 2018 - 2020
from fastapi import HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
import os.path
from kbsb.main import app


@app.get("/ratingnl")
def ratingnl():
    fn = os.path.join(os.path.dirname(__file__), "ratingnl.html")
    try:
        with open(fn) as f:
            page = f.read()
        return HTMLResponse(page)
    except Exception:
        raise HTTPException(status_code=401, detail="ratingnl.html not found")


@app.get("/ratingfr")
def ratingfr():
    fn = os.path.join(os.path.dirname(__file__), "ratingfr.html")
    try:
        with open(fn) as f:
            page = f.read()
        return HTMLResponse(page)
    except Exception:
        raise HTTPException(status_code=401, detail="ratingfr.html not found")
