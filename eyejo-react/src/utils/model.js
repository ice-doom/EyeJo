import modelExtend from 'dva-model-extend'

export const model = {
  reducers: {
    updateState(state, { payload }) {
      return {
        ...state,
        ...payload,
      }
    },
  },
}

export const pageModel = modelExtend(model, {
  state: {
    list: [],
    pagination: {
      // pageSizeOptions: [2, 3, 4],
      showSizeChanger: true,
      showQuickJumper: true,
      current: 1,
      total: 0,
      pageSize: 10,
    },
  },

  reducers: {
    querySuccess(state, { payload }) {
      // console.log(888, payload)
      const { list, pagination } = payload
      return {
        ...state,
        list,
        pagination: {
          ...state.pagination,
          ...pagination,
        },
      }
    },
  },
})
