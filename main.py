from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from query_module import query_from_API, reorder_bydate, reorder_bycitations
import random
import pymongo
import bcrypt
from database_user import PaperSearchForm

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://coen6313:irank@coen6313irank.xbzvo.mongodb.net/"
                             "myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('paper_search')
userinfo = db.userinfo
paper_db = db.paper_db
app.secret_key = "testing_coen6313"


# @app.route('/')
# def hello_world():
#     return 'hello, welcome to iRanking system of COEN 6313'


# assign URLs to have a particular route
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    # if "email" in session:
    #     return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        userid = request.form.get("userid")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        userid_found = userinfo.find_one({"userid": userid})
        user_found = userinfo.find_one({"name": user})
        email_found = userinfo.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if userid:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            # hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            # assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'user_id': userid, 'password': hashed}
            # insert it in the record collection
            userinfo.insert_one(user_input)

            # find the new created account and its email
            user_data = userinfo.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = userinfo.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        return redirect(url_for("search_welcome"))
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search_welcome():
    if "email" in session:
        email = session["email"]
        search = PaperSearchForm(request.form)
        if request.method == 'POST':
            return search_results(search)
        return render_template('logged_in.html', form=search, email=email)


@app.route('/search/results', methods=['GET', 'POST'])
def search_results(search):
    results = []
    search_string = search.data['search']
    search_number = search.data['number']
    if search_string == '':
        return redirect(url_for("search_welcome"))
    if search_number == '':
        search_number = 10
    search_number = int(search_number)
    if search.data['select'] == 'NormalSearch':
        # search_string = search_string.split('&')
        return redirect(url_for("query_result_req", keyword=search_string, number=search_number))
    elif search.data['select'] == 'by_Date':
        search_number = int(search_number)
        return redirect(url_for("query_result_req_bydate", keyword=search_string, number=search_number))
    elif search.data['select'] == 'by_Citations':
        return redirect(url_for("query_result_req_bycitations", keyword=search_string, number=search_number))
    elif search.data['select'] == 'by_Trend':
        return
        # return redirect(url_for("query_result_req_bycitations", keyword=search_string, number=search_number))
    elif search.data['select'] == 'by_s2Model':
        return
        # return redirect(url_for("query_result_req_bycitations", keyword=search_string, number=search_number))


@app.route('/search/<string:keyword>&<string:number>', methods=['GET', 'POST'])
def query_result_req(keyword, number):
    """
    :param keyword: keyword you wanna search like "cloud computing"
    :param number: how many papers you wanna return with the highest rank
    :return: Json list
    """
    '''when debug = True, will not call s2search module, which includes the whole machine learning predict model and 
    complex env requirements, only feed an example of paper dict that for debug web funtion.'''
    paper_list = query_from_API(keyword, number)

    # paper_list = random.shuffle(paper_list)
    return jsonify(paper_list)


@app.route('/search/<string:keyword>&<string:number>/by_date', methods=['GET', 'POST'])
def query_result_req_bydate(keyword, number):
    """
    :param keyword: keyword you wanna search like "cloud computing"
    :param number: how many papers you wanna return with the highest rank
    :return: Json list
    """
    '''when debug = True, will not call s2search module, which includes the whole machine learning predict model and 
    complex env requirements, only feed an example of paper dict that for debug web funtion.'''
    paper_list = query_from_API(keyword, number)
    paper_list = reorder_bydate(paper_list)

    return jsonify(paper_list)


@app.route('/search/<string:keyword>&<string:number>/by_citations', methods=['GET', 'POST'])
def query_result_req_bycitations(keyword, number):
    """
    :param keyword: keyword you wanna search like "cloud computing"
    :param number: how many papers you wanna return with the highest rank
    :return: Json list
    """
    '''when debug = True, will not call s2search module, which includes the whole machine learning predict model and 
    complex env requirements, only feed an example of paper dict that for debug web funtion.'''
    paper_list = query_from_API(keyword, number)
    paper_list = reorder_bycitations(paper_list)

    return jsonify(paper_list)


# @app.route('/view/paper_history')
# def show_mangodb():
#     # return render_template('papermeta.html', paper_db=paper_db)
#     cur = paper_db.archive.find({}, {'paper_id': 1, 'title': 1, 'author': 1, 'abstract': 1, 'venue': 1, 'year': 1,
#                                      'citations': 1, 'url': 1})
#     print(list(cur))
#     return render_template('papermeta.html', cur=list(cur))


if __name__ == '__main__':
    app.run(debug=True)
