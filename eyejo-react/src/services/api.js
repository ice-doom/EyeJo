export default {
  // 用户信息
  queryUserInfo: '/api/project/userinfo/check/',

  // 登录
  logoutUser: '/api/logout',
  // 登出
  loginUser: 'POST /api/login',

  // 项目列表
  queryProject: 'POST /api/project/all/show/',
  // 项目新增
  createProject: 'POST /api/project/all/',
  // 项目-新增-名称是否重复
  projectCheckName: 'POST /api/project/assets/check_name/',
  // 项目新增初始化信息
  createProjectInfo: '/api/project/all/add_info/',
  // 项目详情-5个tab数据
  queryProjectDetailsUrl: 'POST /api/project/url_info/show/',
  queryProjectDetailsDomain: 'POST /api/project/domain/show/',
  queryProjectDetailsIp: 'POST /api/project/ip/show/',
  queryProjectDetailsLoginSite: 'POST /api/project/login_site/show/',
  queryProjectDetailsAssets: 'POST /api/project/assets/show/',
  // 项目详情-站点详情-导出excel
  // queryProjectExportUrl: 'POST /api/project/url_info/export/',
  // 项目-删除单个
  removeProject: 'POST /api/project/all/delete/',
  // 项目-删除多个
  removeProjectList: 'POST /api/project/all/multiple_delete/',
  // 项目-ip-查看旁站
  detailsIpSide: 'POST /api/project/ip/side_station/',
  // 项目-ip-查看C段
  detailsIpC: 'POST /api/project/ip/cnet/',
  // 项目-资产组-新增
  createGroup: 'POST /api/project/assets/',
  // 项目-资产组-新增-url列表
  createGroupUrl: 'POST /api/project/assets/url_info/',
  // 项目-资产-新增
  createAssets: 'POST /api/project/assets/add/',
  // 项目-资产组-详情
  detailsGroup: 'POST /api/project/assets/view/',
  // 项目-资产组-详情删除单个
  removeAssets: 'POST /api/project/assets/url_delete/',
  // 项目-资产组-详情删除多个
  removeAssetsList: 'POST /api/project/assets/url_multiple_delete/',
  // 项目-资产组-删除单个
  delGroup: 'POST /api/project/assets/delete/',
  // 项目-资产组-删除多个
  delGroupList: 'POST /api/project/assets/multiple_delete/',

  // 项目-tags列表
  tagList: 'POST /api/project/url_info/tags_show/',
  // 项目-tags删除
  removeTags: 'POST /api/project/url_info/tags_delete/',
  // 项目-tags新增
  addTags: 'POST /api/project/url_info/tags_add/',

  // 任务列表
  queryTask: 'POST /api/scanTask/task/show/',
  // 任务新增
  createTask: 'POST /api/scanTask/task/',
  // 任务-新增-名称是否重复
  taskCheckName: 'POST /api/scanTask/task/check_name/',
  // 任务详情-4个tab数据
  queryTaskDetailsVul: 'POST /api/scanTask/vul/show/',
  queryTaskDetailsPoc: 'POST /api/scanTask/poc/show/',
  queryTaskDetailsFuzz: 'POST /api/scanTask/fuzz/show/',
  queryTaskDetailsBrute: 'POST //api/scanTask/brute/show/',
  // 任务详情-FUZZ-详情
  detailsFuzz: 'POST /api/scanTask/fuzz/view/',
  // 任务-删除单个
  removeTask: 'POST /api/scanTask/task/delete/',
  // 任务-删除多个
  removeTaskList: 'POST /api/scanTask/task/multiple_delete/',
  // 任务-暂停
  pauseTask: 'POST /api/scanTask/task/stop/',

  // 配置页
  querySetting: '/api/scanTask/config/show/',
  editSetting: 'POST /api/scanTask/config/save/',
}
