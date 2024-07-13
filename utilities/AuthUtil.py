import CommonConstants
import ConfigurationConstants
from Handlers import DBHandler
from utilities import CommonUtil,DBUtil


def validateUser(username,password):
    query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns':CommonConstants.ALL,'table_name':CommonConstants.USERS,'clause':DBUtil.getCriteria([CommonConstants.USERNAME],[username],[ConfigurationConstants.OPERATORS[1]],"(1)")})
    data = DBHandler.getData(query)
    status = {"data" : None,"status":"FAILURE","message":None}
    try:
        if(len(data) != 0):
            query = ConfigurationConstants.READ_TEMPLATE.substitute({'columns': CommonConstants.PASSWORD,'table_name':CommonConstants.USERVSPASSWORD,'clause':DBUtil.getCriteria([CommonConstants.USER_ID],[data[0][0]],[ConfigurationConstants.OPERATORS[1]], "(1)")})
            if password == CommonUtil.decode(DBHandler.getData(query)[0][0]):
                status["status"] = "SUCCESS"
                status["data"] = data
            else:
                status["status"] = "FAILED"
                status["message"] = "login failed wrong password"
        else:
            status["status"] = "FAILED"
            status["message"] = "user not found, kindly register if you're new user"
        return status
    except Exception as es:
        CommonUtil.getLogger().error(f"exception while validation user {es}")