# main.py
# etusivun route
import contextlib
import sqlite3

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@contextlib.contextmanager
def connect():
    conn = None
    try:
        conn = sqlite3.connect('users.sqlite')
        yield conn
    finally:
        if conn is not None:
            conn.close()

# _get_users

# erillinen funktio käyttäjien noutamiselle tietokannasta,
# koska tarvitaan useammassa paikassa
def _get_users(conn):
    cur = conn.cursor()
    cur.execute(
        "SELECT users.id, users.name, users.email, departments.name FROM users INNER JOIN departments ON departments.id = users.department_id")
    _users = cur.fetchall()
    users_list = []
    for u in _users:
        users_list.append({'id': u[0], 'name': u[1], 'email': u[2], 'department': u[3]})
    return users_list

@app.route('/js_example')
def js_example():
    return render_template("js_example.html")

@app.route('/')
def index():
    # tämä rivi saa palvelimen generoimaan index.html-sivun ja lähettämään sen vastauksena selaimelle
    return render_template('index.html')

# lisää jatkossa kaikki uudet routet ennen if-lausetta tähän

@app.route('/users', methods=['GET'])
def get_users():
    with connect() as conn:
        _users = _get_users(conn)
        return render_template('users/index.html', users=_users, error=None)


# tähän tullaan, kun formiseta painetaan, Delete-nappia
@app.route('/users', methods=['POST'])
def delete_user():
    # request.form-sisältää tiedot, jotka formilla lähetetään palvelimelle
    _body = request.form
    with connect() as connection:
        try:
            # haetaan userid form datasta
            # userid on formin hidden-inputin name-attribuutin arvo
            userid = _body.get('userid')
            if userid is None:
                raise Exception('missing userid')

            # jos tämä epäonnistuu, tulee ValueError
            userid = int(userid)
            cursor = connection.cursor()
            # jos kaikki onnistuu,
            # poistetaan valittu käyttäjä tietokannasta
            # ja ladataan sivu kokonaan uudelleen
            cursor.execute('DELETE FROM users WHERE id = ?', (userid,))
            connection.commit()
            cursor.close()
            return redirect(url_for('get_users'))

        # valueError-exception tulee silloin
        # jos userid-kenttä ei sisällä numeerista arvoa
        # (ei voida muuttaa kentän arvoa integeriksi)
        except ValueError as e:

            connection.rollback()
            # haetaan käyttäjät ja ladataan sivu uudelleen
            _users = _get_users(connection)
            return render_template('users/index.html', error=str(e), users=_users)

        except Exception as e:
            # haetaan käyttäjät ja ladataan sivu uudelleen
            _users = _get_users(connection)
            connection.rollback()
            return render_template('users/index.html', error=str(e), users=_users)

# GET-metodilla ladataan uuden käyttäjän listäystä varten tehty sivu

def _get_departments(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM departments')
    _departments = cur.fetchall()
    departments_list = []
    for d in _departments:
        departments_list.append({'id': d[0], 'name': d[1]})
    cur.close()
    return departments_list

@app.route('/users/new', methods=['GET'])
def new_user():
    with connect() as con:
        _departments = _get_departments(con)
        return render_template('users/new.html', departments=_departments, error=None)

# POST-metodilla lisätään käyttäjän tiedot lomakkeelta tietokantaan

@app.route('/users/new', methods=['POST'])
def add_user():
    _body = request.form
    with connect() as con:

        try:
            cur = con.cursor()
            cur.execute('INSERT INTO users (name, email, department_id) VALUES (?, ?, ?)',
                        (_body.get('name'), _body.get('email'), _body.get('department_id')))
            con.commit()
            # kun käyttäjä on lisätty tietokantaan, ohjataan selain takaisin käyttäjälistauksen sivulle
            return redirect(url_for('get_users'))
        except Exception as e:
            con.rollback()
            # jos tulee virhe, haetaan departmentit uudelleen ja näytetään lisäksi virhe käyttäjälle
            _departments = _get_departments(con)
            return render_template('users/new.html', error=str(e), departments=_departments)



# osastojen listauksen puolivalmis koodi

@app.route('/departments', methods=['GET'])
def get_departments():
    with connect() as con:
        _departments = _get_departments(con)
        return render_template('departments/index.html', departments=_departments, error=None)
        # lisää tähän puuttuvat osat, jotta saat osastot listattua html-sivulle. TEHTY

@app.route('/departments/new', methods=['GET'])
def new_department():
    with connect() as con:
        departments = _get_departments(con)  # Hae kaikki osastot
        return render_template('departments/new.html', departments=departments, error=None)
        # lisää tähän puuttuva koodi, jotta formin lähettäminen selaimelle onnistuu. TEHTY

# koodi joka lisää rivin tietokantaan

@app.route('/departments/new', methods=['POST'])
def add_department():
    # HUOM!!!!! Muista, että _body-muuttujassa olevat avaimet vastaavat HTML-formin name-attribuutteja
    _body = request.form
    with connect() as con:

        try:
            cur = con.cursor()
            cur.execute('INSERT INTO departments (name) VALUES (?)',
                        # eli jotta 'name'-avain löytyy _bodysta, HTML-formissa osaston lisäysformilla p
                        # pitää osaston nimen tekstikentän name-attribuutti olla arvoltaan name
                        (_body.get('name'), ))
            con.commit()
            # kun osasto on lisätty tietokantaan, ohjataan selain takaisin osastojen listauksen sivulle

            return redirect(url_for('get_departments'))
            # lisää puuttuva koodi tähän. TEHTY

        except Exception as e:
            con.rollback()

            # jos tulee virhe, haetaan departmentit uudelleen ja näytetään lisäksi virhe käyttäjälle

            _departments = _get_departments(con)
            return render_template('departments/index.html', departments = _departments, error=str(e))
            # lisää puuttuvat koodit tähän. TEHTY


if __name__ == '__main__':
    app.run(port=5001, debug=True)
