from flask import render_template,Flask,request,redirect
from flask_login import login_user,current_user,login_required,LoginManager,UserMixin,logout_user
import CommonConstants
import ConfigurationConstants
from utilities import AuthUtil, DBUtil, CommonUtil
from Handlers import DBHandler
from objects import obj

app = Flask(__name__)
app.config['SECRET_KEY'] = "RANDOM_STRING"
loginManager = LoginManager(app)
loginManager.login_view = 'loginPage'

@app.route("/")
def index():
    #DBHandler.reinitializeDB()
    return render_template('index.html',home="/")

@app.route("/login-page")
def loginPage():
    return render_template('login.html',error="",home="/")

@app.route("/register-page",methods=['GET'])
def register():
    params = request.args
    return render_template('register.html',error="",type=params.get('type'),home="/")

@app.route("/register",methods=['POST'])
def registerUser():
    data = {"username":request.form.get("username", "-1"),"password":request.form.get('password', "-1"),"address":request.form.get('address', "-1"),"mobile_number":request.form.get('mobile', "-1"),"store_name":request.form.get('store',"-1"),"type":request.form.get('type',"-1")}
    error = DBUtil.checkPrimaryData(data,[CommonConstants.USERS,CommonConstants.STORES])
    if error is None:
        userId = DBUtil.addUser(data["username"],data['password'],data['address'],data['mobile_number'],data['type'])
        if(userId != "-1"):
            if(CommonUtil.getRole(data['type']) == 1):
                if DBUtil.addStore(data["store_name"],userId) != "-1":
                    return render_template('login.html',error="Registration Successfull, Kindly login !",home="/")
                else:
                    DBUtil.removeUser(userId,False)
                    return render_template('register.html',error="error occured while creating store, Contact support",type=data['type'],home="/")
            else:
                return render_template('login.html',error="Registration Successfull, Kindly login !",home="/")
        else:
            return render_template('register.html',error="error occured while creating user, Contact support",type=data['type'],home="/")
    else:
        return render_template('register.html',error=error,type=data['type'],home="/")

@app.route("/validateUser", methods=['POST'])
def validate():
    username = request.form['username']
    password = request.form['password']
    res = AuthUtil.validateUser(username,password)
    if(res["status"] == "SUCCESS"):
        user = obj.User(id=res["data"][0][0],username=username, data = res["data"])
        login_user(user)
        return redirect(f"user/{username}")
    else:
        return render_template('login.html',error=res["message"],home="/")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("login-page")

@app.route("/user/<username>")
@login_required
def homePage(username):
    if(current_user.getUsername() == username):
        if current_user.get_role() == 1:
            stat = DBUtil.getBasicStats(DBUtil.getStore(current_user.get_userId())[0])
            return render_template('homepage.html',type=current_user.get_role(),route='home',username=username,units=DBUtil.getAllUnits(),categories=DBUtil.getAllCategories(),home=f"/user/{username}", productsVsCount=stat["productsVsCount"],  categoriesVsCount=stat["categoriesVsCount"], productVsSelling=stat["productVsSelling"], categoriesVsSelling=stat["categoriesVsSelling"],totalRevenue=stat["totalRevenue"],totalSelling=stat["totalSelling"], totalCustomers=stat["totalCustomers"], totalProducts=stat["totalProducts"], totalCategories=stat["totalCategories"])
        else:
            searchStr = request.args.get('k')
            sortType = request.args.get('sortType')
            sortValue = request.args.get('value')
            return render_template("listItems.html",products=DBUtil.getList('products','',searchStr,sortType,sortValue),type=current_user.get_role(),home=f"/user/{username}",username=username,page="Home",units=DBUtil.getAllUnits(),categories=DBUtil.getAllCategories())
    return  redirect("/logout")


@loginManager.user_loader
def load_user(userid):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.USERS,'clause':DBUtil.getCriteria([CommonConstants.USER_ID],[userid],[ConfigurationConstants.OPERATORS[1]],"(1)")})
    data = DBHandler.getData(query)
    user = obj.User(id=userid, username=data[0][1], data=data)
    return user


@app.route("/addData", methods=['POST'])
@login_required
def addData():
    data = request.get_json()
    response = {}
    type = data.get("type")
    statusCode = "-1"
    if current_user.get_role() == 1:
        if type == "product":
            statusCode = DBUtil.addItem(data.get("itemName"),data.get("category"),data.get("rate"),data.get("quantity"),data.get("unit"),DBUtil.getStore(current_user.get_userId())[0])
        elif type == "category":
            statusCode = DBUtil.addCategory(data.get("categoryName"),DBUtil.getStore(current_user.get_userId())[0])
        elif type == "unit":
            statusCode = DBUtil.addUnit(data.get("unitName"),DBUtil.getStore(current_user.get_userId())[0])
    elif current_user.get_role() == 2:
        if type == "cart":
            itemId = data.get('id')
            qnty = data.get('quantity')
            leftStocks, price = DBUtil.getStockAvailable(current_user.get_userId(),itemId, qnty)
            if leftStocks >= 0:
                statusCode = DBUtil.addUserVsCart(current_user.get_userId())
                if statusCode != "-1":
                    statusCode = DBUtil.addCart(statusCode,itemId,int(qnty),price)
                    # if statusCode != "-1":
                    #     updatingColumns = [CommonConstants.QUANTITY]
                    #     values = [leftStocks]
                    #     flag = DBUtil.updateItem(itemId,updatingColumns,values)
                    #     if not flag:
                    #         statusCode = "-1"
        if statusCode == "-1":
            CommonUtil.getLogger().info("Data not added ")
            response["status"] = "failed"
        else:
            CommonUtil.getLogger().info("Data Succesfully added ")
            response["status"] = "success"
        return response
    else:
        CommonUtil.getLogger().info("Not Authorized to perform this action!")
        response["status"] = "failed"
        return response

@app.route("/deleteData", methods=['POST'])
@login_required
def deletedData():
    data = request.get_json()
    response = {}
    status = False
    type = data.get("type")
    if(type == "item"):
        status = DBUtil.deleteItem(data.get("id"))
    elif(type == "category"):
        status = DBUtil.deleteCategory(data.get("id"))
    elif(type == "cart"):
        status = DBUtil.deleteCart(data.get("itemId"),data.get("cartId"))
    if status:
        response["status"] = "success"
    else:
        response["status"] = "failed"
    return response


@app.route("/updateData", methods=['POST'])
@login_required
def updateData():
    data = request.get_json()
    response = {}
    type = data.get("type")
    status = False
    if(type == "item"):
        updatingColumns = [CommonConstants.ITEM_NAME,CommonConstants.PRICE,CommonConstants.QUANTITY,CommonConstants.UNIT,CommonConstants.CATEGORY_ID]
        values = [data.get("name"),data.get("price"),data.get("quantity"),data.get("unit"),data.get("category")]
        status = DBUtil.updateItem(data.get("id"),updatingColumns,values)
    elif(type == "category"):
        updatingColumns = [CommonConstants.CATEGORY_NAME]
        values = [data.get("name")]
        status = DBUtil.updateCategory(data.get("id"), updatingColumns, values)
    elif(type == "unit"):
        updatingColumns = [CommonConstants.UNIT_NAME]
        values = [data.get("name")]
        status = DBUtil.updateUnit(data.get("id"), updatingColumns, values)
    elif(type == "checkOut"):
        cartId = DBUtil.getCartId(current_user.get_userId())
        if(cartId != -1 ):
            status = DBUtil.checkOut(cartId,current_user.get_userId())
    if status:
        response["status"] = "success"
    else:
        response["status"] = "failed"
    return response

@app.route("/user/<username>/<type>")
@login_required
def listData(username, type):
    if(type != "cart"):
        id = DBUtil.getStore(current_user.get_userId())[0]
        searchStr = request.args.get('k')
        sortType = None
        sortValue = None
        if type == "products":
            sortType = request.args.get('sortType')
            sortValue = request.args.get('value')
        if id is not None:
            if (current_user.getUsername() == username):
                return render_template("listItems.html",products=DBUtil.getList(type,id,searchStr,sortType,sortValue),type=current_user.get_role(),home=f"/user/{username}",username=username,page=type,units=DBUtil.getAllUnits(),categories=DBUtil.getAllCategories())
            else:
                return redirect("/logout")
    else:
        id = current_user.get_userId()
        if id is not None:
            if (current_user.getUsername() == username):
                return render_template("listItems.html",products=DBUtil.getList(type,id,'',None,None),type=current_user.get_role(),home=f"/user/{username}",username=username,page=type,units={},categories={},totalAmount=DBUtil.getTotalCartAmount(id))
            else:
                return redirect("/logout")