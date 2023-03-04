from flask import Flask,render_template,flash,redirect,url_for,session,logging,request

from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
import time

from flask import g, request, redirect, url_for



app=Flask(__name__)
app.secret_key="real-app"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="real-app"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)
@app.route("/")
def home():
    return render_template("home.html")
#Login decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapınız.","danger")
            return redirect(url_for("login"))
        
    return decorated_function 
#Register Form

class RegisterForm(Form):
    name=StringField("Name", validators=[validators.Length(min=3, max=25)])
    email=StringField("Email",validators=[validators.Email("Please enter a valid email")])
    password=PasswordField("Password" , validators=[validators.DataRequired(message="Password is required"),validators.EqualTo(fieldname="confirm", message="Your password does not match")])
    confirm=PasswordField("Confirm password")


#Register Page
@app.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm(request.form)
    
    if request.method=="POST" and form.validate():
        name=form.name.data
        
        email=form.email.data
        password= sha256_crypt.encrypt(form.password.data)
        
        cursor=mysql.connection.cursor()
        
        sorgu="Insert into users(name,email,password) VALUES(%s,%s,%s)" 
        
        cursor.execute(sorgu,(name,email,password))
        mysql.connection.commit()
        cursor.close()
        flash("You have successfully registered","success")
        return redirect(url_for("home"))
    
    else:
         return  render_template("register.html",form=form)

#Login Page
@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        email=form.email.data
        password_entered=form.password.data
        cursor=mysql.connection.cursor()
        sorgu="Select * From users where email =%s"
        result=cursor.execute(sorgu,(email,))
        if result > 0:
            data=cursor.fetchone()
            real_password=data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("You have succesfully in","success")
                
                
                session["logged_in"]=True
                session["email"]=email
                
                return redirect(url_for("home"))
            else:
                flash("Your password is not correct","danger")
                return redirect(url_for("login"))
        else:
            flash("User can not found.","danger")
            return redirect(url_for("login"))
            
    return render_template("login.html",form=form)

#Logout
@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    session.clear()
    return render_template("home.html")


#Login Form
class LoginForm(Form):
    email=StringField("Email Address")
    password=PasswordField("Password")
    
#Dashboard Movie
"""
@app.route("/dashboardmovie",methods=["GET","POST"])
@login_required
def dashboardmovie():
    
    form=AddMovie(request.form)
    cursor=mysql.connection.cursor()
    movie=form.movie.data
    sorgu="Select * from movies where movie=%s"
    result =cursor.execute(sorgu,(movie,))
    if result > 0:
        movies=cursor.fetchall()
        return render_template("dashboardmovie.html",movies=movies)
    
    return render_template("dashboardmovie.html")
"""
@app.route("/movies")
def movies():
    cursor=mysql.connection.cursor()
    sorgu="Select * from movies"
    result=cursor.execute(sorgu)
    if result>0:
        movies=cursor.fetchall()
        return render_template("movies.html",movies=movies)
    return render_template("movies.html")
    
    
    
    
    
    
    
@app.route("/addmoviepage",methods=["GET","POST"])
@login_required
def addmoviepage():
    form=AddMovie(request.form)
    if request.method=="POST" and form.validate():
        movie=form.movie.data
        category=form.category.data
        year=form.year.data
        producer=form.producer.data
        cursor=mysql.connection.cursor()
        sorgu="Insert into movies (movie,year,category,producer) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(movie,year,category,producer))
        mysql.connection.commit()
        cursor.close()
        flash("You have add the movie","success")
        return redirect(url_for("addmoviepage"))
    
    
    return render_template("addmoviepage.html",form=form)

class AddMovie(Form):
    movie=StringField(validators=[validators.Length(min=2, max=25)])
    category=StringField(validators=[validators.Length(min=2, max=25)])
    year=StringField(validators=[validators.Length(min=4,max=4)])
    producer=StringField(validators=[validators.Length(min=2, max=25)])
    
    
    
#Recipe
@app.route("/recipes")
def recipes():
    cursor=mysql.connection.cursor()
    sorgu="Select * from recipes"
    result=cursor.execute(sorgu)
    if result > 0:
        recipes=cursor.fetchall()
        return render_template("recipes.html",recipes=recipes)
    return render_template("recipes.html")


#Add recipe

@app.route("/addrecipepage",methods=["GET","POST"])
@login_required
def addrecipepage():
    form=RecipeForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        category=form.category.data
        ingredients=form.ingredients.data 
        preparation=form.preparation.data
        cursor=mysql.connection.cursor()
        sorgu="Insert into recipes (name,category,ingredients,preparation) VALUES (%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,category,ingredients,preparation))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("recipes",form=form))   
    
    return render_template("addrecipepage.html",form=form)


#Recipe Form
class RecipeForm(Form):
    name=StringField(validators=[validators.Length(min=5)])
    category=StringField(validators=[validators.Length(min=5)])
    ingredients=StringField(validators=[validators.Length(min=3)])
    preparation=StringField(validators=[validators.Length(min=10)])
"""
#dashboard Recipe
@app.route("/dashboardrecipe")
def dashboardrecipe():
    return render_template("dashboardrecipe.html")
"""

#todo 
@app.route("/todos",methods=["GET","POST"])
@login_required
def todos():
    cursor=mysql.connection.cursor()
    sorgu="Select * from todos"
    result=cursor.execute(sorgu)
    if result>0:
        todos=cursor.fetchall()
        return render_template("todos.html",todos=todos)
    
    return render_template("todos.html")

#Add Todo

@app.route("/addtodopage",methods=["GET","POST"])
@login_required
def addtodopage():
    form=TodoForm(request.form)
    if request.method=="POST":
        todo=form.todo.data
        deadline=form.deadline.data
        
        
        cursor=mysql.connection.cursor()
        sorgu="Insert into todos(todo,deadline) VALUES(%s,%s)"
        cursor.execute(sorgu,(todo,deadline))
        mysql.connection.commit()
        cursor.close()
        flash("You have add.","success")
        return redirect(url_for("todos"))
    
    return render_template("addtodopage.html",form=form)

"""
#dashboard todo
@app.route("/dashboardtodo")
def dashboardtodo():
    return render_template("dashboardtodo.html")
    """


#todo form
class TodoForm(Form):
    todo=StringField("Todo", validators=[validators.Length(min=5)])
    deadline=StringField("Deadline",validators=[validators.Length(min=4,max=20)])
    
    


    
    
#delete movie
@app.route("/delete/<string:id>")
@login_required
def deletemovie(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from movies where id=%s"
    result=cursor.execute(sorgu,(id))
    if result>0:
        sorgu2="Delete  from movies where id=%s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("movies"))
        
    else:
        flash("You can not delete the movie","danger")
        return redirect(url_for("home"))
    
    
    
    
#delete recipe
@app.route("/deleterecipe/<string:id>")
@login_required
def deleterecipe(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from recipes where id=%s"
    result=cursor.execute(sorgu,(id,))
    if result>0:
        sorgu2="Delete from recipes where id=%s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("recipes"))
    else:
        flash("You can not delete the recipe","danger")
        return redirect(url_for("home"))
    
#delete todo
@app.route("/deletetodo/<string:id>")
@login_required
def deletetodo(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from todos where id=%s"
    result=cursor.execute(sorgu,(id))
    if result>0:
        sorgu2="Delete from todos where id=%s"
        cursor.execute(sorgu2,(id))
        mysql.connection.commit()
        return redirect(url_for("todos"))
    else:
        flash("You can not delete the todo item.")
        return redirect(url_for("home"))    

#edit movie
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def editmovie(id):
    if request.method=="GET":
        cursor=mysql.connection.cursor()
        sorgu="Select * from movies where id=%s"
        result=cursor.execute(sorgu,(id,))
        
        if result==0:
            flash("You can not edit the movie.")
            return redirect(url_for("home"))
        else:
            movie=cursor.fetchone()
            form=AddMovie()
            form.movie.data=movie["movie"]
            form.category.data=movie["category"]
            form.year.data=movie["year"]
            form.producer.data=movie["producer"]
            return render_template("movieupdate.html",form=form)
        
    else:
        form=AddMovie(request.form)
        newMovie=form.movie.data
        newCategory=form.category.data
        newYear=form.year.data
        newProducer=form.producer.data
        sorgu2="Update movies set movie=%s,category=%s,year=%s,producer=%s where id=%s"
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newMovie,newCategory,newYear,newProducer,id))
        mysql.connection.commit()
        flash("You successfully updated.","success")
        return redirect(url_for("movies"))
        
#edit recipe
@app.route("/editrecipe/<string:id>",methods=["GET","POST"])     
@login_required
def editrecipe(id):
    if request.method=="GET":
        cursor=mysql.connection.cursor()
        sorgu="Select * from recipes where id=%s"
        result =cursor.execute(sorgu,(id))
        if result==0:
            flash("You can not delete the recipe")
            return redirect(url_for("recipes"))
        else:
            recipe=cursor.fetchone()
            form=RecipeForm()
            form.name.data=recipe["name"]
            form.category.data=recipe["category"]
            form.ingredients.data=recipe["ingredients"]
            form.preparation.data=recipe["preparation"]
            return render_template("recipeupdate.html",form=form)
        
    else:
        form=RecipeForm(request.form)
        newName=form.name.data
        newCategory=form.category.data
        newIngredients=form.ingredients.data
        newPreparation=form.preparation.data
        
        sorgu2="Update recipes set name=%s,category=%s,ingredients=%s,preparation=%s where id=%s "
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newName,newCategory,newIngredients,newPreparation,id))
        mysql.connection.commit()
        flash("You have successfully updated ","success")
        return redirect(url_for("recipes"))
   
#edit todo
@app.route("/edittodo/<string:id>",methods=["GET","POST"])   
@login_required
def edittodo(id):
    if request.method=="GET":
        cursor=mysql.connection.cursor()
        sorgu="Select * from todos where id=%s"
        result=cursor.execute(sorgu,(id))
        if result==0:
            flash("You can not edit the todo item","danger")
            return redirect(url_for("todos"))
        
        else:
            todo=cursor.fetchone()
            form=TodoForm()
            form.todo.data=todo["todo"]
            form.deadline.data=todo["deadline"]
            return render_template("todoupdate.html",form=form)
    
    else:
        form=TodoForm(request.form)
        newTodo=form.todo.data
        newDeadline=form.deadline.data 
        sorgu2="Update todos set todo=%s,deadline=%s where id=%s"
        cursor=mysql.connection.cursor()
        cursor.execute(sorgu2,(newTodo,newDeadline,id))
        mysql.connection.commit()
        flash("You have successfully updated","success")
        return redirect(url_for("todos"))
        
                 
            
#check todo
@app.route("/checktodo/<string:id>")
@login_required
def checktodo(id):
    
        cursor=mysql.connection.cursor()
        sorgu="Select * from todos where id=%s"
        result=cursor.execute(sorgu,(id))
        if result>0:
            sorgu2="Delete  from todos where id=%s"
            cursor.execute(sorgu2,(id))
            mysql.connection.commit()
            flash("You have successfully done this todo item.","success")
            return redirect(url_for("todos"))
        else:
            flash("You can not check this todo item")
            return render_template("todos.html")
    
       

#search movie
@app.route("/searchmovie", methods=["GET","POST"])
@login_required
def searchmovie():
    form=AddMovie(request.form)
    if request.method=="POST":
        
        keywoard=request.form.get("keywoard")
        cursor=mysql.connection.cursor()
        sorgu="Select * from movies where movie like '%"+keywoard+"%'"
        result=cursor.execute(sorgu)
        if result==0:
            flash("There is no movie like this. ","danger")
            return redirect(url_for("movies"))
        else:
            movies=cursor.fetchall()
            return render_template("movies.html",movies=movies)
        
    else:
         flash("You have to login","danger")
         return redirect(url_for("home"))
    
#search recipe
@app.route("/searchrecipe",methods=["GET","POST"])
@login_required
def searchrecipe():
    form=RecipeForm(request.form)
    if request.method=="POST":
        
        keywoard=request.form.get("keywoard")
        cursor=mysql.connection.cursor()
        sorgu="Select * from recipes where name like '%"+keywoard+"%'"
        result=cursor.execute(sorgu)
        if result ==0 :
            flash("There is no recipe like this.","danger")
            return redirect(url_for("recipes"))
        else:
            recipes=cursor.fetchall()
            return render_template("recipes.html",recipes=recipes)
    else:
        flash("You have to login","danger")
        return redirect(url_for("home"))
        
    
    
#search todo
@app.route("/searchtodo",methods=["GET","POST"])
@login_required
def searchtodo():
    form=TodoForm(request.form)
    if request.method=="POST":
        keywoard=request.form.get("keywoard")
        cursor=mysql.connection.cursor()
        sorgu="Select * from todos where todo like '%"+keywoard+"%'"
        result=cursor.execute(sorgu)
        if result==0:
            flash("There is no todo item like this","danger")
            return redirect(url_for("todos"))
        else:
            todos=cursor.fetchall()
            return render_template("todos.html",todos=todos)
        
        
    else:
        
        flash("You have to login","danger")
        return redirect(url_for("home"))
    
    
#homepage
@app.route("/homepage")
def homepage():
    return render_template("homepage.html")
    
                
if __name__=="__main__":
    app.run(debug=True,port=5001)