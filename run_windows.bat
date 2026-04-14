@echo off
setlocal

set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set http_proxy=
set https_proxy=
set all_proxy=

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip --isolated install --upgrade pip
python -m pip --isolated install -r requirements.txt
python main.py
