# Yandex Tracker CLI

Консольный клиент для [Яндекс Трекер](https://tracker.yandex.ru/) — работа с очередями, задачами, комментариями, спринтами и чек-листами через API.

## Требования

- **bash** (с поддержкой `BASH_REMATCH`)
- **curl**
- **jq**

## Установка

0. Простейший способ:
   попросить openclaw бота установить yandex-tracker-cli скилл
   или дать ссылку https://clawhub.ai/bkamuz/yandex-tracker-cli

или

1. Скачайте скрипт и сделайте его исполняемым:

   ```bash
   chmod +x yandex-tracker.sh
   ```

2. При желании переименуйте или создайте симлинк для удобства:

   ```bash
   ln -s yandex-tracker.sh yandex-tracker
   ```

## Настройка

Нужны **OAuth-токен** и **Org ID** (идентификатор организации).

- **TOKEN** — получить в Трекере: Настройки → Приложения → OAuth.
- **ORG_ID** — можно посмотреть в DevTools браузера (вкладка Network) в заголовке `X-Org-Id`.

Задать можно двумя способами (приоритет у переменных окружения):

1. **Переменные окружения:**

   ```bash
   export TOKEN="y0_..."
   export ORG_ID="1234567"
   ```

2. **Файл конфигурации** `~/.yandex-tracker-env` (используется, если `TOKEN` и `ORG_ID` не заданы в окружении):

   ```
   TOKEN=y0_...
   ORG_ID=1234567
   ```

   Из файла читаются только строки `TOKEN=...` и `ORG_ID=...` (без выполнения кода).

## Использование

```text
./yandex-tracker.sh <команда> [аргументы]
```

### Очереди

| Команда | Описание |
|--------|----------|
| `queues` | Список очередей |
| `queue-get <key>` | Информация об очереди |
| `queue-fields <key>` | Поля очереди |

### Задачи (issues)

| Команда | Описание |
|--------|----------|
| `issue-get <id>` | Получить задачу |
| `issue-create <queue> <summary>` | Создать задачу (доп. JSON через stdin) |
| `issue-update <id>` | Обновить задачу (JSON через stdin) |
| `issue-delete <id>` | Удалить задачу |
| `issue-transitions <id>` | Доступные переходы по статусам |
| `issue-close <id> <resolution>` | Закрыть задачу с резолюцией |
| `issue-worklog <id> <duration> [comment]` | Добавить учёт времени |
| `issues-search` | Поиск по YQL (JSON с `query`, `limit` через stdin) |

### Комментарии

| Команда | Описание |
|--------|----------|
| `issue-comment <id> <text>` | Добавить комментарий |
| `issue-comment-edit <id> <comment-id> <new-text>` | Редактировать комментарий |
| `issue-comment-delete <id> <comment-id>` | Удалить комментарий |

### Вложения

| Команда | Описание |
|--------|----------|
| `issue-attachments <id>` | Список вложений задачи |
| `attachment-download <issue-id> <fileId> [output]` | Скачать вложение |
| `attachment-upload <issue-id> <filepath> [comment]` | Загрузить файл в задачу |

Пути для скачивания и загрузки вложений ограничены текущей директорией (или `YANDEX_TRACKER_ATTACHMENTS_DIR`); подробнее см. SKILL.md (раздел Security) и опцию отключения проверки.

### Проекты и спринты

| Команда | Описание |
|--------|----------|
| `projects-list` | Список проектов |
| `project-get <id>` | Информация о проекте |
| `project-issues <id>` | Задачи проекта |
| `sprints-list` | Список спринтов |
| `sprint-get <id>` | Информация о спринте |
| `sprint-issues <id>` | Задачи спринта |

### Справочники

| Команда | Описание |
|--------|----------|
| `users-list` | Пользователи |
| `statuses-list` | Статусы |
| `resolutions-list` | Резолюции |
| `issue-types-list` | Типы задач |

### Чек-лист (API v3)

| Команда | Описание |
|--------|----------|
| `issue-checklist <id>` | Элементы чек-листа |
| `checklist-add <issue-id> <text>` | Добавить пункт |
| `checklist-complete <issue-id> <item-id>` | Отметить выполненным |
| `checklist-delete <issue-id> <item-id>` | Удалить пункт |

## Примеры

Список очередей:

```bash
./yandex-tracker.sh queues
```

Создать задачу:

```bash
./yandex-tracker.sh issue-create MYQUEUE "Краткое описание"
```

Создать задачу с дополнительными полями (JSON через stdin):

```bash
echo '{"description":"Подробное описание"}' | ./yandex-tracker.sh issue-create MYQUEUE "Заголовок"
```

Поиск задач по YQL:

```bash
echo '{"query":"Queue = MYQUEUE AND Status = Open","limit":10}' | ./yandex-tracker.sh issues-search
```

Добавить комментарий:

```bash
./yandex-tracker.sh issue-comment MYQUEUE-123 "Текст комментария"
```

## Лицензия

См. репозиторий проекта.
