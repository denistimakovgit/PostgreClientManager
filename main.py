import psycopg2

def create_tables(conn):
    """
    Функция создающая таблицы в БД
    """
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            client_name VARCHAR(40),
            client_surname VARCHAR(40),
            client_email VARCHAR(40)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients_phones(
            client_id INTEGER NOT NULL REFERENCES clients(client_id),
            client_phone VARCHAR(40) UNIQUE
        );
        """)
        conn.commit()  # фиксируем в БД

def add_new_client(conn):
    """
    функция созающая клиента в БД
    """
    with conn.cursor() as cur:
        client_name = str(input('Введите имя клиента '))
        client_surname = str(input('Введите фамилию клиента '))
        client_email = str(input('Введите email клиента '))
        cur.execute("""
        INSERT INTO clients(client_name, client_surname, client_email) 
        VALUES(%s, %s, %s);
        """, (str(client_name), str(client_surname), str(client_email)))
        conn.commit()

def add_phone_num(conn):
    """
    функция добавляющая номер телефона клиента
    """
    with conn.cursor() as cur:
        client_name = input('Введите имя клиента ')
        client_surname = input('Введите фамилию клиента ')
        try:
            cur.execute("""
            SELECT client_id FROM clients WHERE client_name=%s and client_surname=%s;
            """, (str(client_name), str(client_surname)))
            client_id = cur.fetchone()[0]
            phone_num = input('Введите номер телефона клиента ')
            cur.execute("""
            INSERT INTO clients_phones(client_id, client_phone) 
            VALUES(%s, %s);
            """, (int(client_id), str(phone_num)))
            conn.commit()
        except:
            print('Клиент не найден')

def change_client_data(conn):
    with conn.cursor() as cur:
        client_name = input('Введите имя клиента: ')
        client_surname = input('Введите имя клиента: ')
        try:
            cur.execute("""
            SELECT client_id FROM clients WHERE client_name=%s and client_surname=%s;
            """, (str(client_name), str(client_surname)))
            client_id = cur.fetchone()[0]
        except:
            print('Клиент не найден')
            return

        new_name = input('Изменение данных. Введите имя клиента: ')
        new_surname = input('Изменение данных. Введите фамилию клиента: ')
        new_email = input('Изменение данных. Введите email клиента ')
        try:
            cur.execute("""
            UPDATE clients SET client_name = %s, client_surname = %s, client_email = %s 
            WHERE client_id = %s;
            """, (str(new_name), str(new_surname), str(new_email), int(client_id)))
            conn.commit()
        except:
            print('Изменить данные не удалось')

def delete_phone_num(conn):
    """
    Функция для удаления номера телефона клиента
    """
    with conn.cursor() as cur:
        phone_num = input('Удаление тел.номера. Введите номер телефона клиента: ')
        print(type(phone_num))
        try:
            cur.execute("""
            DELETE FROM clients_phones WHERE client_phone = %s;
            """, (phone_num,))
            conn.commit()
        except:
            print('Удалить запись не удалось. Возможно номер телефона введен не корректно')
            return

def delete_client(conn):
    """
    Функция удаления клиента вместе с его номером телефона
    """
    with conn.cursor() as cur:
        client_name = input('Введите имя клиента: ')
        client_surname = input('Введите имя клиента: ')
        try:
            cur.execute("""
            SELECT client_id FROM clients WHERE client_name=%s and client_surname=%s;
            """, (str(client_name), str(client_surname)))
            client_id = cur.fetchone()[0]
        except:
            print('Клиент не найден')
            return

        try:
            cur.execute("""
            DELETE FROM clients_phones WHERE client_id = %s;
            """, (client_id,))
            conn.commit()
        except:
            print('Удалить запись не удалось. Возможно ФИО клиента введено не корректно')
            return

        try:
            cur.execute("""
            DELETE FROM clients WHERE client_id = %s;
            """, (client_id,))
            conn.commit()
        except:
            print('Удалить запись не удалось. Возможно ФИО клиента введено не корректно')
            return

def find_client(conn):
    """
    Функция поиска клиента по следующим параметрам:
    - Имя
    - Фамилия
    - Номер телефона или адрес email
    """
    with conn.cursor() as cur:
        client_name = input('Введите имя клиента: ')
        client_surname = input('Введите имя клиента: ')
        phone_num = input('Введите номер телефона клиента: ')
        email = input('Введите email клиента: ')

        cur.execute("""
        SELECT * FROM clients c 
        WHERE c.client_name LIKE %s 
        AND c.client_surname LIKE %s
        AND (c.client_email LIKE %s OR client_id IN 
	        (SELECT client_id FROM clients_phones cp 
	            WHERE cp.client_phone LIKE %s));
            """, (str(client_name), str(client_surname), str(email), str(phone_num)))
        res = cur.fetchall()
        if len(res) == 0:
            print('Клиент не найден')
        else:
            print('fetchall', res)

with psycopg2.connect(database="ClientManagment_db", user="postgres", password="postgres") as conn:

    create_tab = create_tables(conn)

    while True:

        print('Список команд для управления клиентом:'
              '\n -a - добавить нового клиента'
              '\n -b - добавить номер телефона клиента'
              '\n -с - изменить данные клиента'
              '\n -d - удалить номер телефона клиента'
              '\n -e - удалить клиента'
              '\n -f - поиск клиента'
              '\n любая другая клавиша - выход из программы')
        command = input('Введите команду ')

        if command == 'a':
            function_start = add_new_client(conn)
        elif command == 'b':
            function_start = add_phone_num(conn)
        elif command == 'c':
            function_start = change_client_data(conn)
        elif command == 'd':
            function_start = delete_phone_num(conn)
        elif command == 'e':
            function_start = delete_client(conn)
        elif command == 'f':
            function_start = find_client(conn)
        else:
            print('Выход')
            break

conn.close()