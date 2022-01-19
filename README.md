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
        "name": "Александр Попов",
        "level": "junior",
        "tg_username": "@example",
        "discord_username": "example#1234",
        "is_far_east": "True"
    },
    {
        "name": "Иван Петров",
        "level": "novice+",
        "tg_username": "@example2",
        "discord_username": "example2#4321",
        "is_far_east": "False"
    }
]
```
Запустите скрипт:
```shell
python manage.py add_students
```