# main.py

from app import app
from db_setup import init_db, db_session
from forms import SearchForm, EditForm
from flask import flash, render_template, request, redirect
from models import Userdata
from tables import Results

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    search = SearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search)

@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search_string:
        
        if search.data['select'] == 'Username':
            qry = db_session.query(Userdata).filter(
                Userdata.username.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'User_id':
            qry = db_session.query(Userdata).filter(
                Userdata.user_id.contains(search_string))
            results = qry.all()
        else:
            qry = db_session.query(Userdata)
            results = qry.all()
    else:
        qry = db_session.query(Userdata)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():

    form = EditForm(request.form)

    if request.method == 'POST' and form.validate():
        userdata = Userdata()
        save_changes(userdata, form, new=True)
        flash('User created successfully!')
        return redirect('/')

    return render_template('new_user.html', form=form)

@app.route('/item/<int:id>', methods=['GET', 'POST'])
def edit(id):

    qry = db_session.query(Userdata).filter(
                Userdata.user_id==id)
    userdata = qry.first()

    if userdata:
        form = EditForm(formdata=request.form, obj=userdata)
        if request.method == 'POST' and form.validate():
            # save edits
            save_changes(userdata, form)
            flash('User updated successfully!')
            return redirect('/')
        return render_template('edit_user.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):

    qry = db_session.query(Userdata).filter(
        Userdata.user_id==id)
    userdata = qry.first()

    if userdata:
        form = EditForm(formdata=request.form, obj=userdata)
        if request.method == 'POST' and form.validate():
            db_session.delete(userdata)
            db_session.commit()

            flash('User deleted successfully!')
            return redirect('/')
        return render_template('delete_user.html', form=form)
    else:
        return 'Error deleting #{id}'.format(id=id)

def save_changes(userdata, form, new=False):

    userdata.username = form.username.data
    userdata.password = form.password.data

    if new:

        db_session.add(userdata)

    db_session.commit()
