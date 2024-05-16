from flask import Flask, render_template, request, session, redirect, url_for
import requests
import mysql.connector

app = Flask(__name__)
app.secret_key = b'\xab\x14\xe2\xfc\xd3\xd0\x83\x07\xfd\x85\x9e]\x07x\xd5\xc8D\xec\x97r\xe1\xea\xb3\x8b'


def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2006",
        database="weatherapp"
    )


@app.route('/register', methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        # Extract form data
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Username and password are required.", 400

        try:
            # Connect to the database
            connection = get_database_connection()
            cursor = connection.cursor()

            # Prepare SQL query (using parameterized query to prevent SQL injection)
            query = "INSERT INTO users(Username, password) VALUES (%s, %s)"
            data = (username, password)

            # Execute query
            cursor.execute(query, data)

            # Commit changes
            connection.commit()

            print("Data inserted successfully")

        except Exception as e:
            print("Error:", e)
            return "An error occurred while registering. Please try again later.", 500

        finally:
            if 'connection' in locals():
                connection.close()

    return render_template('registrer.html')

@app.route('/login', methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        # Extract form data
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "Username and password are required.", 400

        try:
            # Connect to the database
            connection = get_database_connection()
            cursor = connection.cursor()

            # Check if the user exists in the database
            query = "SELECT * FROM users WHERE Username = %s AND password = %s"
            data = (username, password)
            cursor.execute(query, data)
            user = cursor.fetchone()

            if user:
                # If user exists, set the session username
                session['username'] = username
                return redirect(url_for('index'))  # Redirect to index route after successful login

        except Exception as e:
            print("Error:", e)
            return "An error occurred while logging in. Please try again later.", 500

        finally:
            # Close cursor and connection
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    return render_template('login.html')




@app.route('/', methods=['GET', 'POST'])
def index():
    username = session.get('username')  # Retrieve the username from the session

    if request.method == 'POST':
        city_name = request.form['name']

        api_key = 'ea99730f45b2a1cf3715bb86e4d17a50'
        url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(city_name, api_key)
        response = requests.get(url).json()

        temp = round(response['main']['temp'] - 273.15, 2)
        weather = response['weather'][0]['description']
        icon = response['weather'][0]['icon']

        print(temp, weather, icon)
        return render_template('index.html', temp=temp, weather=weather, icon=icon, city_name=city_name, username=username)
    else:
        return render_template('index.html', username=username)


@app.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/FAQ')
def FAQ():
    return render_template('Faq.html')



if __name__ == '__main__':
    app.run(debug=True)
