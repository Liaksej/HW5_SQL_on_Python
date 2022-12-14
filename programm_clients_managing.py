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
                if cuantity_of_phones == 1 and len(data['phones']) == 1:
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
                else:
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
    print('?????????????? ???? ????????????????:\n'
          'c - ??????????????, ?????????????????? ?????????????????? ???? (??????????????);\n'
          'i - ??????????????, ?????????????????????? ???????????????? ???????????? ??????????????\n'
          't - ??????????????, ?????????????????????? ???????????????? ?????????????? ?????? ?????????????????????????? ??????????????;\n'
          'u - ??????????????, ?????????????????????? ???????????????? ???????????? ?? ??????????????;\n'
          'dt - ??????????????, ?????????????????????? ?????????????? ?????????????? ?????? ?????????????????????????? ??????????????;\n'
          'dc - ??????????????, ?????????????????????? ?????????????? ?????????????????????????? ??????????????;\n'
          'f - ??????????????, ?????????????????????? ?????????? ?????????????? ???? ?????? ???????????? (??????????, ??????????????, email-?? ?????? ????????????????)\n'
          'q - quit')

    with psycopg2.connect(database='clients_managing_db', user='postgres', password='') as conn:
        while True:
            command = input('\n?????????????? ??????????????: ')
            if command == 'c':
                create_db()
            if command == 'i':
                insert_new_client(name=input('?????????????? ??????: '), surname=input('?????????????? ??????????????: '),
                                  email=input('?????????????? email: '),
                                  phones=(input('?????????????? ??????????(??) ????????????????(????): ')).split(', '))
            if command == 't':
                insert_phone_number_for_existing_client(email=input('?????????????? email ??????????????: '),
                                                        phones=(input('?????????????? ??????????(??) ????????????????(????): ')).split(', '))
            if command == 'u':
                change = input('?????? ???????????? ????????????????: ??????, ??????????????, email ?????? ?????????????? ? -->')
                if change == '??????':
                    update_data_client(existing_email=input('?????????????? ???????????????????????? email ??????????????: '),
                                       name=input('?????????????? ?????????? ?????? ??????????????: '))
                elif change == '??????????????':
                    update_data_client(existing_email=input('?????????????? ???????????????????????? email ??????????????: '),
                                       surname=input('?????????????? ?????????? ?????????????? ??????????????: '))
                elif change == 'email':
                    update_data_client(existing_email=input('?????????????? ???????????????????????? email ??????????????: '),
                                       new_email=input('?????????????? ?????????? email ??????????????: '))
                elif change == '??????????????':
                    update_data_client(existing_email=input('?????????????? ???????????????????????? email ??????????????: '),
                                       phones=(input('?????????????? ??????????(??) ????????????????(????): ')).split(', '))
            if command == 'dt':
                delete_clients_phones(email=input('?????????????? email ??????????????: '))
            if command == 'dc':
                delete_client(email=input('?????????????? email ??????????????: '))
            if command == 'f':
                find_data = input('???? ?????????? ???????????? ???????????? ?????????? ??????????????: ??????, ????????????, email ?????? ??????????????? -->')
                if find_data == '??????':
                    print('?????????????????? ????????????:', find_client(name=input('?????????????? ??????: ')))
                elif find_data == '??????????????':
                    print('?????????????????? ????????????:', find_client(surname=input('?????????????? ??????????????: ')))
                elif find_data == 'email':
                    print('?????????????????? ????????????:', find_client(email=input('?????????????? email: ')))
                elif find_data == '??????????????':
                    print('?????????????????? ????????????:', find_client(phones=input('?????????????? ??????????????: ')))
            if command == 'q':
                break
        # delete_tabs() # ?????????????? ??????????????
    conn.close()
