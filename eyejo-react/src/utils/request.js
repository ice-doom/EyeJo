import axios from 'axios'
import { history } from 'umi'
import { cloneDeep } from 'lodash'
import { message } from 'antd'
import { CANCEL_REQUEST_MESSAGE } from 'utils/constant'
const { parse, compile } = require('path-to-regexp')

const { CancelToken } = axios
window.cancelRequest = new Map()

export default function request(options) {
  let { data, url, method = 'get' } = options
  // console.log(options)
  const cloneData = cloneDeep(data)

  try {
    let domain = ''
    const urlMatch = url.match(/[a-zA-z]+:\/\/[^/]*/)
    if (urlMatch) {
      ;[domain] = urlMatch
      url = url.slice(domain.length)
    }

    const match = parse(url)
    url = compile(url)(data)

    for (const item of match) {
      if (item instanceof Object && item.name in cloneData) {
        delete cloneData[item.name]
      }
    }
    url = domain + url
  } catch (e) {
    message.error(e.message)
  }

  options.url = url
  if (method === 'GET') {
    options.params = cloneData
  }
  options.cancelToken = new CancelToken((cancel) => {
    window.cancelRequest.set(Symbol(Date.now()), {
      pathname: window.location.pathname,
      cancel,
    })
  })

  return axios(options)
    .then((response) => {
      // console.log('response', response)
      const { data } = response

      // 站点详情导出excel特殊处理
      if (response.config.url === '/api/v1/api/project/url_info/export/') {
        // 从content-disposition响应头获取文件名
        let fileName = ''
        const contentDisposition = response.headers['content-disposition']
        if (contentDisposition) {
          fileName = window.decodeURI(contentDisposition.split('=')[1], 'UTF-8')
        }
        return Promise.resolve({
          // ...result,
          success: true,
          fileName,
          data,
        })
      }
      if (data.code === 100) {
        // 用户未登录
        history.push('/login')
        return Promise.resolve({
          success: false,
          ...data,
        })
      } else if (data.code !== 0) {
        // console.log('code',data.code)
        if (data.code === 102) {
          let msg = `${data.msg}${data.target}`
          message.error(msg)
        } else {
          message.error(data.msg)
        }
        return Promise.resolve({
          success: false,
          ...data,
        })
      }
      return Promise.resolve({
        // ...result,
        success: true,
        ...data,
      })
    })
    .catch((error) => {
      // console.log('axioserror', error)
      const { response, message } = error

      if (String(message) === CANCEL_REQUEST_MESSAGE) {
        return {
          success: false,
        }
      }

      let msg
      let statusCode

      if (response && response instanceof Object) {
        const { data, statusText } = response
        statusCode = response.status
        msg = data.message || statusText
      } else {
        statusCode = 600
        msg = error.message || 'Network Error'
      }

      /* eslint-disable */
      return Promise.reject({
        success: false,
        statusCode,
        message: msg,
      })
    })
}
