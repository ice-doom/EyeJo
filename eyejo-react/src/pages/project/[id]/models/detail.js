import api from 'api'
import modelExtend from 'dva-model-extend'
import { pageModel } from 'utils/model'
import { queryProjectExportUrl } from '@/services/indexs'
const { pathToRegexp } = require('path-to-regexp')

const {
  queryProjectDetailsUrl,
  queryProjectDetailsDomain,
  queryProjectDetailsIp,
  queryProjectDetailsLoginSite,
  queryProjectDetailsAssets,
  createGroup,
  detailsGroup,
  delGroup,
  delGroupList,
  createGroupUrl,
  detailsIpSide,
  detailsIpC,
  createAssets,
  removeAssets,
  removeAssetsList,
  tagList,
  removeTags,
  addTags,
} = api

export default modelExtend(pageModel, {
  namespace: 'projecyDetail',

  state: {
    currentItem: {},
    activeKey: '1',
    groupAddVisible: false,
    assetsAddVisible: false,
    groupDetailsVisible: false,
    ipSideVisible: false,
    ipCVisible: false,
    tagsSettingVisible: false,
    addTagsVisible: false,
    selectedRowKeys: [],
    listDetails: [],
    paginationDetails: {
      showSizeChanger: true,
      showQuickJumper: true,
      current: 1,
      total: 0,
      pageSize: 10,
    },
    projectDetailsSortData: {},
    projectDetailsFilterData: {},
    projectGroupDetailsSortData: {},
    projectGroupDetailsFilterData: {},
    tagsSettingData: [],
    tagsList: [],
  },

  subscriptions: {
    setup({ dispatch, history }) {
      history.listen(({ pathname }) => {
        // console.log(pathname, query)
        const match = pathToRegexp('/project/:id').exec(pathname)
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
      const activeKey = yield select((state) => state.projecyDetail.activeKey)
      const pagination = yield select((state) => state.projecyDetail.pagination)
      const projectDetailsSortData = yield select(
        (state) => state.projecyDetail.projectDetailsSortData
      )
      const projectDetailsFilterData = yield select(
        (state) => state.projecyDetail.projectDetailsFilterData
      )
      // console.log(projectDetailsSortData)
      let obj = {
        page: pagination.current,
        limit: pagination.pageSize,
        ...projectDetailsSortData,
        ...projectDetailsFilterData,
      }
      payload = { ...obj, ...payload }
      let method = queryProjectDetailsUrl
      switch (activeKey) {
        case '2':
          method = queryProjectDetailsDomain
          break
        case '3':
          method = queryProjectDetailsIp
          break
        case '4':
          method = queryProjectDetailsLoginSite
          break
        case '5':
          method = queryProjectDetailsAssets
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
    *exportUrl({ payload }, { call, put }) {
      const data = yield call(queryProjectExportUrl, payload)
      if (data.success) {
        return data
      } else {
        throw data
      }
    },
    *create({ payload }, { call, put }) {
      const data = yield call(createGroup, payload)
      if (data.success) {
        yield put({ type: 'changeState', payload: { groupAddVisible: false } })
      } else {
        return data
      }
    },
    *createAssets({ payload }, { call, put }) {
      const data = yield call(createAssets, payload)
      if (data.success) {
        yield put({ type: 'changeState', payload: { assetsAddVisible: false } })
      } else {
        return data
      }
    },
    *delete({ payload }, { call, put, select }) {
      const data = yield call(delGroup, { id: payload })
      const { selectedRowKeys } = yield select((_) => _.project)
      if (data.success) {
        yield put({
          type: 'updateState',
          payload: {
            selectedRowKeys: selectedRowKeys.filter((_) => _ !== payload),
          },
        })
      } else {
        throw data
      }
    },
    *multiDelete({ payload }, { call, put }) {
      const data = yield call(delGroupList, payload)
      if (data.success) {
        yield put({ type: 'updateState', payload: { selectedRowKeys: [] } })
      } else {
        throw data
      }
    },
    // 资产组详情
    *details({ payload }, { call, put, select }) {
      const pagination = yield select(
        (state) => state.projecyDetail.paginationDetails
      )
      const projectGroupDetailsSortData = yield select(
        (state) => state.projecyDetail.projectGroupDetailsSortData
      )
      const projectGroupDetailsFilterData = yield select(
        (state) => state.projecyDetail.projectGroupDetailsFilterData
      )
      let obj = {
        page: pagination.current,
        limit: pagination.pageSize,
        ...projectGroupDetailsSortData,
        ...projectGroupDetailsFilterData,
      }
      payload = { ...obj, ...payload }
      const data = yield call(detailsGroup, payload)
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
    *detailsIpSide({ payload }, { call, put }) {
      let obj = { page: 1, limit: 10 }
      payload = { ...obj, ...payload }
      const data = yield call(detailsIpSide, payload)
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
    *detailsIpC({ payload }, { call, put }) {
      let obj = { page: 1, limit: 10 }
      payload = { ...obj, ...payload }
      const data = yield call(detailsIpC, payload)
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
    *urlInfo({ payload = {} }, { call }) {
      const { resolve, reject, parameter } = payload
      const data = yield call(createGroupUrl, parameter)
      if (data.success) {
        resolve(data)
      } else {
        reject(data)
      }
    },
    // tag操作相关
    *tagList({ payload = {} }, { call, put }) {
      const data = yield call(tagList, payload)
      if (data.success) {
        yield put({
          type: 'changeState',
          payload: {
            tagsList: data.data,
          },
        })
      }
    },
    *tagInfo({ payload = {} }, { call, put }) {
      const { resolve, reject, parameter } = payload
      const data = yield call(tagList, parameter)
      if (data.success) {
        yield put({
          type: 'changeState',
          payload: {
            tagsSettingData: data.data,
          },
        })
        resolve(data)
      } else {
        reject(data)
      }
    },
    *deleteTags({ payload = {} }, { call }) {
      const data = yield call(removeTags, payload)
      if (data.success) {
      } else {
        return data
      }
    },

    *addTag({ payload }, { call, put }) {
      const data = yield call(addTags, payload)
      if (data.success) {
        yield put({ type: 'changeState', payload: { addTagsVisible: false } })
        return data
      } else {
        return data
      }
    },
    // 资产组删除一项
    *deleteAssets({ payload }, { call, put, select }) {
      const data = yield call(removeAssets, { id: payload })
      if (data.success) {
      } else {
        return data
      }
    },
    // 资产组删除多项
    *multiDeleteAssets({ payload }, { call, put }) {
      const data = yield call(removeAssetsList, payload)
      if (data.success) {
      } else {
        return data
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
      // console.log(state, payload)
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
