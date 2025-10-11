#!/bin/bash

# Создание администратора СПбГУ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_spbu",
    "email": "admin.spbu@university.ru",
    "password": "asdfghjkl888",
    "group": "SPbU",
    "first_name_rus": "Алексей",
    "second_name_rus": "Петров",
    "middle_name_rus": "Сергеевич",
    "first_name_eng": "Alexey",
    "second_name_eng": "Petrov",
    "middle_name_eng": "Sergeevich",
    "year_of_birth": 1980,
    "year_of_graduation": 2002,
    "academic_degree": "Доктор наук",
    "year_of_degree": 2010,
    "position": "Профессор"
  }'

echo -e "\n---\n"

# Создание администратора ПОМИ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_pomi",
    "email": "admin.pomi@math.ru",
    "password": "asdfghjkl888",
    "group": "POMI",
    "first_name_rus": "Мария",
    "second_name_rus": "Сидорова",
    "middle_name_rus": "Ивановна",
    "first_name_eng": "Maria",
    "second_name_eng": "Sidorova",
    "middle_name_eng": "Ivanovna",
    "year_of_birth": 1975,
    "year_of_graduation": 1997,
    "academic_degree": "Кандидат наук",
    "year_of_degree": 2005,
    "position": "Старший научный сотрудник"
  }'

echo -e "\n---\n"

# Создание обычного пользователя СПбГУ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_spbu1",
    "email": "user1.spbu@university.ru",
    "password": "asdfghjkl888",
    "group": "SPbU",
    "first_name_rus": "Иван",
    "second_name_rus": "Иванов",
    "middle_name_rus": "Петрович",
    "first_name_eng": "Ivan",
    "second_name_eng": "Ivanov",
    "middle_name_eng": "Petrovich",
    "year_of_birth": 1990,
    "year_of_graduation": 2012,
    "academic_degree": "Кандидат наук",
    "year_of_degree": 2018,
    "position": "Доцент"
  }'

echo -e "\n---\n"

# Создание обычного пользователя ПОМИ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user_pomi1",
    "email": "user1.pomi@math.ru",
    "password": "asdfghjkl888",
    "group": "POMI",
    "first_name_rus": "Ольга",
    "second_name_rus": "Кузнецова",
    "middle_name_rus": "Владимировна",
    "first_name_eng": "Olga",
    "second_name_eng": "Kuznetsova",
    "middle_name_eng": "Vladimirovna",
    "year_of_birth": 1985,
    "year_of_graduation": 2007,
    "academic_degree": "Кандидат наук",
    "year_of_degree": 2013,
    "position": "Научный сотрудник"
  }'

echo -e "\n---\n"

# Создание молодого ученого СПбГУ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "young_spbu",
    "email": "young.spbu@university.ru",
    "password": "asdfghjkl888",
    "group": "SPbU",
    "first_name_rus": "Дмитрий",
    "second_name_rus": "Смирнов",
    "middle_name_rus": "Александрович",
    "first_name_eng": "Dmitry",
    "second_name_eng": "Smirnov",
    "middle_name_eng": "Alexandrovich",
    "year_of_birth": 1995,
    "year_of_graduation": 2017,
    "academic_degree": "",
    "year_of_degree": null,
    "position": "Ассистент"
  }'

echo -e "\n---\n"

# Создание опытного ученого ПОМИ
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "senior_pomi",
    "email": "senior.pomi@math.ru",
    "password": "asdfghjkl888",
    "group": "POMI",
    "first_name_rus": "Сергей",
    "second_name_rus": "Васильев",
    "middle_name_rus": "Николаевич",
    "first_name_eng": "Sergey",
    "second_name_eng": "Vasiliev",
    "middle_name_eng": "Nikolaevich",
    "year_of_birth": 1965,
    "year_of_graduation": 1987,
    "academic_degree": "Доктор наук",
    "year_of_degree": 2000,
    "position": "Главный научный сотрудник"
  }'

echo -e "\n---\n"

# Создание пользователя без отчества
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "no_middle",
    "email": "no.middle@university.ru",
    "password": "asdfghjkl888",
    "group": "SPbU",
    "first_name_rus": "Анна",
    "second_name_rus": "Морозова",
    "middle_name_rus": "",
    "first_name_eng": "Anna",
    "second_name_eng": "Morozova",
    "middle_name_eng": "",
    "year_of_birth": 1988,
    "year_of_graduation": 2010,
    "academic_degree": "Кандидат наук",
    "year_of_degree": 2016,
    "position": "Старший преподаватель"
  }'

echo -e "\n---\n"

# Создание пользователя только с английскими именами
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "english_only",
    "email": "english@university.ru",
    "password": "asdfghjkl888",
    "group": "POMI",
    "first_name_rus": "John",
    "second_name_rus": "Smith",
    "middle_name_rus": "",
    "first_name_eng": "John",
    "second_name_eng": "Smith",
    "middle_name_eng": "",
    "year_of_birth": 1978,
    "year_of_graduation": 2000,
    "academic_degree": "PhD",
    "year_of_degree": 2005,
    "position": "Researcher"
  }'

echo -e "\n---\n"
echo "Все пользователи созданы с паролем: asdfghjkl888"
