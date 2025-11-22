# Скрипт для загрузки проекта на GitHub
# Убедитесь, что репозиторий 'cb' создан на https://github.com/vvryzhov

Write-Host "Проверка статуса git..." -ForegroundColor Yellow
git status

Write-Host "`nПопытка загрузки на GitHub..." -ForegroundColor Yellow
Write-Host "Если репозиторий еще не создан, выполните следующие шалы:" -ForegroundColor Cyan
Write-Host "1. Перейдите на https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Создайте репозиторий с именем 'cb'" -ForegroundColor Cyan
Write-Host "3. НЕ инициализируйте его (README, .gitignore и т.д.)" -ForegroundColor Cyan
Write-Host "4. Запустите этот скрипт снова" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Репозиторий уже создан? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Загрузка кода..." -ForegroundColor Green
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nУспешно загружено на GitHub!" -ForegroundColor Green
        Write-Host "Репозиторий: https://github.com/vvryzhov/cb" -ForegroundColor Cyan
    } else {
        Write-Host "`nОшибка при загрузке. Проверьте:" -ForegroundColor Red
        Write-Host "- Репозиторий создан на GitHub" -ForegroundColor Red
        Write-Host "- У вас есть права на запись" -ForegroundColor Red
        Write-Host "- Правильно настроена аутентификация GitHub" -ForegroundColor Red
    }
} else {
    Write-Host "Создайте репозиторий на GitHub и запустите скрипт снова." -ForegroundColor Yellow
}

