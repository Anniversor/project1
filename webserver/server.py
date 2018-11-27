"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import random
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask import jsonify
import csv
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "hy2574"
DB_PASSWORD = "q74ml90c"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

schools = []
ranks = []
with open('static/u_rank.csv', 'rb') as file:
  reader = csv.reader(file)
  header = reader.next()
  for row in reader:
    schools.append(row[0])
    ranks.append(row[1])

s_rank = dict(zip(schools, ranks))
print(schools)
print(s_rank)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  if not session.get('logged_in'):
    return render_template('login.html')
  print (request.args)

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

@app.route('/test')
def test():
  context = dict(data=schools)
  return render_template("test.html", **context)

@app.route('/another')
def another():
  return render_template("anotherfile.html")

'''Completed'''
@app.route('/register', methods= ['POST','GET'])
def register():
    if request.method == 'POST':
      cursor = g.conn.execute("SELECT user_account FROM user_affiliation Where user_account = '%s';" % request.form['username'])
      cursor1 = g.conn.execute("SELECT email FROM user_affiliation Where email = '%s';" % request.form['email'])
      rows = cursor.fetchall()
      rows1 = cursor1.fetchall()
      flag = False
      if rows or rows1:
        flag = True
        context = dict(flag=flag,schools = schools)
        cursor.close()
        return render_template("register.html", **context)
      else:
        query = "INSERT INTO user_affiliation (user_account, nickname, password, birthdate, email, gender, school_name, dept_name, degree, credit) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s);"
        data = (request.form['username'], request.form['nickname'],request.form['password'], request.form['birthdate'],request.form['email'], request.form['gender'],request.form['school'],request.form['department'],request.form['degree'], 100)
        print(data)
        cursor = g.conn.execute(query, data)
        print("successfully registered")
        session['logged_in'] = False
        cursor.close()
        context = dict(flag = True)
        return render_template('login.html', **context)
    else:
      context = dict(schools=schools)
      return render_template("register.html", **context)

@app.route('/get_dept', methods=["POST"])
def get_dept():
    school = request.form["school"]
    cursor = g.conn.execute("SELECT name from department_has where school_name = '%s';" % school)
    depts = []
    for dept in cursor.fetchall():
        depts.append(dept[0])
    return jsonify(depts=depts)

# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   print(name)
#   cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#   g.conn.execute(text(cmd), name1 = name, name2 = name);
#   return redirect('/')

#TODO: add some notifications!!
@app.route('/login', methods=['POST', 'GET'])
def do_admin_login():
    if request.method == 'POST':
        cursor = g.conn.execute("SELECT user_account, password FROM user_affiliation Where user_account = '%s';" % request.form['username'])
        rows = cursor.fetchall()
        if not rows:
          flash("No such account exisits!")
        else:
            password = rows[0][1]
            print(password)
            if password == request.form['password']:
                session['logged_in'] = True
                session['username'] = request.form['username']
            else:
                flash("Wrong password!")
        cursor.close()
        return index()
    else:
        return render_template("login.html")

@app.route('/profile_navigate')
def profile_navigate():
    query = '''SELECT * from user_affiliation where user_account = '%s'; ''' % session["username"]
    cursor = g.conn.execute(query)
    rows = cursor.fetchall()[0]
    print(rows)
    names = ["", "nickname", "birthdate", "email", "degree", "credit", "gender", "", "school", "department"]
    profile = {}
    for i in range(len(rows)):
        if i != 0 and i != 7:
            profile[names[i]] = rows[i]
    context = dict(profile=profile)
    return render_template("navigate_profile.html", **context)

@app.route('/set_profile', methods = ['POST','GET'])
def set_profile():
    if request.method =='GET':
        return render_template("set_profile.html",schools=schools)
    else:
        print("What the fuck?")
        query1 = "SELECT email FROM user_affiliation Where email='%s' and user_account!='%s';"
        cursor1 = g.conn.execute(query1 % (request.form['email'],session['username']))
        rows1 = cursor1.fetchall()
        if rows1:
            print("row is empty")
            flag = True
            context = dict(flag=flag, schools=schools)
            cursor1.close()
            return render_template("set_profile.html", **context)
        query = "UPDATE user_affiliation SET nickname=%s, birthdate=%s, email=%s, gender=%s, school_name=%s, dept_name=%s, degree=%s WHERE user_account = %s;"
        data = (request.form["nickname"], request.form["birthdate"], request.form["email"], request.form["gender"], request.form["school"], request.form["department"], request.form["degree"], session['username'])
        print("right!!!!")
        g.conn.execute(query, data)
        print("right!!!!agian!!")
        modified_flag = True
        return render_template("notification.html", modified_flag = modified_flag)

@app.route("/set_password", methods=['POST','GET'])
def set_passowrd():
    if request.method == 'POST':
        query = "UPDATE user_affiliation SET password = '%s';" % request.form["new_password"]
        g.conn.execute(query)
        session['logged_in'] = False
        return redirect("/login")
    else:
        return render_template("set_password.html")

'''Completed'''
@app.route('/setPreference', methods=['POST', 'GET'])
def set_preference():
  if request.method == 'GET':
    cursor = g.conn.execute("SELECT * FROM preference_has Where user_account = '%s';" % session['username'])
    rows = cursor.fetchall()
    preference = []
    if rows:
      preference = rows[0]
      print(preference)
    context = dict(preference = preference)
    return render_template('set_preference.html', **context)
  else:
    cursor = g.conn.execute("SELECT * FROM preference_has Where user_account = '%s';" % session['username'])
    rows = cursor.fetchall()
    data = (request.form['gender'], request.form['same_school'], request.form['rank'], session['username'])
    if rows:
      query = "UPDATE preference_has SET gender = %s, same_school=%s, rank = %s WHERE user_account = %s;"
      g.conn.execute(query, data)
    else:
      query = "INSERT INTO preference_has(gender, same_school, rank, user_account) VALUES (%s, %s, %s,%s);"
      g.conn.execute(query, data)

    cursor1 = g.conn.execute("SELECT * FROM preference_has Where user_account = '%s';" % session['username'])
    context = dict(preference=cursor1.fetchall()[0])
    return render_template('set_preference.html', **context)

@app.route('/goal')
def goal():
    cursor = g.conn.execute("SELECT * FROM set_goal Where user_account = '%s';" % session['username'])
    rows = cursor.fetchall()
    print(rows)
    goal_info = []
    for goal in rows:
        sections = []
        cursor1 = g.conn.execute("SELECT * FROM has_section WHERE user_account = '%s' and goal_id = %s;" % (session['username'], goal[0]))
        for section in cursor1.fetchall():
            sections.append((section[0], section[1]))
        info = {}
        info['id'] = goal[0]
        info['time'] = goal[2]
        info['name'] = goal[3]
        info['sections'] = sections
        goal_info.append(info)
    context = dict(goal_info = goal_info)
    return render_template('goal.html',**context)

@app.route('/delete_goal', methods=['POST'])
def delete_goal():
    cursor = g.conn.execute("SELECT * FROM match WHERE partner_1_id = %s and goal_1_id = %s or partner_2_id = %s and goal_2_id = %s;",
                   (session['username'], request.form['delete'],session['username'], request.form['delete']))
    if cursor.fetchall():
        g.conn.execute("UPDATE user_affiliation SET credit = credit - 10 WHERE user_account = '%s';" % session['username'])
    g.conn.execute("DELETE FROM match WHERE partner_1_id = %s and goal_1_id = %s or partner_2_id = %s and goal_2_id = %s;",
                   (session['username'], request.form['delete'],session['username'], request.form['delete']))
    g.conn.execute("DELETE FROM set_goal WHERE user_account = '%s' and goal_id = %s;" % (session['username'], request.form['delete']))
    return redirect("/goal")

@app.route('/create_goal', methods = ['POST', 'GET'])
def create_goal():
    if request.method == "GET":
        cursor = g.conn.execute("SELECT count(*),max(goal_id) from set_goal where user_account = '%s';" % session['username'])
        info = cursor.fetchall()
        count = info[0][0]
        max_id = 0
        if count!=0:
            max_id = info[0][1]
        print(max_id)
        session["max_id"] = max_id
        if count>=3:
            return render_template('notification.html')
        else:
            cursor = g.conn.execute("SELECT distinct test from test_section;")
            tests = []
            for test in cursor.fetchall():
                tests.append(test[0])
            context = dict(tests = tests)
            return render_template('create_goal.html', **context)
    else:
        g.conn.execute("INSERT into set_goal(user_account, goal_id, name, completed_date) values ('%s', %s, '%s', '%s');"
                       % (session["username"], session["max_id"]+1, request.form["test"], request.form["completed_date"]))
        sections = []
        key_dict = request.form.to_dict()
        print(key_dict)
        print(len(key_dict))
        for i in range((len(key_dict)-2)/2):
            sections.append((key_dict["section"+str(i+1)], key_dict["score"+str(i+1)]))
        section_name = {}
        for section in sections:
            if section[0] in section_name:
                continue
            else:
                section_name[section[0]] = 1
                g.conn.execute("INSERT into has_section(name, scores, user_account, goal_id) values('%s', %s, '%s', %s);"%
                               (section[0],section[1], session["username"], session["max_id"]+1))
        return redirect("/goal")

@app.route('/get_section', methods=["POST"])
def get_section():
    test = request.form["test"]
    cursor = g.conn.execute("SELECT section from test_section where test = '%s';" % test)
    sections = []
    for section in cursor.fetchall():
        sections.append(section[0])
    return jsonify(sections=sections)

@app.route('/get_score', methods=["POST"])
def get_score():
    test = request.form["test"]
    section = request.form["section"]
    print(test, section)
    cursor = g.conn.execute("SELECT score from test_section where test = '%s' and section = '%s';" %(test, section))
    score = cursor.fetchall()[0][0]
    return jsonify(score=score)

@app.route('/match', methods=['POST', 'GET'])
def match():
    def get_match_info():
        cursor = g.conn.execute("SELECT goal_id,name FROM set_goal Where user_account = '%s';" % session['username'])
        rows = cursor.fetchall()
        print(rows)
        match_info = {}
        for goal in rows:
            query1 = "SELECT partner_1_id, goal_1_id,time_start, time_end from match where partner_2_id=%s and goal_2_id = %s;"
            query2 = "SELECT partner_2_id, goal_2_id,time_start, time_end from match where partner_1_id=%s and goal_1_id = %s;"
            data = (session['username'], goal[0])
            cursor1= g.conn.execute(query1, data)
            rows1 = cursor1.fetchall()
            cursor2= g.conn.execute(query2, data)
            rows2 = cursor2.fetchall()
            if not rows1 and not rows2:
                match_info[(goal[0],goal[1])] = []
            elif rows1:
                match_info[(goal[0],goal[1])] = list(rows1[0])
            else:
                match_info[(goal[0],goal[1])] = list(rows2[0])

        return match_info

    if request.method == 'GET':
        context = dict(match_info = get_match_info())
        return render_template("match.html", **context)
    else:
        query = '''with gg(user_account, goal_id, name) 
        AS(select g.user_account, g.goal_id, g.name from set_goal g 
        where not exists 
        (select * from match m 
        where g.user_account = m.partner_1_id 
        and g.goal_id = m.goal_1_id 
        or g.user_account = m.partner_2_id 
        and g.goal_id = m.goal_2_id ))
        select gg.user_account, gg.goal_id from gg, set_goal g 
        where g.goal_id = %s and g.user_account = %s and gg.name=g.name and gg.user_account!=%s'''
        data = (request.form["match"], session['username'],session['username'])
        cursor = g.conn.execute(query, data)
        rows = cursor.fetchall()
        if not rows:
            context = dict(match_info=get_match_info(), match_flag=True)
            return render_template("match.html", **context)
        random.shuffle(rows)
        partner_id = rows[0][0]
        partner_goal = rows[0][1]
        start_time =  str(datetime.date.today())
        end_time =  str(datetime.date.today()+datetime.timedelta(days=7))
        query1 = '''Insert into match(partner_1_id, goal_1_id, partner_2_id,
          goal_2_id, time_start, time_end) values (%s, %s, %s, %s,%s,%s)'''
        data1 = (session['username'], request.form["match"], partner_id, partner_goal,start_time,end_time)
        g.conn.execute(query1, data1)

        return redirect("/match")

@app.route('/un_match', methods = ['POST'])
def un_match():
    query = '''DELETE from match where partner_1_id = %s and goal_1_id = %s  or 
    partner_2_id = %s  and goal_2_id = %s;'''
    data = (session['username'], request.form["un_match"], session['username'], request.form["un_match"])
    g.conn.execute(query, data)
    return redirect("/match")

@app.route('/check', methods=['POST'])
def check():
    query = '''SELECT * from user_affiliation where user_account = '%s'; ''' % request.form['check']
    cursor = g.conn.execute(query)
    rows = cursor.fetchall()[0]
    print(rows)
    names = ["", "nickname", "birthdate", "email", "degree", "credit", "gender","", "school", "department"]
    profile = {}
    for i in range(len(rows)):
        if i!= 0 and i!=7:
            profile[names[i]] = rows[i]
    context = dict(profile = profile)
    return render_template("check.html", **context)

@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        cursor = g.conn.execute("SELECT account, password FROM admin Where account = '%s';" % request.form['username'])
        rows = cursor.fetchall()
        if not rows:
          print("No such account exisits!")
        else:
            password = rows[0][1]
            print(password)
            if password == request.form['password']:
                session['logged_in'] = True
                session['admin'] = True
                session['username'] = request.form['username']
                cursor.close()
                return render_template("admin.html")
            else:
                flash("Wrong password!")
        return redirect("/login")
    else:
        return render_template("login.html")
@app.route('/un_match_admin', methods=['POST'])
def un_match_admin():
    query = '''DELETE from match where partner_1_id = %s and goal_1_id = %s and partner_2_id = %s
        and goal_2_id = %s or partner_1_id = %s and goal_1_id = %s and
        partner_2_id = %s  and goal_2_id = %s;'''
    data = (request.form['user1'], request.form['goal1'],request.form['user2'], request.form['goal2'],request.form['user2'], request.form['goal2'],request.form['user1'], request.form['goal1'], )
    g.conn.execute(query, data)
    return render_template("admin.html")


@app.route('/get_matches', methods=['POST'])
def get_matches():
    query = '''SELECT * from match where partner_1_id = %s and partner_2_id = %s
            or partner_1_id = %s and partner_2_id = %s;'''
    data = (request.form["user1"], request.form["user2"],request.form["user2"], request.form["user1"])
    cursor = g.conn.execute(query, data)
    rows = cursor.fetchall()
    if not rows:
        flag = True
        return render_template("admin.html", flag = flag)
    else:
        return render_template("admin.html", matches = rows)

@app.route('/update_credit', methods=['POST'])
def update_credit():
    query='''UPDATE  user_affiliation set credit= %s where user_account = %s;'''
    data = (request.form['credit'], request.form['user_account'])
    g.conn.execute(query, data)
    return render_template("admin.html")

'''Completed'''
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['admin'] = False
    return render_template('login.html')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.secret_key = os.urandom(12)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()