import api from 'api'
import modelExtend from 'dva-model-extend'
import { pageModel } from 'utils/model'
const { pathToRegexp } = require('path-to-regexp')

const {
  queryTaskDetailsVul,
  queryTaskDetailsPoc,
  queryTaskDetailsFuzz,
  queryTaskDetailsBrute,
  detailsFuzz,
} = api

export default modelExtend(pageModel, {
  namespace: 'taskDetail',

  state: {
    activeKey: '1',
    currentItem: {},
    detailsVisible: false,
    listDetails: [],
    paginationDetails: {
      showSizeChanger: true,
      showQuickJumper: true,
      current: 1,
      total: 0,
      pageSize: 10,
    },
    taskFuzzDetailsSortData: {},
    taskFuzzDetailsFilterData: {},
  },

  subscriptions: {
    setup({ dispatch, history }) {
      history.listen(({ pathname, query }) => {
        // console.log(pathname, query)
        const match = pathToRegexp('/task/:id').exec(pathname)
        if (match) {
          const payload = { id: match[1] }
          dispatch({
            type: 'query',
            payload,
          })
        }
      })
    },
  },

  effects: {
    *query({ payload = {} }, { call, put, select }) {
      let obj = { page: 1, limit: 10 }
      payload = { ...obj, ...payload }
      const activeKey = yield select((state) => state.taskDetail.activeKey)
      // console.log(activeKey)
      let method = queryTaskDetailsVul
      switch (activeKey) {
        case '2':
          method = queryTaskDetailsPoc
          break
        case '3':
          method = queryTaskDetailsFuzz
          break
        case '4':
          method = queryTaskDetailsBrute
          break
        default:
          break
      }
      const data = yield call(method, payload)
      if (data.success) {
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
      } else {
        throw data
      }
    },
    *details({ payload }, { call, put, select }) {
      const pagination = yield select(
        (state) => state.projecyDetail.paginationDetails
      )
      const taskFuzzDetailsSortData = yield select(
        (state) => state.projecyDetail.taskFuzzDetailsSortData
      )
      const taskFuzzDetailsFilterData = yield select(
        (state) => state.projecyDetail.taskFuzzDetailsFilterData
      )
      let obj = {
        page: pagination.current,
        limit: pagination.pageSize,
        ...taskFuzzDetailsSortData,
        ...taskFuzzDetailsFilterData,
      }
      payload = { ...obj, ...payload }
      const data = yield call(detailsFuzz, payload)
      if (data.success) {
        yield put({
          type: 'querySuccessDetails',
          payload: {
            listDetails: data.data,
            paginationDetails: {
              current: Number(payload.page) || 1,
              pageSize: Number(payload.limit) || 10,
              total: data.total,
            },
          },
        })
      } else {
        throw data
      }
    },
  },

  reducers: {
    changeKey(state, { payload }) {
      const { activeKey } = payload
      return { ...state, activeKey: activeKey }
    },
    changeState(state, { payload }) {
      // console.log(payload)
      return { ...state, ...payload }
    },
    querySuccessDetails(state, { payload }) {
      const { listDetails, paginationDetails } = payload
      return {
        ...state,
        listDetails,
        paginationDetails: {
          ...state.paginationDetails,
          ...paginationDetails,
        },
      }
    },
  },
})
