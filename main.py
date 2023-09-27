from fastapi import FastAPI, Request, Depends, HTTPException, Cookie, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha3_256
from pydantic import BaseModel
from decouple import config

import deepdoctection as dd
import os
import shutil
import jwt
import datetime

# Create an API app
app = FastAPI(
    title="API OCR dạng bảng tiếng Việt",
    description="API cho phép upload file ảnh (*.jpg, *.png) hoặc pdf dạng bảng để OCR và trả về kết quả dạng bảng",
    version="0.0.1"
)
# App middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
# Mount to disk

# Secret key for hash
SECRET_KEY = 'BN3298'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 720
USERNAME = 'giangpt'
PASSWORD = 'ThanhGiang2808@@'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Model UserCredentials
class UserCredentials(BaseModel):
    username: str
    password: str

# Model Token
class Token(BaseModel):
    access_token: str
    token_type: str

def verify_user_route(credentials: UserCredentials):
    if credentials.username == USERNAME and credentials.password == PASSWORD:
        return True
    else:
        return False

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

# Middleware để bắt lỗi 404 và xử lý
@app.middleware("http")
async def catch_404(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        return JSONResponse(content={"ERROR": "Not found"}, status_code=404)
    return response

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login", response_model=Token)
async def login_for_access_token(credentials: UserCredentials):
    if verify_user_route(credentials):
        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": credentials.username}, expires_delta=access_token_expires)
        response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
        response.set_cookie("token", access_token, httponly=False)
        response.set_cookie("username", credentials.username, httponly=False)
        return response
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.get('/')
async def home(request: Request, token: str = Cookie(None)):
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                return JSONResponse(content={'status': 'You are connected'})
        except jwt.PyJWTError:
            pass
    return RedirectResponse('/login')

@app.get('/login')
async def login(request: Request, token: str = Cookie(None)):
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                return RedirectResponse(url='/')
        except jwt.PyJWTError:
            pass
    else:
        return JSONResponse(status_code=401, content={'status': 'Must login'})

@app.post('/ocr')
async def ocr(file: UploadFile = File(...), token: str = Cookie(None)):
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                uploaded_folder = os.path.join(os.getcwd(), 'uploaded', username)
                os.makedirs(uploaded_folder, exist_ok=True)
                
                file_path = os.path.join(uploaded_folder, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                analyzer = dd.get_dd_analyzer(config_overwrite=["LANGUAGE='Vietnamese'"])

                df = analyzer.analyze(path=uploaded_folder)
                df.reset_state()  # This method must be called just before starting the iteration. It is part of the API.

                doc=iter(df)
                page = next(doc)
                table = page.tables[0]
                table.get_attribute_names()
                csv_table = []
                for i in table.csv:
                    i = [item.replace('|', ' ').strip() for item in i]
                    csv_table.append(i)
                os.remove(file_path)
                return JSONResponse(status_code=200, content=csv_table)
        except Exception as e:
            return JSONResponse(status_code=400, content={'status': 'BADDDD REQUEST'})
    else:
        return JSONResponse(status_code=401, content={'status': 'Login first'})

