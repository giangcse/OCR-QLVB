from fastapi import FastAPI, Request, Depends, HTTPException, Cookie, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha3_256
from pydantic import BaseModel
from .ocr_bangtn import extract_text
from .ocr_bangdiem import find_tables_from_image
from .utils import *

import os
import shutil
import jwt
import datetime
import sqlite3

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
# Create connection
conn = sqlite3.connect('sql.db')
# Secret key for hash
SECRET_KEY = 'BN3298'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 720
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
    if credentials.username == "" or credentials.password == "":
        return False
    else:
        results = conn.execute('''SELECT COUNT(USERNAME) FROM users WHERE USERNAME = ? AND PASSWORD = ?''', (credentials.username, sha3_256(bytes(credentials.password, 'utf-8')).hexdigest(),))
        existed_username = 0
        for i in results:
            existed_username = int(i[0])
        if existed_username != 0:
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

@app.post('/register')
async def register(credentials: UserCredentials):
    if credentials.username == "" or credentials.password == "":
        return JSONResponse(status_code=401, content="username/password/is_admin is empty")
    else:
        results = conn.execute('''SELECT COUNT(USERNAME) FROM users WHERE USERNAME = ?''', (credentials.username, ))
        existed_username = 0
        for i in results:
            existed_username = int(i[0])
        if existed_username == 0:
            create_account = conn.execute('''INSERT INTO users VALUES (?, ?)''', (credentials.username, sha3_256(bytes(credentials.password, 'utf-8')).hexdigest(),))
            conn.commit()
            return JSONResponse(status_code=201, content="Created!")
        else:
            return JSONResponse(status_code=409, content="Username is existed!")

@app.post('/change_password')
async def change_password(request: Request):
    if request.username == "" or request.password == "":
        return JSONResponse(status_code=401, content="username/password is empty")
    else:
        results = conn.execute('''SELECT COUNT(USERNAME) FROM users WHERE USERNAME = ?''', (request.username, ))
        existed_username = 0
        for i in results:
            existed_username = int(i[0])
        if existed_username == 0:
            create_account = conn.execute('''UPDATE users SET PASSWORD = ? WHERE USERNAME = ?''', (sha3_256(bytes(request.password, 'utf-8')).hexdigest(), request.username,))
            conn.commit()
            return JSONResponse(status_code=201, content="Updated!")
        else:
            return JSONResponse(status_code=409, content="Username is existed!")

@app.post('/ocr_bangdiem')
async def ocr_bangdiem(file: UploadFile = File(...), token: str = Cookie(None)):
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
                ocr_result = find_tables_from_image(file_path)
                os.remove(file_path)
                create_log = conn.execute('''INSERT INTO logs VALUES (?, ?, ?, ?)''', ('OCR Bảng điểm', str(ocr_result), username, round(datetime.datetime.now().timestamp()),))
                conn.commit()
                return JSONResponse(status_code=200, content=ocr_result)
        except Exception as e:
            return JSONResponse(status_code=400, content={'status': e})
    else:
        return JSONResponse(status_code=401, content={'status': 'Login first'})
    
@app.post('/ocr_bangtn')
async def ocr_vanban(file: UploadFile = File(...), token: str = Cookie(None)):
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

                result = extract_text(file_path)
                os.remove(file_path)
                create_log = conn.execute('''INSERT INTO logs VALUES (?, ?, ?, ?)''', ('OCR Bằng tốt nghiệp', str(result), username, round(datetime.datetime.now().timestamp()),))
                conn.commit()
                return JSONResponse(status_code=200, content=result)
        except Exception as e:
            return JSONResponse(status_code=400, content={'status': str(e)})
    else:
        return JSONResponse(status_code=401, content={'status': 'Login first'})

