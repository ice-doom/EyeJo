import request from 'utils/request'
import { apiPrefix } from 'utils/config'
import { isEmpty } from 'lodash'

import api from './api'

const gen = (params) => {
  let url = apiPrefix + params
  let method = 'GET'

  const paramsArray = params.split(' ')
  if (paramsArray.length === 2) {
    method = paramsArray[0]
    url = apiPrefix + paramsArray[1]
  }

  return function (data) {
    // console.log('data', data)
    // 所有接口，过滤搜索参数为空字符的情况
    if (!isEmpty(data)) {
      for (let item in data) {
        if (data[item] === '') {
          delete data[item]
        }
      }
    }
    return request({
      url,
      data,
      method,
    })
  }
}

const APIFunction = {}
for (const key in api) {
  APIFunction[key] = gen(api[key])
}

APIFunction.queryWeather = (params) => {
  params.key = 'i7sau1babuzwhycn'
  return request({
    url: `${apiPrefix}/weather/now.json`,
    data: params,
  })
}

export default APIFunction
