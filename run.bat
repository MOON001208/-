@echo off
chcp 65001 > nul
echo ========================================
echo   Job Scout AI - 로컬 실행
echo ========================================
echo.

REM .env 파일에서 환경변수 로드
if exist .env (
    echo [1/3] 환경변수 로딩 중...
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    echo       완료!
) else (
    echo [오류] .env 파일이 없습니다!
    echo        .env.example 파일을 복사해서 .env로 만들고 정보를 입력하세요.
    pause
    exit /b 1
)

echo.
echo [2/3] 채용공고 수집 시작...
echo.

python src/main.py

echo.
echo [3/3] 완료!
echo.
pause
