# Telegram-бот заявок — Railway

## Деплой на Railway

1. Распакуйте архив и загрузите содержимое проекта в корень GitHub-репозитория.
2. В Railway выберите **New Project → Deploy from GitHub Repo** и подключите репозиторий.
3. Откройте сервис → **Variables** и добавьте:
   - `BOT_TOKEN` — токен от @BotFather
   - `ADMIN_CHANNEL_ID` — ID чата/канала для заявок
   - `PRIVATE_CHANNEL_ID` — ID закрытого канала
   - `DB_PATH=/data/applications.db`
   - `ADMIN_IDS` — необязательно, ID администраторов через запятую
4. В сервисе Railway откройте **Volumes**, создайте Volume и задайте **Mount Path** `/data`.
   Это сохраняет SQLite-базу между перезапусками и деплоями.
5. Railway возьмёт команду запуска из `railway.json`: `python main.py`.
6. Проверьте **Deployments → Logs**.

## Настройка Telegram

- Добавьте бота в админ-чат/канал и выдайте право отправлять сообщения.
- Добавьте бота в закрытый канал и выдайте право создавать пригласительные ссылки.
- Убедитесь, что `ADMIN_CHANNEL_ID` и `PRIVATE_CHANNEL_ID` указаны как целые числа, обычно с префиксом `-100`.

## Локальный запуск

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

Скопируйте `.env.example` в `.env` и заполните значения. Для локального запуска установите переменные окружения из `.env` любым удобным способом, затем:

```bash
python main.py
```

## Важно

- Настоящий `.env` не загружайте в GitHub. В репозитории хранится только `.env.example`.
- Не указывайте `PORT` и не настраивайте HTTP healthcheck: бот работает через Telegram long polling и не поднимает веб-сервер.
- Без подключённого Volume файл SQLite может потеряться при пересоздании контейнера.
