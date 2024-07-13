import ConfigurationConstants
import CommonConstants
from utilities import CommonUtil
from Handlers import DBHandler
import json
import re
import time

logger = CommonUtil.getLogger()

def getTotalCartAmount(userId):
    query = ConfigurationConstants.TOTAL_CART_PRICE.substitute({'user_id':userId})
    data = DBHandler.getData(query)
    if data is not None and len(data) > 0:
        return data[0][0]
    else:
        return -1

def getTableColumns(table):
    data = (json.load(open(ConfigurationConstants.FILE_PATH_TO_TABLES_JSON))["tables"][table]["columns"])
    return data

def addData(table, newData):
    data = getTableColumns(table)
    str = ""
    columns = data.keys()
    newDataColumns = newData.keys()
    for key in columns:
        if key not in newDataColumns:
            CommonUtil.getLogger().error(f" column value mismatch {key}")
            return False
        if (data[key]["type"] == CommonConstants.TEXT_DATA_TYPE) or (data[key]["type"] == CommonConstants.VARCHAR_DATA_TYPE):
            str += f"'{newData[key]}',"
        else:
            str += f"{newData[key]},"
    str = str[:-1]
    return DBHandler.executeQuery(ConfigurationConstants.INSERT_TEMPLATE.substitute(
        {'values': str, 'columns': ",".join(columns), 'table_name': table}))


def removeData(table, columns, values, operators, relations):
    return DBHandler.executeQuery(ConfigurationConstants.DELETE_TEMPLATE.substitute(
        {'table_name': table, 'clause': getCriteria(columns, values, operators, relations)}))


def updateData(table, setColumns, setValues, critColumns, critValues, critOperators, critRelations):
    return DBHandler.executeQuery(ConfigurationConstants.UPDATE_TEMPLATE.substitute(
        {'table_name': table, 'clause': getCriteria(critColumns, critValues, critOperators, critRelations),
         'set_values': getSetClause(table, setColumns, setValues)}))


def getSetClause(table, setColumns, setValues):
    data = json.load(open(ConfigurationConstants.FILE_PATH_TO_TABLES_JSON))["tables"][table]["columns"]
    i = 0
    setCols = []
    for column in setColumns:
        if data[column][CommonConstants.TYPE] == CommonConstants.INTEGER_DATA_TYPE:
            setCols.append(f" {column} = {setValues[i]}")
        else:
            setCols.append(f" {column} = '{setValues[i]}'")
        i += 1
    return ",".join(setCols)


def getCriteria(columns, values, operators, relations):
    i = 0
    if (len(columns) != len(values) != len(operators)):
        raise ValueError("while creating criteria length mis-match in the given list")
    criterias = []
    for column in columns:
        operator = operators[i]
        if (operator in ConfigurationConstants.OPERATORS[4]):
            crit = f" {column} {operators[i]} ("
            for value in values:
                crit += f"'{value} ',"
            crit = crit[:-1]
            crit += ")"
        elif (operator in ConfigurationConstants.OPERATORS[5]):
            crit = f" {column} {operators[i]} '%{values[i]}%'"
        else:
            crit = f" {column} {operators[i]} '{values[i]}' "
        i += 1
        criterias.append(crit)
    return replaceCriteria(relations, criterias)


def replaceCriteria(relation, criterias):
    def replaceRelation(pattern):
        num = int(pattern.group())
        if 1 <= num <= len(criterias):
            return criterias[num - 1]
        return pattern.group()

    completeCriteria = re.sub(r'\d+', replaceRelation, relation)
    return completeCriteria


def addUser(username, password, address, mobile, role):
    userId = CommonUtil.generateRandomID()
    data = {'user_id': userId, 'username': username, 'address': address, 'mobile_number': mobile,
            'user_role': CommonUtil.getRole(role)}
    if addData(CommonConstants.USERS, data):
        data = {'user_id': userId, 'password': CommonUtil.encode(password)}
        if(addData(CommonConstants.USERVSPASSWORD, data)):
            return userId
    return "-1"

def removeUser(username, isUsername):
    return removeData(CommonConstants.USERS, [CommonConstants.USERNAME if isUsername else CommonConstants.USER_ID], [username], [ConfigurationConstants.OPERATORS[1]],"(1)")

def updateUser(userID, setColumns, setColumnValues):
    return updateData(CommonConstants.USERS, setColumns, setColumnValues, [CommonConstants.USER_ID], [userID], [ConfigurationConstants.OPERATORS[1]],"(1)")


def addItem(itemName, categoryId, price, quantity, unit, store):
    itemId = CommonUtil.generateRandomID()
    if addData(CommonConstants.ITEMS, {CommonConstants.ITEM_ID: itemId, 'item_name': itemName, 'category_id': categoryId, 'price': price, 'quantity': quantity, 'unit': unit, 'store_id': store}):
        return itemId
    return '-1'

def updateItem(itemId,setColumns, setColumnValues):
    return updateData(CommonConstants.ITEMS, setColumns, setColumnValues, [CommonConstants.ITEM_ID], [itemId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def deleteItem(itemId):
    return removeData(CommonConstants.ITEMS,[CommonConstants.ITEM_ID], [itemId], [ConfigurationConstants.OPERATORS[1]],"(1)")


def addCategory(categoryName,userId):
    cat_id = CommonUtil.generateRandomID()
    if addData(CommonConstants.CATEGORIES, {CommonConstants.CATEGORY_ID:cat_id ,'category_name':categoryName,'store_id':userId}):
        return cat_id
    return '-1'

def updateCategory(categoryId,setColumns, setColumnValues):
    return updateData(CommonConstants.CATEGORIES, setColumns, setColumnValues, [CommonConstants.CATEGORY_ID], [categoryId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def deleteCategory(categoryId):
    return removeData(CommonConstants.CATEGORIES, [CommonConstants.CATEGORY_ID], [categoryId], [ConfigurationConstants.OPERATORS[1]],"(1)")


def addStore(storeName, managerId):
    store_id = CommonUtil.generateRandomID()
    if addData(CommonConstants.STORES,{CommonConstants.STORE_ID:store_id,'store_name': storeName,'manager_id':managerId}):
        return store_id
    return '-1'

def updateStore(storeId,setColumns, setColumnValues):
    return updateData(CommonConstants.STORES, setColumns, setColumnValues, [CommonConstants.STORE_ID], [storeId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def deleteStore(storeId):
    return removeData(CommonConstants.STORES,CommonConstants.STORE_ID, [storeId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def getStore(userId):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.STORES,'clause':getCriteria([CommonConstants.MANAGER_ID],[userId],[ConfigurationConstants.OPERATORS[1]],"(1)")})
    data = DBHandler.getData(query)
    return data[0]

def addUnit(unitName,userId):
    unitId = CommonUtil.generateRandomID()
    if addData(CommonConstants.UNITS,{'unit_id':unitId,'unit_name':unitName,'store_id':userId}):
        return unitId
    return '-1'

def updateUnit(unitId,setColumns, setColumnValues):
    return updateData(CommonConstants.UNITS, setColumns, setColumnValues, [CommonConstants.UNIT_ID], [unitId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def deleteUnit(unitId):
    return removeData(CommonConstants.UNITS,[CommonConstants.UNIT_ID], [unitId], [ConfigurationConstants.OPERATORS[1]],"(1)")

def deleteCart(itemId, cartId):
    return removeData(CommonConstants.CARTS,[CommonConstants.CART_ID,CommonConstants.ITEM_ID],[cartId,itemId],[ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[1]],"(1 and 2)")

def addCart(cartId,itemId,count,price):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns': CommonConstants.ALL, 'table_name': CommonConstants.CARTS,'clause': getCriteria([CommonConstants.CART_ID,CommonConstants.ITEM_ID], [cartId,itemId],[ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[1]],"(1 and 2)")})
    data = DBHandler.getData(query)
    if data is not None and len(data) > 0:
        oldCount = int(data[0][2])
        oldTotalPrice = int(data[0][4])
        if updateData(CommonConstants.CARTS,[CommonConstants.COUNT,CommonConstants.TOTAL_PRICE],[(oldCount+count),((count * price) + oldTotalPrice)],[CommonConstants.CART_ID,CommonConstants.ITEM_ID],[cartId,itemId],[ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[1]],"(1 and 2)"):
            return cartId
        else:
            return "-1"
    elif addData(CommonConstants.CARTS,{'cart_id':cartId,'item_id':itemId,'count':count,'price': price,'total_price':price * count }):
        return cartId
    return "-1"

def addUserVsCart(userId):
    cartId = getCartId(userId)
    if cartId == -1:
        cartId = CommonUtil.generateRandomID()
        if addData(CommonConstants.CARTVSUSER,{'cart_id':cartId,'user_id':userId }):
            return cartId
    else:
        return cartId

    return "-1"


def getStoreFromItem(itemId):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns': CommonConstants.ALL, 'table_name': CommonConstants.ITEMS,'clause': getCriteria([CommonConstants.ITEM_ID], [itemId], [ConfigurationConstants.OPERATORS[1]], "(1)")})
    data = DBHandler.getData(query)
    return data[0][6]

def checkOut(cartId,userId):
    cartItems = getCart(cartId)
    flag = True
    if len(cartItems) > 0:
        for item in cartItems:
            data = {}
            data[CommonConstants.STORE_ID] = getStoreFromItem(item[1])
            data[CommonConstants.CART_ID] = cartId
            data[CommonConstants.USER_ID] = userId
            data[CommonConstants.ITEM_ID] = item[1]
            data[CommonConstants.QUANTITY] = item[2]
            data[CommonConstants.TIME_IN_MILLIS] = int(time.time() * 1000)
            data[CommonConstants.TOTAL_PRICE] = item[4]
            newCount = getLeftQuantity(userId,item[1],item[2])
            if newCount >= 0 :
                if not (addData(CommonConstants.SOLD_DATA,data) and updateData(CommonConstants.ITEMS,[CommonConstants.QUANTITY],[newCount],[CommonConstants.ITEM_ID],[item[1]],[ConfigurationConstants.OPERATORS[1]],"(1)")):
                    flag = False
                    break
            else:
                flag = False
                break
    if flag:
        removeData(CommonConstants.CARTVSUSER,[CommonConstants.CART_ID],[cartId],[ConfigurationConstants.OPERATORS[1]],"(1)")
    return flag

def getCart(cartId):
    query = ConfigurationConstants.READ_TEMPLATE.substitute(
        {'columns': CommonConstants.ALL, 'table_name': CommonConstants.CARTS,
         'clause': getCriteria([CommonConstants.CART_ID], [cartId], [ConfigurationConstants.OPERATORS[1]], "(1)")})
    data = DBHandler.getData(query)
    if (data is not None and len(data) > 0):
        return data
    else:
        return []

def getCartId(userId):
    query = ConfigurationConstants.READ_TEMPLATE.substitute(
        {'columns': CommonConstants.ALL, 'table_name': CommonConstants.CARTVSUSER,
         'clause': getCriteria([CommonConstants.USER_ID], [userId], [ConfigurationConstants.OPERATORS[1]], "(1)")})
    data = DBHandler.getData(query)
    if (data is not None and len(data) > 0):
        return data[0][0]
    else:
        return -1

def getCountFromCart(userId,itemId):
    cartId = getCartId(userId)
    if (cartId != -1):
        query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns': CommonConstants.COUNT , 'table_name': CommonConstants.CARTS,'clause': getCriteria([CommonConstants.CART_ID,CommonConstants.ITEM_ID], [cartId,itemId], [ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[1]], "(1 and 2)")})
        data = DBHandler.getData(query)
        if(data is not None and len(data) > 0):
            return data[0][0]
    return 0


def getLeftQuantity(userId,itemId,count):
    query = ConfigurationConstants.READ_TEMPLATE.substitute(
        {'columns': ",".join([CommonConstants.QUANTITY, CommonConstants.PRICE]), 'table_name': CommonConstants.ITEMS,
         'clause': getCriteria([CommonConstants.ITEM_ID], [itemId], [ConfigurationConstants.OPERATORS[1]], "(1)")})
    data = DBHandler.getData(query)
    if int(data[0][0]) >= int(count):
        return int(data[0][0]) - int(count)
    else:
        return -1

def getStockAvailable(userId,itemId,count):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':",".join([CommonConstants.QUANTITY,CommonConstants.PRICE]),'table_name':CommonConstants.ITEMS,'clause':getCriteria([CommonConstants.ITEM_ID],[itemId],[ConfigurationConstants.OPERATORS[1]],"(1)")})
    data = DBHandler.getData(query)
    ct = getCountFromCart(userId,itemId)
    if  int(data[0][0]) >= (int(count) + ct):
        return (int(data[0][0]) - (int(count)+ct), int(data[0][1]))
    else:
        return (-1,-1)

def getAllUnits():
    data = {}
    query = ConfigurationConstants.READ_ALL_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.UNITS})
    output = DBHandler.getData(query)
    for dat in output:
        data[dat[0]] = dat[1]
    return data

def getAllCategories():
    data = {}
    query = ConfigurationConstants.READ_ALL_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.CATEGORIES})
    output = DBHandler.getData(query)
    for dat in output:
        data[dat[0]] = dat[1]
    return data

def getAllProducts():
    data = {}
    query = ConfigurationConstants.READ_ALL_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.ITEMS})
    output = DBHandler.getData(query)
    for dat in output:
        data[dat[0]] = dat[1]
    return data

def checkPrimaryData(columnData,tables):
    for i in range(len(tables)):
        table = tables[i]
        data = (json.load(open(ConfigurationConstants.FILE_PATH_TO_TABLES_JSON))["tables"][table])
        defaultColumns = data['columns']
        primaryKeys = data['primary_key']
        for col in defaultColumns.keys():
            if col not in primaryKeys and CommonConstants.UNIQUE in defaultColumns[col]["constraints"] :
                temp = {'columns':col,"table_name":table,"clause":getCriteria([col],[columnData[col]],[ConfigurationConstants.OPERATORS[1]],"(1)")}
                query = ConfigurationConstants.READ_TEMPLATE.substitute(temp)
                data = DBHandler.getData(query)
                if(len(data) != 0):
                    return f"The value with {col.replace('_',' ')} has already been registered"
    return None


def getList(type,id,search,sortType,sortValue):
    lst = []

    if(search is not None):
        search = re.escape(search)
    else:
        search = ''

    if(type == "products"):
        if (sortType is not None and sortValue is not None):
            filter = ''
            if sortType == 'category':
                filter = f" and t2.{CommonConstants.CATEGORY_ID} = '{sortValue}' "
            elif sortType == 'price':
                if sortValue == 'highToLow':
                    filter = f" ORDER BY t1.{CommonConstants.PRICE} DESC "
                elif sortValue == 'lowToHigh':
                    filter = f" ORDER BY t1.{CommonConstants.PRICE} ASC"
            elif sortType == 'unit':
                filter = f" and t3.{CommonConstants.UNIT_ID} = '{sortValue}' "
            query = ConfigurationConstants.ALL_PRODUCTS_QUERY.substitute({"store_id": id, 'search': search, 'filter': filter})
        else:
            query = ConfigurationConstants.ALL_PRODUCTS_QUERY.substitute({"store_id":id,'search':search,'filter':''})

        data = DBHandler.getData(query)
        for dat in data:
            res = {}
            res["id"] = dat[0]
            res["name"] = dat[1]
            res["price"] = dat[2]
            res["quantity"] = dat[3]
            res["category"] = dat[4]
            res["unit"] = dat[5]
            res["store"] = dat[6]
            res["unitId"] = dat[7]
            res["categoryId"] = dat[8]
            lst.append(res)
    elif(type == "categories"):
        query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.CATEGORIES,'clause':getCriteria([CommonConstants.STORE_ID,CommonConstants.CATEGORY_NAME],[id,search],[ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[5]],"(1 and 2)")})
        data = DBHandler.getData(query)
        for dat in data:
            res ={}
            res["id"] = dat[0]
            res["name"] = dat[1]
            lst.append(res)
    elif(type == "units"):
        query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.UNITS,'clause':getCriteria([CommonConstants.STORE_ID,CommonConstants.UNIT_NAME],[id,search],[ConfigurationConstants.OPERATORS[1],ConfigurationConstants.OPERATORS[5]],"(1 and 2)")})
        data = DBHandler.getData(query)
        for dat in data:
            res = {}
            res["id"] = dat[0]
            res["name"] = dat[1]
            lst.append(res)
    elif(type == "cart"):
        query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.CART_ID,'table_name':CommonConstants.CARTVSUSER,'clause':getCriteria([CommonConstants.USER_ID],[id],[ConfigurationConstants.OPERATORS[1]],"(1)")})
        data = DBHandler.getData(query)
        if data is not None and len(data) > 0:
            query = ConfigurationConstants.CART_QUERY.substitute({'cart_id':data[0][0]})
            data = DBHandler.getData(query)
            if data is not None and len(data) > 0:
                for dat in data:
                    res = {}
                    res["cart_id"] = dat[0]
                    res["item_id"] = dat[1]
                    res["quantity"] = dat[2]
                    res["price"] = dat[3]
                    res["total_price"] = dat[4]
                    res["name"] = dat[5]
                    res["category"] = dat[6]
                    res["unit"] = dat[7]
                    lst.append(res)
    return lst

def getBasicStats(storeId):
    totalStat = {}
    productsVsCount = {}
    categoriesVsCount = {}
    productVsSelling = {}
    categoriesVsSelling = {}
    data = DBHandler.getData(ConfigurationConstants.READ_ALL_STORE_TEMPLATE.substitute({'table_name':CommonConstants.ITEMS,'columns':",".join([CommonConstants.QUANTITY,CommonConstants.ITEM_NAME]),'store_id':storeId, 'order_by':CommonConstants.QUANTITY}))
    i = 0
    for dat in data:
        if i > ConfigurationConstants.PRODUCT_COUNT_STATS_LIMIT :
            productsVsCount[CommonConstants.OTHERS] = dat[0]
        else:
            productsVsCount[dat[1]] = dat[0]
            i += 1

    data = DBHandler.getData(ConfigurationConstants.CATEGORYVSCOUNT.substitute({'store_id':storeId}))
    i = 0
    for dat in data:
        if i > ConfigurationConstants.CATEGORY_COUNT_STATS_LIMIT :
            categoriesVsCount[CommonConstants.OTHERS] = dat[1]
        else:
            categoriesVsCount[dat[0]] = dat[1]
            i += 1

    data = DBHandler.getData(ConfigurationConstants.PRODUCTVSSELLING.substitute({'store_id':storeId}))
    i = 0
    for dat in data:
        if i > ConfigurationConstants.PRODUCT_SELLING_STATS_LIMIT:
            productVsSelling[CommonConstants.OTHERS] = dat[1]
        else:
            productVsSelling[dat[0]] = dat[1]
            i += 1

    data = DBHandler.getData(ConfigurationConstants.CATEGORYVSSELLING.substitute({'store_id': storeId}))
    i = 0
    for dat in data:
        if i > ConfigurationConstants.CATEGORY_SELLING_STATS_LIMIT:
            categoriesVsSelling[CommonConstants.OTHERS] = dat[1]
        else:
            categoriesVsSelling[dat[0]] = dat[1]
            i += 1

    statVars = [ConfigurationConstants.TOTAL_REVENUE,ConfigurationConstants.TOTAL_SELLING,ConfigurationConstants.TOTAL_CUSTOMERS, ConfigurationConstants.TOTAL_PRODUCTS, ConfigurationConstants.TOTAL_CATEGORIES]
    statCols = ["totalRevenue","totalSelling","totalCustomers","totalProducts","totalCategories"]
    i = 0
    for var in statVars:
        data= DBHandler.getData(var.substitute({'store_id': storeId}))
        if data is not None and len(data) != 0:
            totalStat[statCols[i]] = data[0][0]
        else:
            totalStat[statCols[i]] = 0
        i += 1
    if totalStat[statCols[0]] is None:
        totalStat[statCols[0]] = 0

    totalStat["productsVsCount"] = productsVsCount
    totalStat["categoriesVsCount"] = categoriesVsCount
    totalStat["productVsSelling"] = productVsSelling
    totalStat["categoriesVsSelling"] = categoriesVsSelling

    return totalStat