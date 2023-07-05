from pathlib import Path

from fastapi import FastAPI, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware

from bs4.dammit import UnicodeDammit

from engine.database import Database
from engine.concardancer import concardancer
from misc.data_models import WordForm, LetterRange
from misc.util import get_temp_file_path, get_plain_text


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"response": "I <3 Yandex"}


@app.get("/api/db_names")
def db_names():
    return Database().get_collections()


@app.post("/api/token")
def api_token(token: str = Body(embed=True), db_name: str = Body(embed=True)):
    return Database().search_by_token(token, db_name)


@app.post("/api/lemma")
def api_lemma(lemma: str = Body(embed=True), db_name: str = Body(embed=True)):
    return Database().search_by_lemma(lemma, db_name)


@app.post("/api/form")
def api_form(form: WordForm, letter_range: LetterRange, db_name: str = Body(embed=True)):
    return Database().search_by_word_form(form, letter_range, db_name)


@app.post("/add/files")
def add_files(files: list[UploadFile], db_name: str = Body(embed=True)):
    with open(text_file_path := get_temp_file_path("txt"), "a", encoding="utf-8") as text_file:
        for file in files:
            suffix = Path(file.filename).suffix
            if suffix in (".docx", ".odt", ".pdf", ".epub", ".xslx", ".htm", ".html"):
                with open(temp_file_path := get_temp_file_path(suffix), "wb") as temp_file:
                    temp_file.write(file.file.read())
            else:
                with open(temp_file_path := get_temp_file_path(suffix), "w", encoding="utf-8") as temp_file:
                    temp_file.write(UnicodeDammit(file.file.read(), ["cp1251", "utf-8"]).unicode_markup)

            text_file.write(get_plain_text(temp_file_path))

    Database().new_collection(db_name, concardancer.get_forms(text_file_path))

    return {"success": True}


@app.post("/add/text")
def add_text(text: str = Body(embed=True), db_name: str = Body(embed=True)):
    with open(text_file_path := get_temp_file_path("txt"), "w", encoding="utf-8") as text_file:
        text_file.write(text)

    Database().new_collection(db_name, concardancer.get_forms(text_file_path))

    return {"success": True}
