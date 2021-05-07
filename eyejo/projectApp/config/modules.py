class TaskStatus:
    WAITING = "waiting"
    DONE = "done"
    STOP = "stop"


error_map = {
    "NotLogin": {
        "msg": "用户未登录",
        "code": 100
    },
    "LoginFail": {
        "msg": "用户或密码错误",
        "code": 101
    },
    "TargetInvalid": {
        "msg": "输入域名无效",
        "code": 102
    },
    "IPInBlackIpc": {
        "msg": "输入目标存在黑名单IP列表中",
        "code": 103
    },
    "AssetUrlEmpty": {
        "msg": "资产组URL为空",
        "code": 104
    },
    "ProjectExist": {
        "msg": "项目名已存在",
        "code": 201
    },
    "ProjectNameEmpty": {
        "msg": "项目名为空",
        "code": 202
    },
    "ProjectNotFound": {
        "msg": "未找到该项目",
        "code": 204
    },
    "PortInvalid": {
        "msg": "端口号存在非法字符",
        "code": 205
    },
    "BruteTypeInvalid": {
        "msg": "爆破类型存在非法字符",
        "code": 206
    },
    "ProjectNameInvalid": {
        "msg": "项目名称存在非法字符",
        "code": 207
    },
    "FuzzFileInvalid": {
        "msg": "FUZZ文件名存在非法字符",
        "code": 208
    },
    "TaskNameInvalid": {
        "msg": "任务名称存在非法字符",
        "code": 209
    },
    "AssetNameInvalid": {
        "msg": "资产组名称存在非法字符",
        "code": 210
    },
    "AssetExist": {
        "msg": "资产组已存在",
        "code": 211
    },
    "TagsAddError": {
        "msg": "未选择需要加入tags的URL",
        "code": 212
    },
    "AssetsNotFound": {
        "msg": "资产组未找到",
        "code": 304
    },
    "InputStringError": {
        "msg": "输入参数非字符类型",
        "code": 401
    },
    "InputIntError": {
        "msg": "输入参数非数字类型",
        "code": 402
    },
    "TaskExist": {
        "msg": "任务已存在",
        "code": 501
    },
    "TaskNameEmpty": {
        "msg": "任务为空",
        "code": 502
    },
    "TaskDeleteError": {
        "msg": "请先停止任务后删除",
        "code": 503
    },
    "DeleteNotFound": {
        "msg": "未找到需要删除的内容",
        "code": 504
    },
    "TaskNotFound": {
        "msg": "未找到对应的任务",
        "code": 505
    },
    "FofaApiEmailInvalid": {
        "msg": "FOFA邮箱输入错误",
        "code": 601
    },
    "FofaApiKeyInvalid": {
        "msg": "FOFA Key输入错误",
        "code": 602
    },
    "ShodanApiKeyInvalid": {
        "msg": "Shaodan Api输入错误",
        "code": 603
    }
}


class ErrorMsg:
    LoginFail = error_map['LoginFail']
    NotLogin = error_map['NotLogin']
    TargetInvalid = error_map['TargetInvalid']
    IPInBlackIpc = error_map['IPInBlackIpc']
    AssetUrlEmpty = error_map['AssetUrlEmpty']
    ProjectExist = error_map['ProjectExist']
    ProjectNameEmpty = error_map['ProjectNameEmpty']
    ProjectNotFound = error_map['ProjectNotFound']
    # AssetsForProjectNotFound = error_map['AssetsForProjectNotFound']
    PortInvalid = error_map['PortInvalid']
    BruteTypeInvalid = error_map['BruteTypeInvalid']
    ProjectNameInvalid = error_map['ProjectNameInvalid']
    FuzzFileInvalid = error_map['FuzzFileInvalid']
    TaskNameInvalid = error_map['TaskNameInvalid']
    AssetNameInvalid = error_map['AssetNameInvalid']
    AssetsNotFound = error_map['AssetsNotFound']
    InputStringError = error_map['InputStringError']
    InputIntError = error_map['InputIntError']
    AssetExist = error_map['AssetExist']
    TagsAddError = error_map['TagsAddError']
    DeleteNotFound = error_map['DeleteNotFound']
    TaskDeleteError = error_map['TaskDeleteError']
    TaskExist = error_map['TaskExist']
    TaskNameEmpty = error_map['TaskNameEmpty']
    TaskNotFound = error_map['TaskNotFound']
    FofaApiEmailInvalid = error_map['FofaApiEmailInvalid']
    FofaApiKeyInvalid = error_map['FofaApiKeyInvalid']
    ShodanApiKeyInvalid = error_map['ShodanApiKeyInvalid']
