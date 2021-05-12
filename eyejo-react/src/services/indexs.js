// 有特殊要求（除了url、method、data还需要设置其他请求参数），接口文件
import request from 'utils/request'
import { apiPrefix } from 'utils/config'

// 导出excel接口，必须加上 responseType
export function queryProjectExportUrl(params) {
  return request({
    url: apiPrefix + '/api/project/url_info/export/',
    method: 'POST',
    data: params,
    responseType: 'arraybuffer',
  })
}
