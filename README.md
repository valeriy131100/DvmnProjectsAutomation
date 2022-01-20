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