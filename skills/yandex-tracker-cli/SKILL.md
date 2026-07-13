---
name: yandex-tracker-cli
description: CLI for Yandex Tracker (bash + curl). Queues, issues, comments, worklogs, attachments, YQL.
homepage: https://github.com/bkamuz/yandex-tracker-cli
metadata:
  clawdbot:
    emoji: "📋"
    requires:
      env: ["TOKEN", "ORG_ID"]
      bins: ["curl", "jq"]
    primaryEnv: "TOKEN"
    files: ["yandex-tracker.sh"]
  openclaw:
    requires:
      env: ["TOKEN", "ORG_ID"]
      bins: ["curl", "jq"]
    primaryEnv: "TOKEN"
---

# Yandex Tracker CLI Skill

Простой CLI для Yandex Tracker на чистом bash + curl. Работает напрямую через API с правильными заголовками (`X-Org-Id`). Не требует внешних зависимостей кроме `curl` и `jq`.

## Установка

1. Скопируйте скрипт в директорию в PATH:
```bash
mkdir -p ~/bin
cp yandex-tracker.sh ~/bin/yandex-tracker
chmod +x ~/bin/yandex-tracker
```

Или создайте симлинк:
```bash
ln -s /path/to/skill/yandex-tracker.sh ~/bin/yandex-tracker
```

2. **Предоставьте credentials**: нужны TOKEN и ORG_ID — либо через переменные окружения, либо через конфигурационный файл (достаточно одного способа). Скрипт обращается к файлу только если TOKEN/ORG_ID не заданы в окружении.

**Вариант A — через переменные окружения (рекомендуется):**
```bash
export TOKEN='y0__...'      # OAuth токен (Tracker UI → Settings → Applications → OAuth)
export ORG_ID='1234...'     # Org ID (DevTools → Network → X-Org-Id)
```
Эти переменные можно добавить в `~/.bashrc` или `~/.profile`.

**Вариант B — через конфигурационный файл:**
Создайте `~/.yandex-tracker-env` (скрипт использует его только если TOKEN/ORG_ID не заданы в окружении). Формат — строки `KEY=value` (комментарии с `#` игнорируются). Файл **читается как текст** (парсятся только TOKEN и ORG_ID), без выполнения кода:
```bash
TOKEN='y0__...'
ORG_ID='1234...'
```
Предпочтительно задавать учётные данные переменными окружения. Если используете файл — установите права `chmod 600 ~/.yandex-tracker-env`.

3. Убедитесь, что `jq` установлен:
```bash
sudo apt install jq   # Ubuntu/Debian
# или
brew install jq       # macOS
```

## Использование

### Основные команды

| Команда | Описание |
|---------|----------|
| `queues` | Список всех очередей (формат: `key<TAB>name`) |
| `queue-get <key>` | Детали очереди (JSON) |
| `queue-fields <key>` | Все поля очереди (включая локальные) |
| `issue-get <issue-id>` | Получить задачу (формат: `BIMLAB-123`) |
| `issue-create <queue> <summary>` | **Создать задачу. Автоматически добавляет тег `yandex-tracker-cli`. Доп. поля через stdin (JSON)** |
| `issue-update <issue-id>` | **Обновить задачу. Автоматически добавляет тег `yandex-tracker-cli` если отсутствует. Доп. поля через stdin (JSON)** |
| `issue-delete <issue-id>` | Удалить задачу |
| `issue-comment <issue-id> <text>` | Добавить комментарий |
| `issue-comment-edit <issue-id> <comment-id> <new-text>` | Редактировать комментарий |
| `issue-comment-delete <issue-id> <comment-id>` | Удалить комментарий |
| `issue-transitions <issue-id>` | Список доступных переходов статсусы (GET) |
| `issue-transition <issue-id> <transition-id>` | Выполнить переход статуса (POST, V3 endpoint) |
| `issue-close <issue-id> <resolution>` | Закрыть задачу (устарел, может не работать; лучше использовать `issue-transition` с переходом `close`) |
| `issue-worklog <issue-id> <duration> [comment]` | Добавить worklog (duration: `PT1H30M`) |
| `issue-attachments <issue-id>` | Список вложений задачи (JSON) |
| `attachment-download <issue-id> <fileId> [output]` | Скачать файл. Если output не указано — stdout |
| `attachment-upload <issue-id> <filepath> [comment]` | Загрузить файл в задачу. Опциональный комментарий |
| `issues-search` | Поиск задач через YQL. Запрос JSON через stdin, например: `{"query":"Queue = BIMLAB AND Status = Open","limit":50}` |
| `projects-list` | Список всех проектов (JSON) |
| `project-get <project-id>` | Детали проекта |
| `project-issues <project-id>` | Список задач проекта |
| `sprints-list` | Список спринтов (Agile) |
| `sprint-get <sprint-id>` | Детали спринта |
| `sprint-issues <sprint-id>` | Задачи в спринте |
| `users-list` | Список всех пользователей (справочник) |
| `statuses-list` | Список всех статусов задач |
| `resolutions-list` | Список разрешений для закрытия задач |
| `issue-types-list` | Список типов задач (bug, task, improvement) |
| `issue-checklist <issue-id>` | Список пунктов чеклиста задачи |
| `checklist-add <issue-id> <text>` | Добавить пункт в чеклист |
| `checklist-complete <issue-id> <item-id>` | Отметить пункт как выполненный |
| `checklist-delete <issue-id> <item-id>` | Удалить пункт чеклиста |

### Примеры

```bash
# Список очередей
yandex-tracker queues

# Создать задачу с дополнительными полями
echo '{"priority":"critical","description":"Подробности"}' | yandex-tracker issue-create BIMLAB "Новая задача"

# Добавить комментарий
yandex-tracker issue-comment BIMLAB-266 "Работаю над этим"

# Добавить spent time
yandex-tracker issue-worklog BIMLAB-266 PT2H "Исследование"

# Получить возможные переходы (список)
yandex-tracker issue-transitions BIMLAB-266 | jq .

# Выполнить переход (например, «Решить»)
yandex-tracker issue-transition BIMLAB-266 resolve

# Закрыть задачу (устарел, лучше использовать transition close)
yandex-tracker issue-transition BIMLAB-266 close

# Обновить задачу (очередь, исполнитель, проект — id проекта из projects-list)
echo '{"queue":"RAZRABOTKA"}' | yandex-tracker issue-update BIMLAB-266 # пример
echo '{"assignee":"<uid>","project":123}' | yandex-tracker issue-update BIMLAB-280

# Поиск задач через YQL
echo '{"query":"Queue = BIMLAB AND Status = Open","limit":20}' | yandex-tracker issues-search | jq .

# Список проектов
yandex-tracker projects-list | jq .

# Задачи проекта
yandex-tracker project-issues 104 | jq .

# Вложения (Attachments)
# Список вложений
yandex-tracker issue-attachments BIMLAB-266 | jq .
# Скачать файл (fileId из списка вложений) в указанный путь
yandex-tracker attachment-download BIMLAB-266 abc123 /tmp/downloaded.pdf
# Загрузить файл в задачу (с комментарием)
yandex-tracker attachment-upload BIMLAB-266 /path/to/file.pdf "Служебная записка"

# Чеклист (Checklist) — API v3 (checklistItems)
# Просмотреть чеклист задачи (id пунктов — строки, например "5fde5f0a1aee261d********")
yandex-tracker issue-checklist BIMLAB-279 | jq .
# Добавить пункт
yandex-tracker checklist-add BIMLAB-279 "Подготовить презентацию"
# Отметить пункт как выполненный (item-id из вывода issue-checklist)
yandex-tracker checklist-complete BIMLAB-279 "5fde5f0a1aee261d********"
# Удалить пункт
yandex-tracker checklist-delete BIMLAB-279 "5fde5f0a1aee261d********"

# Спринты (Agile)
yandex-tracker sprints-list | jq .
yandex-tracker sprint-issues 42 | jq .

# Справочники
yandex-tracker users-list | jq .
yandex-tracker statuses-list | jq .
yandex-tracker resolutions-list | jq .
yandex-tracker issue-types-list | jq .

# Редактирование и удаление комментариев
yandex-tracker issue-comment-edit BIMLAB-266 12345 "Обновлённый текст"
yandex-tracker issue-comment-delete BIMLAB-266 12345

# Переходы статусов
# Посмотреть список доступных переходов
yandex-tracker issue-transitions BIMLAB-266 | jq .
# Выполнить переход (например, «Решить» или «Закрыть»)
yandex-tracker issue-transition BIMLAB-266 resolve
yandex-tracker issue-transition BIMLAB-266 close
```

## Примечания

- **Автоматический тег `yandex-tracker-cli`:** При создании (`issue-create`) и обновлении (`issue-update`) задач скрипт автоматически добавляет тег `yandex-tracker-cli` (если он ещё отсутствует). Это помогает фильтровать задачи, созданные через CLI. Если нужно убрать тег — удалите его вручную через интерфейс Tracker или вызовите `issue-update` с пустым массивом `tags: []`.
- **Org-ID (Яндекс 360):** Найдите в DevTools Tracker → Network → любой запрос → заголовок `X-Org-ID`. Используется заголовок `X-Org-ID` (обратите внимание на заглавные "ID").
- **Cloud Org-ID (Yandex Cloud):** Используйте заголовок `X-Cloud-Org-ID`. В зависимости от типа организации используйте соответствующий заголовок.
- **Переходы статусов (transitions):**
  - `issue-transitions <issue-id>` — GET-запрос к V2 endpoint `/v2/issues/{id}/transitions` (возвращает список доступных переходов).
  - `issue-transition <issue-id> <transition-id>` — POST-запрос к V3 endpoint `/v3/issues/{id}/transitions/{transition}/_execute` для выполнения перехода. Требует заголовка `X-Org-ID` или `X-Cloud-Org-ID`.
- **Закрытие задач:** Команда `issue-close` устарела и может возвращать 405 в новых конфигурациях. Для закрытия используйте `issue-transition <id> close`.
- Токен можно получить в Tracker UI: Settings → Applications → OAuth → Generate new token.
- Все команды выводят JSON через `jq` для удобной дальнейшей обработки.

## Security (attachments)

Команды `attachment-download` и `attachment-upload` допускают только пути внутри разрешённой директории. Это снижает риск чтения или записи произвольных файлов при использовании CLI (в т.ч. агентом).

- **Первый запуск:** при первом вызове `attachment-download` или `attachment-upload` (если не задано `YANDEX_TRACKER_ATTACHMENTS_DIR`) скрипт в интерактивном режиме спросит: использовать папку по умолчанию `~/Downloads/YandexTrackerCLI` или ввести свой путь. Выбор сохраняется в `~/.yandex-tracker-attachments-dir` и больше не запрашивается.
- **YANDEX_TRACKER_ATTACHMENTS_DIR** — опциональная переменная окружения: базовая директория для вложений. Если задана — используется она (запрос при первом запуске не показывается). Если не задана и нет сохранённого выбора — при первом запуске запрос, иначе используется текущая директория (например, при неинтерактивном запуске).

**Когда навык используется AI-агентом:**

- Не предлагать и не выполнять `attachment-download` с путём вывода вне разрешённой директории; не использовать чувствительные пути (например `~/.ssh`, `~/.env`, `~/.yandex-tracker-env`, `/etc`, другие конфиги и секреты).
- Не предлагать и не выполнять `attachment-upload` с файлом вне разрешённой директории; не загружать файлы из чувствительных расположений (тот же список).
- Если пользователь просит скачать вложение в чувствительный путь или приложить файл из такого пути — отказать и кратко объяснить ограничение.

**Проект по неполному имени (назначить задачу в проект):**

Когда пользователь просит добавить задачу в проект, но указывает не полное имя (например «Common», «проект Common», «Менеджер»):

1. Получить список проектов: `yandex-tracker projects-list` (или `project-get` по известному id).
2. Найти совпадения по словам: отфильтровать проекты, у которых в названии (`name`), ключе (`key`) или отображаемом имени (`display`, если есть) встречаются введённые пользователем слова (желательно без учёта регистра).
3. Если найден ровно один проект — показать пользователю: «Добавить задачу в проект «<название>» (id: <id>)?» и при согласии выполнить обновление с этим проектом.
4. Если найдено несколько — перечислить их (название и id) и уточнить: «Какой из этих проектов имеется в виду?»
5. Если ничего не найдено — сообщить об этом и предложить вызвать `projects-list` и выбрать вручную.
6. Для обновления задачи использовать `issue-update`: в API v2 в теле PATCH передаётся **числовой идентификатор проекта** в поле `project`: `echo '{"project":<id>}' | yandex-tracker issue-update <issue-id>`. Использовать значение `id` из ответа списка/детали проекта (в v2 это shortId/числовой id).

## Структура

```
skills/yandex-tracker-cli/
├── yandex-tracker        # Исполняемый скрипт
├── SKILL.md              # Эта документация
├── ~/.yandex-tracker-env # (опционально, не в репо) Конфиг с TOKEN и ORG_ID
└── ~/.yandex-tracker-attachments-dir # (опционально) Сохранённая папка для вложений после первого запроса
```

## Limitations

- Нет пагинации (т. первые 100 элементов)
- Нет продвинутого поиска (`issues_find` можно добавить)
- Простая валидация аргументов

## License

MIT
