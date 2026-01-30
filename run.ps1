# Job Scout AI - 로컬 실행 스크립트 (PowerShell)
# 사용법: .\run.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Job Scout AI - 로컬 실행" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# .env 파일 로드
if (Test-Path ".env") {
    Write-Host "[1/3] 환경변수 로딩 중..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Host "      완료!" -ForegroundColor Green
} else {
    Write-Host "[오류] .env 파일이 없습니다!" -ForegroundColor Red
    Write-Host "       .env.example 파일을 복사해서 .env로 만들고 정보를 입력하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/3] 채용공고 수집 시작..." -ForegroundColor Yellow
Write-Host ""

python src/main.py

Write-Host ""
Write-Host "[3/3] 완료!" -ForegroundColor Green
Write-Host ""
Read-Host "아무 키나 누르면 종료..."
