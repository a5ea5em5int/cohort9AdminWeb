from flask import Flask, render_template , request,flash,redirect,url_for, session
import sqlite3 as sql
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "79ee2819cf0d1c205299496cfa748c3c"  # hello or some word
upload_dir="static/images"
app.config['uploadDir'] = upload_dir
pathpic= "static/pictures"
app.config['uploadPic'] = pathpic

def connectDB():
    conn = sql.connect("users.db")
    conn.row_factory= sql.Row # returns resultset as dictionary
    return conn



@app.route("/")
@app.route("/login", methods=["GET","POST"])
def loginUser():
    if request.method == "GET":
        return render_template("login.html")
    else:
        useremail = request.form['email'] # form data by POSt method
        userpwd = request.form['password'] # form data by POSt method
        with connectDB() as conn:
            cursor = conn.cursor()
            cursor.execute("select password,filename,role from user where email=?",(useremail,))
            row = cursor.fetchone()
            if row==None: 
                flash("User email does not exist","warning")
                return redirect(url_for("loginUser"))
            else:
                if row['password'] == userpwd:
                    flash("welcome user ","success")
                    session['email']= useremail
                    session['filename']=row['filename']

                    role = row['role']
                    session['role']=role
                    print(f" role is {role}")
                    if role=="admin":
                        return render_template("aboutus.html")
                    elif role=="user":
                        return redirect(url_for("showProducts"))
                else:
                    flash("wrong password . Try again!","warning")
                    return redirect(url_for("loginUser"))


                




@app.route("/users")
def list_users():
    users = ["Aung Aung","Thiha","Maysi","Mie Mie"]
    return render_template("users.html",usrs = users)

@app.route("/register",methods = ["GET","POST"])
def registerUser():
    if request.method == "GET":
        return render_template("register.html",title="Register User")
    else:
        username = request.form['name'] # accessing data by Post method
        useremail = request.form['email']
        userpwd = request.form['password']
        imgfile = request.files['profile'] # file dictonary
        if username == "" or len(username)<8 :
            flash("Username must not be empty or at least 8 characters","warning")
            return redirect(url_for("registerUser"))
        elif  imgfile.filename == "":
            flash("choose profile picture","info")
            return redirect(url_for("registerUser"))
        else:
            with connectDB() as conn:
                try:
                    filename_form = secure_filename(imgfile.filename)
                    imgfile.save(os.path.join( app.config['uploadDir'],filename_form ))

                    cur = conn.cursor()
                    cur.execute("insert into user (uname, email, password,filename) values (?,?,?,?)",(username, useremail, userpwd,filename_form))
                                       
                    flash("Register Success", "success")
                

                except Exception as e:
                    print(e)
            
        return redirect(url_for("loginUser"))


@app.route("/something")
def aboutus():
    users=[ {"name":" Daw Aye Aye","age":45,"job":"teacher"},
     {"name":"U Tun","age":35,"job":"Manager"},
      {"name":" Daw Seint Seint","age":40,"job":"Director"},
      {"name":"U Ko Ko","age":25,"job":"Programmer"},
       {"name":"Daw Thinzar","age":28,"job":"software engineer"}]
    return render_template("aboutus.html",title="About us",emps=users)

@app.route("/logout")
def logout_user():
    if 'email' in session:
        session.pop("email",None)
        session.pop("filename",None)
        session.pop("role",None)
        session.pop("cart",None)
    return redirect(url_for("loginUser"))




#Product related codes
@app.route("/products/new",methods=["GET","POST"])
def add_product():
    if request.method == "GET":
        return render_template("product.html")
    else:
        pname = request.form['name']
        price = request.form['price']
        print(type(price))
        
       
        category = request.form['category']
        p_pic =request.files['filename']  # img object
        if pname == "" or len(pname)<6:
            flash("product name should not be empty or at least 6 characters","warning")
            return redirect(url_for("add_product"))
        elif price == "":            
            flash("product price should be filled","warning")
            return redirect(url_for("add_product"))
            
        elif p_pic.filename == "":
            flash("product picture should be choosen","warning")
            return redirect(url_for("add_product"))
        else:
            pic_filename =secure_filename(p_pic.filename)
            p_pic.save(os.path.join(app.config['uploadPic'],pic_filename)) #save imaged into local server
            with connectDB() as conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("insert into product (name,price,category,filepath) values (?,?,?,?) ",(pname,price,category,pic_filename))
                    flash("product inserted","info")
                    return redirect(url_for("showProducts"))

                except Exception as err:
                    print(f' error is {err}')
            return "error "

@app.route("/products")
def showProducts():
    with connectDB() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("select * from product").fetchall()
        if 'role' in session:
            rolecarried = session['role']
            if rolecarried=="user":
                return render_template("user_products.html",products = rows, title="product list")

            else:
                return render_template("products.html",records = rows, title="product list")

            
@app.route("/deleteProduct/<int:id>")
def delete_product(id):
    with connectDB() as conn:
        try:
            cur = conn.cursor()
            cur.execute("delete from product where id=?",(id,))
            return redirect(url_for("showProducts"))
        except Exception as err:
            print(f" exception occurs {err}")

@app.route("/updateProduct/<int:id>")
def update_products(id):
    with connectDB() as conn:
        try:
            cur = conn.cursor()
            # Retrieving old product info from table
            row = cur.execute("select * from product where id=?" ,(id,)).fetchone()
            return render_template("update_product.html", data = row, title= "Update Product Form")



        except Exception as exp:
            print(f"exception occurs {exp}")

@app.route("/products/update",methods=["POST"])
def update_product_db():
    product_id = request.form['pd_id']
    product_name = request.form['name']
    product_price = request.form['price']
    product_category = request.form['category']
    product_file = request.files['filename']
    pfile_name = secure_filename(product_file.filename)
    #save image to local file system
    product_file.save(os.path.join(app.config['uploadPic'],pfile_name))
    # save update value to table 
    with connectDB() as conn:
        try:
            cur = conn.cursor()
            cur.execute("update product set name=?, price=?, category=?, filepath=? where id=?",(product_name,product_price,product_category,pfile_name,product_id))
            return redirect(url_for("showProducts"))
        except Exception as err:
            print(f"exception occurs {err}")



@app.route("/addTocart/<id>")
def add_to_cart(id):
    print(f"id data type is {type(id)} {id}")
    if 'cart' in session:  # check whether key cart is in session 
        basket = session['cart']       
           
        if id in basket:
            qty = basket[id]
            qty = qty+1
            basket[id] = qty
            
        else:
            print(" in else block new item ")
            basket[id]=1
        for k,v in basket.items():
            print(f" id= {k} =>  {v}")
        session['cart']= basket
        return redirect(url_for("showProducts"))

         
    else:
        basket={}
        basket[id]=1 #product id is key and qty is value in basket
        session['cart']=basket
        return redirect(url_for("showProducts"))


    
@app.route("/viewCart")
def view_cart():
    basket = session['cart']
    data_list=[]
    with connectDB() as conn:
        cur = conn.cursor()
        for id,qty in basket.items():
            prd = cur.execute("select * from product where id=?",(id,)).fetchone()
            data_list.append([prd['id'],prd['name'],prd['price'],prd['category'],qty])
        




    return render_template("cart.html", basket= data_list)




if __name__ == "__main__":
    app.run(debug=True)