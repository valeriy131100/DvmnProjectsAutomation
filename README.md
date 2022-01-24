# DvmnProjectsAutomation

Бот и админка для автоматизации ведения проектов на [dvmn](https://dvmn.org).

## Установка
Вам понадобится установленный Python 3.8+ и git.

Склонируйте репозиторий:
```bash
git clone https://github.com/valeriy131100/DvmnProjectsAutomation
```

Создайте в этой папке виртуальное окружение:
```bash
cd DvmnProjectsAutomation
python3 -m venv venv
```

Активируйте виртуальное окружение и установите зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка перед использованием

### Переменные среды

Перед использованием вам необходимо заполнить .env.example файл или иным образом передать переменные среды:
* TELEGRAM_TOKEN - токен бота Telegram. Можно получить у [@BotFather](https://t.me/BotFather).
* ALLOWED_HOSTS - список разрешенных хостов через запятую. По умолчанию - `127.0.0.1`.
* DEBUG - включить ли режим дебага в Django. Булево значение (True или False). По умолчанию - True.

### Миграции

Перед использованием нужно обязательно применить миграции базы данных.

Для этого при активном виртуальном окружении напишите:
```shell
python manage.py migrate
```

### Добавить студентов из json-файла

Для того чтобы добавить всех студентов в базу данных, положите students.json в папку Students.
<details>
<summary>Пример файла</summary>

```json
[
  {
    "name": "Валерий Ефремов",
    "level": "novice+",
    "telegram_id": 34534324,
    "discord_username": "example#1234",
    "is_far_east": "False"
  },
  {
    "name": "Илья Габдрахманов",
    "level": "novice",
    "telegram_id": 234234234,
    "discord_username": "example2#4321",
    "is_far_east": "False"
  },
  {
    "name": "Максим Кутовой",
    "level": "junior",
    "telegram_id": 123123123,
    "discord_username": "example2#4321",
    "is_far_east": "True"
  }
]
```

</details>

Запустите скрипт:
```shell
python manage.py add_students
```

<details>
<summary>Если файл находится в другом месте</summary>

Если json-файл лежит в другой папке, то передайте параметр `-p`
```shell
python manage.py add_students -p some_folder/managers.json
```
Если json-файл лежит в интернете, то передайте адрес в параметре `-u`
```shell
python manage.py add_students -u https://raw.githubusercontent.com/valeriy131100/DvmnProjectsAutomation/main/json_examples/students.json
```

</details>


### Добавить менеджеров из json-файла

Для того чтобы добавить всех менеджеров в базу данных, положите managers.json в папку PMs.
<details>
<summary>Пример файла</summary>

```json
[
  {
    "name": "Артем",
    "telegram_id": 12345678,
    "projects_time_begin": "20:00:00",
    "projects_time_end": "23:00:00"
  },
  {
    "name": "Екатерина",
    "telegram_id": 989898989,
    "projects_time_begin": "17:00:00",
    "projects_time_end": "20:00:00"
  },
  {
    "name": "Тим",
    "telegram_id": 124435653,
    "projects_time_begin": "18:00:00",
    "projects_time_end": "21:00:00"
  }
]
```

</details>

Запустите скрипт:
```shell
python manage.py add_project_managers
```

<details>
<summary>Если файл находится в другом месте</summary>

Если json-файл лежит в другой папке, то передайте параметр `-p`
```shell
python manage.py add_project_managers -p some_folder/managers.json
```
Если json-файл лежит в интернете, то передайте адрес в параметре `-u`
```shell
python manage.py add_project_managers -u https://raw.githubusercontent.com/valeriy131100/DvmnProjectsAutomation/main/json_examples/managers.json
```
Для получения адреса json-файла, расположенного на [github.com](https://github.com/), откройте json-файл в режиме просмотра в правом углу найдите кнопку 'Raw'

</details>

## Запуск

С активированным виртуальным окружением выполните команды:
```shell
python manage.py runserver
python manage.py bot
```

Запустится телеграм-бот и Django-админка. Первой команде можно передать ip-адрес и порт, чтобы указать, где Django-сервер должен запуститься, по умолчанию же админка будет доступна по адресу http://127.0.0.1:8000/admin.
