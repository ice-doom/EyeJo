import modelExtend from 'dva-model-extend'
import { isEmpty } from 'lodash'
import api from 'api'
import { pageModel } from 'utils/model'
const { pathToRegexp } = require('path-to-regexp')

const {
  queryProject,
  createProject,
  removeProject,
  removeProjectList,
  createProjectInfo,
  projectCheckName,
} = api

export default modelExtend(pageModel, {
  namespace: 'project',

  state: {
    modalVisible: false,
    modalType: 'create',
    selectedRowKeys: [],
  },

  subscriptions: {
    setup({ dispatch, history }) {
      history.listen((location) => {
        if (pathToRegexp('/project').exec(location.pathname)) {
          const payload = {}
          dispatch({
            type: 'query',
            payload,
          })
        }
      })
    },
  },

  effects: {
    *query({ payload = {} }, { call, put }) {
      let obj = { page: 1, limit: 10 }
      payload = isEmpty(payload) ? obj : { ...obj, ...payload }
      const data = yield call(queryProject, payload)
      // console.log('query', data)
      if (data) {
        yield put({
          type: 'querySuccess',
          payload: {
            list: data.data,
            pagination: {
              current: Number(payload.page) || 1,
              pageSize: Number(payload.limit) || 10,
              total: data.total,
            },
          },
        })
      }
    },

    *addInfo({ payload = {} }, { call }) {
      const { resolve, reject } = payload
      const data = yield call(createProjectInfo, {})
      if (data.success) {
        resolve(data.data)
      } else {
        reject(data)
      }
    },

    *check({ payload = {} }, { call }) {
      const { resolve, reject, parameter } = payload
      const data = yield call(projectCheckName, parameter)
      if (data.success) {
        resolve(data.data)
      } else {
        reject(data)
      }
    },

    *delete({ payload }, { call, put, select }) {
      // console.log(payload)
      const data = yield call(removeProject, { id: payload })
      const { selectedRowKeys } = yield select((_) => _.project)
      if (data.success) {
        yield put({
          type: 'updateState',
          payload: {
            selectedRowKeys: selectedRowKeys.filter((_) => _ !== payload),
          },
        })
      } else {
        return data
      }
    },

    *multiDelete({ payload }, { call, put }) {
      const data = yield call(removeProjectList, payload)
      if (data.success) {
        yield put({ type: 'updateState', payload: { selectedRowKeys: [] } })
      } else {
        throw data
      }
    },

    *create({ payload }, { call, put }) {
      const data = yield call(createProject, payload)
      if (data.success) {
        yield put({ type: 'hideModal' })
      } else {
        return data
      }
    },
  },

  reducers: {
    showModal(state, { payload }) {
      return { ...state, ...payload, modalVisible: true }
    },

    hideModal(state) {
      return { ...state, modalVisible: false }
    },
  },
})
