# # copyright Ruben Decrop 2012 - 2015
# # copyright Chessdevil Consulting BVBA 2015 - 2021

# import logging
# import os, os.path
# from pathlib import Path
# from csv import DictReader
# from fastapi import HTTPException, BackgroundTasks
# from reddevil.core import RdException
# from kbsb.main import app

# # from kbsb.core.site import fetchI18n

# log = logging.getLogger("kbsb")


# # @app.post("/api/site/fetchi18n", response_model=str)
# # async def api_fetchMarkdownFiles():
# #     try:
# #         return await fetchI18n()
# #     except RdException as e:
# #         raise HTTPException(status_code=e.status_code, detail=e.description)
# #     except:
# #         log.exception("failed api call generate_site")
# #         raise HTTPException(status_code=500)

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# cwd = Path(ROOT_DIR)


# def get_translation(key: str, lang: str) -> str:
#     tr = getattr(get_translation, "_tr", None)
#     if tr is None:
#         tr = {}
#         with open(cwd / "data" / "translations - kbsb.csv") as f:
#             reader = DictReader(f)
#             for row in reader:
#                 tr[row["key"]] = {
#                     "nl": row["nl"],
#                     "en": row["en"],
#                     "fr": row["fr"],
#                     "de": row["de"],
#                 }
#             setattr(get_translation, "_tr", tr)
#     return tr.get(key, {}).get(lang, " *** ")


# @app.get("/api/translate", response_model=str)
# def api_translate():
#     try:
#         return get_translation("Back", "nl")
#     except RdException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.description)
#     except:
#         log.exception("failed api call generate_site")
#         raise HTTPException(status_code=500)
