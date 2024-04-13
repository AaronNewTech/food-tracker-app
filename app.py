from flask import Flask, render_template, g, request
from datetime import datetime
from connect_db import connect_db, get_db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date'] #assuming the date is in YYYY-MM-DD format

        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()

    pointer = db.execute('''SELECT log_date.entry_date, 
       COALESCE(SUM(food.protein), 0) AS protein, 
       COALESCE(SUM(food.carbohydrate), 0) AS carbohydrate, 
       COALESCE(SUM(food.fat), 0) AS fat, 
       COALESCE(SUM(food.calories), 0) AS calories 
FROM log_date 
LEFT JOIN food_date ON food_date.log_date_id = log_date.id 
LEFT JOIN food ON food.id = food_date.food_id 
GROUP BY log_date.entry_date 
ORDER BY log_date.entry_date DESC;
''')

    results = pointer.fetchall()

    date_results = []

    for i in results:
        single_date = {}

        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrate'] = i['carbohydrate']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')

        date_results.append(single_date)

    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=['GET', 'POST']) #date is going to be 20170520
def view(date):
    db = get_db()

    pointer = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = pointer.fetchone()

    if request.method == 'POST':
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', [request.form['food-select'], date_result['id']])
        db.commit()

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    food_pointer = db.execute('select id, name from food')
    food_results = food_pointer.fetchall()

    log_pointer = db.execute('''select food.name, food.protein, food.carbohydrate, food.fat, food.calories 
                            from log_date 
                            join food_date on food_date.log_date_id = log_date.id 
                            join food on food.id = food_date.food_id 
                            where log_date.entry_date = ?''', [date])

    log_results = log_pointer.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbohydrate'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrate'] += food['carbohydrate']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, \
                           food_results=food_results, log_results=log_results, totals=totals)

@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrate = int(request.form['carbohydrate'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrate * 4 + fat * 9
     
        db.execute('insert into food (name, protein, carbohydrate, fat, calories) values (?, ?, ?, ?, ?)', \
            [name, protein, carbohydrate, fat, calories])
        db.commit()

    pointer = db.execute('select name, protein, carbohydrate, fat, calories from food')
    results = pointer.fetchall()

    return render_template('add_food.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5555)