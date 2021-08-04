"""
Routes and views for the application.
"""

from datetime import datetime

from flask import render_template, url_for, flash, redirect, request

from proto1 import app

from proto1.forms import RegistrationForm, LoginForm, UploadForm, ProjectForm, ExportForm, EditForm

from proto1.models import Graph, User, Create_Connection

from proto1.api import download, assign, create, version_control, overwrite, delete, version



graph = Graph()
graph.Create_Graph()
conn = Create_Connection()

user = User()

@app.route('/',methods=['GET','POST'])
def login():
    
    form = LoginForm()
    global Check
    Check = False
    if request.method == "POST":
        password = user.password + form.username.data +"'"
        try:
            verification = user.get_record(password)[0][0]
        except:
            verification = False
            flash(f'The username you entered is incorrect, please try again', 'danger')
        if verification == form.password.data:
            flash(f'You have been logged in!', 'success')
            Check = True

            return redirect('/dashboard')
        elif verification:
            flash(f'The password you entered is incorrect, please try again', 'danger')

    return render_template('index.html', title='Login', form=form)


@app.route("/register",methods=['GET','POST'])
def register():

    form = RegistrationForm()
    if request.method == "POST":   
        length = len(form.password.data)
        if (form.password.data == form.confirm_password.data) and (length >= 8):
            flash(f'Account created for {form.username.data}!', 'success')
            user.username = form.username.data
            user.id = 2
            user.add(user.insert,(user.id, user.username, form.password.data))
            return redirect('/')
        elif length < 8:
            flash(f'Password is too short, please try again','danger')
        else:
            flash(f'Passwords do not match, please try again','danger')
    return render_template('register.html', title = 'Register', form=form)


@app.route("/dashboard",methods=['GET','POST'])
def dashboard():

    form = ProjectForm()
    if Check:
        return render_template('dashboard.html', title = 'Dashboard', form=form)
    else:
        return redirect('/')

@app.route("/import_doc",methods=['GET','POST'])
def import_doc():

    form=UploadForm()
    if request.method == "POST":
        v = 5 #version()
        try:
            method = form.method.data
            if method == 'Delete Content':
                delete(v)
                flash(f'Content deleted!', 'success')
            elif method == 'Overwrite':
                overwrite()
            elif method == 'New Version':
                version_control(user.id)
            download(form.file.data)
            assign(v)
            graph.Create_Graph()
            flash(f'Upload complete!', 'success')
            return redirect('/storyboard_view')
        except:
            flash(f'File not found', 'danger')

    #display what's downloaded to screen

    if Check:
        return render_template('import_doc.html', 
                               title = 'Import', 
                               form=form)
    else:
        return redirect('/')


@app.route('/storyboard_view',methods=['GET','POST'])
def storyboard_view():
    form=EditForm()
    if request.method == "POST":
        data = []
        for key,value in form.data.items():
            data.append(value)

        conn.update('Blocks',data)
        graph.Create_Graph()
        return redirect('/storyboard_view')

    if Check:
        return render_template(
            'storyboard_view.html',
            title='Storyboard View', 
            Edges = graph.edges, 
            form=form)
    else:
        return redirect('/')
    

@app.route("/map")
def map():

    if Check:
        return render_template('map.html', title = 'Map', Edges=graph.edges)
    else:
        return redirect('/')

@app.route("/export", methods=['GET','POST'])
def export():

    form=ExportForm()
    if request.method == "POST":
        create(graph.Blocks,graph.edges)
        flash(f'Export complete! Please check your google drive', 'success')
        return redirect('/storyboard_view')
    if Check:
        return render_template('export.html', 
                               title = 'Export', 
                               form=form)
    else:
        return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/stream')
def stream():
    
    if Check:
        return render_template(
            'stream.html',
            title='Stream View', 
            Blocks = graph.Blocks,
            year=datetime.now().year,
        )
    else:
        return redirect('/')
