python -m pip install --upgrade twine cibuildwheel
set CIBW_BEFORE_BUILD='python -m pip install -r requirements.txt'
FOR /F "tokens=* USEBACKQ" %%i IN (`python -c "import sys; print('cp' + ''.join(map(str, sys.version_info[:2])) + '-*')"`) do set "CIBW_BUILD=%%i"
cibuildwheel --output-dir dist