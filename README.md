# DvmnProjectsAutomation

## Переменные окружения

Чтобы запустить бота, нужно указать токен в файле `.env`. 
Создайте его рядом с `manage.py`
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ='значение'`.

```sh
TELEGRAM_TOKEN='ваш_токен'
```

### Добавить студентов из json-файла

Для того, чтобы добавить всех студентов в базу данных, положите students.json в папку Students. Пример файла:
```json
[
  {
    "name": "Валерий Ефремов",
    "level": "novice+",
    "telegram_id": "ididididid",
    "discord_username": "example#1234",
    "is_far_east": "False"
  },
  {
    "name": "Илья Габдрахманов",
    "level": "novice",
    "telegram_id": "ididididid",
    "discord_username": "example2#4321",
    "is_far_east": "False"
  },
  {
    "name": "Максим Кутовой",
    "level": "junior",
    "telegram_id": "ididididid",
    "discord_username": "example2#4321",
    "is_far_east": "True"
  }
]
```
Запустите скрипт:
```shell
python manage.py add_students
```

### Добавить менеджеров из json-файла

Для того, чтобы добавить всех менеджеров в базу данных, положите managers.json в папку PMs. Пример файла:
```json
[
  {
    "name": "Артем",
    "telegram_id": "12345678",
    "projects_time_begin": "20:00:00",
    "projects_time_end": "23:00:00"
  },
  {
    "name": "Екатерина",
    "telegram_id": "989898989",
    "projects_time_begin": "17:00:00",
    "projects_time_end": "20:00:00"
  },
  {
    "name": "Тим",
    "telegram_id": "124435653",
    "projects_time_begin": "18:00:00",
    "projects_time_end": "21:00:00"
  }
]
```
Запустите скрипт:
```shell
python manage.py add_project_managers
```

