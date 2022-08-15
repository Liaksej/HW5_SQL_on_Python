import psycopg2


def create_db():
    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    PRIMARY KEY (client_id),
                    client_id SERIAL,
                    name      VARCHAR(80)         NOT NULL,
                    surname   VARCHAR(160)        NOT NULL,
                    email     VARCHAR(240) UNIQUE NOT NULL
                );
                """)
        conn.commit()
        cur.execute("""
                CREATE TABLE IF NOT EXISTS phones (
                    PRIMARY KEY (phone_number),
                    phone_number VARCHAR(11) UNIQUE   CONSTRAINT only_digits CHECK (phone_number NOT LIKE '%[^0-9]%'),
                    client_id INTEGER        NOT NULL REFERENCES clients (client_id)       
                );
                """)
        conn.commit()


# def delete_tabs():
#     # with conn.cursor() as cur:
#     #     # cur.execute("""
#     #     #     DROP TABLE clients;
#     #     #     DROP TABLE phones;
#     #     #     """)
#     #     conn.commit()


def insert_new_client(name, surname, email, **phones):
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO clients(name, surname, email) 
                VALUES(%s, %s, %s);
                """, (name, surname, email))
        conn.commit()
        cur.execute("""
                SELECT client_id FROM clients
                 WHERE email=%s;
                """, (email,))
        clien_id_for_insert_to_phones_tab = cur.fetchone()[0]
        for item in phones['phones']:
            cur.execute("""
            INSERT INTO phones(phone_number, client_id) 
            VALUES(%s, %s);
            """, (item, clien_id_for_insert_to_phones_tab))
        conn.commit()


def insert_phone_number_for_existing_client(email, phones):
    with conn.cursor() as cur:
        cur.execute("""
                SELECT client_id 
                  FROM clients
                 WHERE email=%s;
                """, (email,))
        clien_id_for_insert_to_phones_tab = cur.fetchone()[0]
        for phone in phones:
            cur.execute("""
                    INSERT INTO phones(phone_number, client_id) 
                    VALUES(%s, %s);
                    """, (phone, clien_id_for_insert_to_phones_tab))
        conn.commit()


def update_data_client(existing_email, **data):
    with conn.cursor() as cur:
        cur.execute("""
                SELECT client_id 
                  FROM clients
                 WHERE email=%s;
                """, (existing_email,))
        clien_id_for_insert_to_phones_tab = cur.fetchone()[0]
        for item in data:
            if item == 'name':
                cur.execute("""
                        UPDATE clients
                           SET name = %s
                         WHERE client_id = %s;
                    """, (data['name'], clien_id_for_insert_to_phones_tab))
                conn.commit()
            elif item == 'surname':
                cur.execute("""
                        UPDATE clients
                           SET surname = %s
                         WHERE client_id = %s;
                    """, (data['surname'], clien_id_for_insert_to_phones_tab))
                conn.commit()
            elif item == 'new_email':
                cur.execute("""
                       UPDATE clients
                          SET email = %s
                        WHERE client_id = %s;
                       """, (data['new_email'], clien_id_for_insert_to_phones_tab))
                conn.commit()
            elif item == 'phones':
                cur.execute("""
                        SELECT count(client_id) 
                          FROM phones
                         WHERE client_id=%s;
                        """, (clien_id_for_insert_to_phones_tab,))
                cuantity_of_phones = cur.fetchone()[0]
                if cuantity_of_phones and len(data['phones']) == 1:
                    for phone in data['phones']:
                        cur.execute("""
                        UPDATE phones
                           SET phone_number = %s
                         WHERE client_id = %s;
                        """, (phone, clien_id_for_insert_to_phones_tab))
                    conn.commit()
                elif cuantity_of_phones == 0:
                    for phone in data['phones']:
                        cur.execute("""
                        INSERT INTO phones(phone_number, client_id) 
                        VALUES(%s, %s);
                        """, (phone, clien_id_for_insert_to_phones_tab))
                    conn.commit()
                elif cuantity_of_phones >= 1:
                    cur.execute("""
                            DELETE FROM phones
                             WHERE client_id = %s;
                    """, (clien_id_for_insert_to_phones_tab,))
                    conn.commit()
                    for phone in data['phones']:
                        cur.execute("""
                            INSERT INTO phones(phone_number, client_id) VALUES(%s, %s);
                            """, (phone, clien_id_for_insert_to_phones_tab))
                    conn.commit()


def delete_clients_phones(email):
    with conn.cursor() as cur:
        cur.execute("""
                SELECT client_id 
                  FROM clients
                 WHERE email=%s;
                """, (email,))
        clien_id_for_insert_to_phones_tab = cur.fetchone()[0]
        cur.execute("""
                SELECT count(client_id) 
                  FROM phones
                 WHERE client_id=%s;
                """, (clien_id_for_insert_to_phones_tab,))
        cuantity_of_phones = cur.fetchone()[0]
        if cuantity_of_phones > 0:
            cur.execute("""
                    DELETE FROM phones
                    WHERE client_id = %s;
            """, (clien_id_for_insert_to_phones_tab,))
            conn.commit()


def delete_client(email):
    with conn.cursor() as cur:
        cur.execute("""
                SELECT client_id 
                  FROM clients
                 WHERE email=%s;
                """, (email,))
        clien_id_for_insert_to_phones_tab = cur.fetchone()[0]
        cur.execute("""
                DELETE FROM phones
                WHERE client_id = %s;
                """, (clien_id_for_insert_to_phones_tab,))
        cur.execute("""
                DELETE FROM clients
                WHERE client_id = %s;
                """, (clien_id_for_insert_to_phones_tab,))
        conn.commit()


def find_client(**kwargs):
    for item in kwargs:
        if item == 'name':
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT name, surname, email, phone_number 
                          FROM clients c
                     LEFT JOIN phones p ON c.client_id = p.client_id
                         WHERE name=%s;
                        """, (kwargs['name'],))
                show_result = cur.fetchall()
        elif item == 'surname':
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT name, surname, email, phone_number 
                          FROM clients c
                     LEFT JOIN phones p ON c.client_id = p.client_id
                         WHERE surname=%s;
                        """, (kwargs['surname'],))
                show_result = cur.fetchall()
        elif item == 'email':
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT name, surname, email, phone_number 
                          FROM clients c
                     LEFT JOIN phones p ON c.client_id = p.client_id
                         WHERE email=%s;
                        """, (kwargs['email'],))
                show_result = cur.fetchall()
        elif item == 'phones':
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT name, surname, email, phone_number 
                          FROM clients c
                          JOIN phones p ON c.client_id = p.client_id
                         WHERE phone_number=%s;
                        """, (kwargs['phones'],))
                show_result = cur.fetchall()[0]
        return show_result


if __name__ == '__main__':
    print('Справка по командам:\n'
          'c - Функция, создающая структуру БД (таблицы);\n'
          'i - Функция, позволяющая добавить нового клиента\n'
          't - Функция, позволяющая добавить телефон для существующего клиента;\n'
          'u - Функция, позволяющая изменить данные о клиенте;\n'
          'dt - Функция, позволяющая удалить телефон для существующего клиента;\n'
          'dc - Функция, позволяющая удалить существующего клиента;\n'
          'f - Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)\n'
          'q - quit')

    with psycopg2.connect(database='clients_managing_db', user='postgres', password='') as conn:
        while True:
            command = input('\nВведите команду: ')
            if command == 'c':
                create_db()
            if command == 'i':
                insert_new_client(name=input('Введите имя: '), surname=input('Введите фамилию: '),
                                  email=input('Введите email: '),
                                  phones=(input('Введите номер(а) телефона(ов): ')).split(', '))
            if command == 't':
                insert_phone_number_for_existing_client(email=input('Введите email клиента: '),
                                                        phones=(input('Введите номер(а) телефона(ов): ')).split(', '))
            if command == 'u':
                change = input('Что хотите изменить: имя, фамилию, email или телефон ? -->')
                if change == 'имя':
                    update_data_client(existing_email=input('Введите существующий email клиента: '),
                                       name=input('Введите новое имя клиента: '))
                elif change == 'фамилию':
                    update_data_client(existing_email=input('Введите существующий email клиента: '),
                                       surname=input('Введите новую фамилию клиента: '))
                elif change == 'email':
                    update_data_client(existing_email=input('Введите существующий email клиента: '),
                                       new_email=input('Введите новый email клиента: '))
                elif change == 'телефон':
                    update_data_client(existing_email=input('Введите существующий email клиента: '),
                                       phones=(input('Введите номер(а) телефона(ов): ')).split(', '))
            if command == 'dt':
                delete_clients_phones(email=input('Введите email клиента: '))
            if command == 'dc':
                delete_client(email=input('Введите email клиента: '))
            if command == 'f':
                find_data = input('По каким данным хотите найти клиента: имя, фамиля, email или телефон? -->')
                if find_data == 'имя':
                    print('Результат поиска:', find_client(name=input('Введите имя: ')))
                elif find_data == 'фамилия':
                    print('Результат поиска:', find_client(surname=input('Введите фамилию: ')))
                elif find_data == 'email':
                    print('Результат поиска:', find_client(email=input('Введите email: ')))
                elif find_data == 'телефон':
                    print('Результат поиска:', find_client(phones=input('Введите телефон: ')))
            if command == 'q':
                break
        # delete_tabs() # удаляет таблицы
    conn.close()
