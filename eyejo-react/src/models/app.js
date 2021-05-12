/* global window */

import { history } from 'umi'
import { stringify } from 'qs'
import store from 'store'
import { CANCEL_REQUEST_MESSAGE } from 'utils/constant'
import api from 'api'
const { pathToRegexp } = require('path-to-regexp')

const { logoutUser, queryUserInfo } = api

const goDashboard = () => {
  if (pathToRegexp(['/', '/login']).exec(window.location.pathname)) {
    history.push({
      pathname: '/project',
    })
  }
}

const getCookie = (key) => {
  // 1.先获取所有cookie，若cookie没有值，返回空字符串
  var cookies = document.cookie
  if (cookies.length === 0) {
    return ''
  }
  // 2.拆分每一个cookie
  cookies = cookies.split('; ')
  for (var i = 0; i < cookies.length; i++) {
    var arr = cookies[i].split('=')
    if (arr[0] === key) {
      return arr[1]
    }
  }
}

export default {
  namespace: 'app',
  state: {
    routeList: [],
    locationPathname: '',
    locationQuery: {},
    theme: store.get('theme') || 'light',
    collapsed: store.get('collapsed') || false,
    notifications: [
      {
        title: 'New User is registered.',
        date: new Date(Date.now() - 10000000),
      },
      {
        title: 'Application has been approved.',
        date: new Date(Date.now() - 50000000),
      },
    ],
  },
  subscriptions: {
    setup({ dispatch }) {
      dispatch({ type: 'query' })
    },
    setupHistory({ dispatch, history }) {
      history.listen((location) => {
        dispatch({
          type: 'updateState',
          payload: {
            locationPathname: location.pathname,
            locationQuery: location.query,
          },
        })
      })
    },

    setupRequestCancel({ history }) {
      history.listen(() => {
        const { cancelRequest = new Map() } = window

        cancelRequest.forEach((value, key) => {
          if (value.pathname !== window.location.pathname) {
            value.cancel(CANCEL_REQUEST_MESSAGE)
            cancelRequest.delete(key)
          }
        })
      })
    },
  },
  effects: {
    *query({ payload }, { call, put, select }) {
      // 判断是否登录
      const isInit = getCookie('sessionid')
      // console.log(isInit)
      if (isInit) {
        goDashboard()
        return
      }
      const { success } = yield call(queryUserInfo, payload)
      if (success) {
        let routeList = [
          {
            id: '2',
            icon: 'unordered-list',
            name: 'Project',
            zh: {
              name: '项目管理',
            },
            route: '/project',
          },
          {
            id: '21',
            menuParentId: '-1',
            breadcrumbParentId: '2',
            name: 'Project Detail',
            zh: {
              name: '项目详情',
            },
            route: '/project/:id',
          },
          {
            id: '3',
            icon: 'unordered-list',
            name: 'Task',
            zh: {
              name: '任务管理',
            },
            route: '/task',
          },
          {
            id: '31',
            menuParentId: '-1',
            breadcrumbParentId: '3',
            name: 'Task Detail',
            zh: {
              name: '任务详情',
            },
            route: '/task/:id',
          },
          {
            id: '4',
            icon: 'setting',
            name: 'settings',
            zh: {
              name: '项目设置',
            },
            route: '/settings',
          },
        ]
        store.set('routeList', routeList)
        goDashboard()
      } else {
        history.push({
          pathname: '/login',
        })
      }
    },

    *signOut({ payload }, { call, put, select }) {
      const { locationPathname } = yield select((_) => _.app)
      const data = yield call(logoutUser)
      if (data.success) {
        store.set('routeList', [])
        store.set('user', {})
        history.push({
          pathname: '/login',
          search: stringify({
            from: locationPathname,
          }),
        })
      } else {
        throw data
      }
    },
  },
  reducers: {
    updateState(state, { payload }) {
      return {
        ...state,
        ...payload,
      }
    },

    handleThemeChange(state, { payload }) {
      store.set('theme', payload)
      state.theme = payload
    },

    handleCollapseChange(state, { payload }) {
      store.set('collapsed', payload)
      state.collapsed = payload
    },

    allNotificationsRead(state) {
      state.notifications = []
    },
  },
}
