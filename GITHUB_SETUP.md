# Инструкция по загрузке проекта на GitHub

## Шаг 1: Создание репозитория на GitHub

1. Перейдите на https://github.com/new
2. В поле "Repository name" введите: **cb**
3. Выберите **Private** или **Public** (на ваше усмотрение)
4. **НЕ** отмечайте галочки:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
5. Нажмите кнопку **"Create repository"**

## Шаг 2: Загрузка кода

После создания репозитория выполните одну из команд:

### Вариант 1: Через PowerShell скрипт
```powershell
.\push_to_github.ps1
```

### Вариант 2: Вручную через командную строку
```bash
git push -u origin main
```

Если потребуется аутентификация, GitHub может запросить:
- **Username**: ваш GitHub username
- **Password**: используйте Personal Access Token (не пароль!)

## Шаг 3: Создание Personal Access Token (если нужно)

Если GitHub запросит пароль:

1. Перейдите на https://github.com/settings/tokens
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Дайте токену имя (например, "cb-project")
4. Выберите срок действия
5. Отметьте права: **repo** (полный доступ к репозиториям)
6. Нажмите **"Generate token"**
7. Скопируйте токен (он показывается только один раз!)
8. Используйте этот токен вместо пароля при push

## Альтернативный способ: через SSH

Если у вас настроен SSH ключ:

```bash
git remote set-url origin git@github.com:vvryzhov/cb.git
git push -u origin main
```

## Проверка

После успешной загрузки проект будет доступен по адресу:
**https://github.com/vvryzhov/cb**

