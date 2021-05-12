import { history } from 'umi'
import { stringify } from 'qs'
import store from 'store'
import api from 'api'
const { pathToRegexp } = require('path-to-regexp')

const { loginUser } = api

export default {
  namespace: 'login',

  state: {},
  // subscriptions: {
  //   setup({ dispatch, history }) {
  //     history.listen(location => {
  //       if (pathToRegexp('/login').exec(location.pathname)) {
  //       }
  //     })
  //   },
  // },
  effects: {
    *login({ payload }, { put, call, select }) {
      const data = yield call(loginUser, payload)
      const { locationQuery } = yield select((_) => _.app)
      if (data.success) {
        const { from } = locationQuery
        yield put({ type: 'app/query' })
        store.set('user', { username: payload.username })
        if (!pathToRegexp('/login').exec(from)) {
          // console.log(from)
          if (['', '/', undefined].includes(from)) {
            history.push('/project')
          } else {
            history.push(from)
          }
        } else {
          history.push('/project')
        }
      } else {
        throw data
      }
    },
  },
}
