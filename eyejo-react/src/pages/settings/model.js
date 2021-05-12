import api from 'api'
const { pathToRegexp } = require('path-to-regexp')

const { querySetting, editSetting } = api

export default {
  namespace: 'settings',

  state: {
    settingFormData: {},
    initialFormData: {},
  },
  subscriptions: {
    setup({ dispatch, history }) {
      history.listen((location) => {
        if (pathToRegexp('/settings').exec(location.pathname)) {
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
    *query({ payload }, { put, call }) {
      const data = yield call(querySetting, payload)
      // console.log('query', data)
      if (data) {
        yield put({
          type: 'querySuccess',
          payload: {
            settingFormData: data.data,
            initialFormData: data.data,
          },
        })
      }
    },
    *edit({ payload }, { put, call }) {
      // console.log(payload)
      const { diff, values } = payload
      const data = yield call(editSetting, diff)
      // console.log('query', payload)
      if (data) {
        yield put({
          type: 'querySuccess',
          payload: {
            settingFormData: values,
            initialFormData: values,
          },
        })
        return data
      }
    },
  },
  reducers: {
    querySuccess(state, { payload }) {
      return { ...state, ...payload }
    },
  },
}
