import modelExtend from "dva-model-extend";
import { isEmpty } from "lodash";
import api from "api";
import { pageModel } from "utils/model";
const { pathToRegexp } = require("path-to-regexp");

const {
  queryTask,
  createTask,
  removeTask,
  removeTaskList,
  pauseTask,
  queryProject,
  queryProjectDetailsAssets,
  taskCheckName,
} = api;

export default modelExtend(pageModel, {
  namespace: "task",

  state: {
    modalVisible: false,
    modalType: "create",
    selectedRowKeys: [],
    project_id: null,
  },

  subscriptions: {
    setup({ dispatch, history }) {
      history.listen((location) => {
        // console.log('setup', location)
        const { params } = location;
        if (pathToRegexp("/task").exec(location.pathname)) {
          let payload = {};
          if (!isEmpty(params)) {
            payload = params;
            if (params.project_id) {
              dispatch({
                type: "changeState",
                payload,
              });
            }
          }
          dispatch({
            type: "query",
            payload,
          });
        }
      });
    },
  },

  effects: {
    changeState({ payload = {} }, { put }) {
      // console.log(payload)
      put({
        type: "changeState",
        payload,
      });
    },
    *query({ payload = {} }, { call, put }) {
      let obj = { page: 1, limit: 10 };
      payload = isEmpty(payload) ? obj : { ...obj, ...payload };
      const data = yield call(queryTask, payload);
      // console.log('query', data)
      if (data) {
        yield put({
          type: "querySuccess",
          payload: {
            list: data.data,
            pagination: {
              current: Number(payload.page) || 1,
              pageSize: Number(payload.limit) || 10,
              total: data.total,
            },
          },
        });
      }
    },

    *delete({ payload }, { call, put, select }) {
      const data = yield call(removeTask, { id: payload });
      const { selectedRowKeys } = yield select((_) => _.task);
      if (data.success) {
        yield put({
          type: "updateState",
          payload: {
            selectedRowKeys: selectedRowKeys.filter((_) => _ !== payload),
          },
        });
      } else {
        throw data;
      }
    },

    *multiDelete({ payload }, { call, put }) {
      const data = yield call(removeTaskList, payload);
      if (data.success) {
        yield put({ type: "updateState", payload: { selectedRowKeys: [] } });
      } else {
        throw data;
      }
    },

    *pause({ payload }, { call, put, select }) {
      const data = yield call(pauseTask, { id: payload });
      const { selectedRowKeys } = yield select((_) => _.task);
      if (data.success) {
        yield put({
          type: "updateState",
          payload: {
            selectedRowKeys: selectedRowKeys.filter((_) => _ !== payload),
          },
        });
      } else {
        throw data;
      }
    },

    *create({ payload }, { call, put }) {
      const data = yield call(createTask, payload);
      if (data.success) {
        yield put({ type: "hideModal" });
        return data;
      } else {
        return data;
      }
    },

    *queryProject({ payload = {} }, { call, put }) {
      const data = yield call(queryProject, { page: 1, limit: 10000 });
      const { resolve, reject } = payload;
      if (data.success) {
        resolve(data.data);
      } else {
        reject(data);
      }
    },

    *queryAssets({ payload = {} }, { call, put }) {
      const { id, resolve, reject } = payload;
      const data = yield call(queryProjectDetailsAssets, {
        id,
        page: 1,
        limit: 10000,
      });
      if (data.success) {
        resolve(data.data);
      } else {
        reject(data);
      }
    },

    *check({ payload = {} }, { call }) {
      const { resolve, reject, parameter } = payload;
      const data = yield call(taskCheckName, parameter);
      if (data.success) {
        resolve(data.data);
      } else {
        reject(data);
      }
    },
  },

  reducers: {
    showModal(state, { payload }) {
      return { ...state, ...payload, modalVisible: true };
    },

    hideModal(state) {
      return { ...state, modalVisible: false };
    },
    changeState(state, { payload }) {
      // console.log(payload)
      return { ...state, ...payload };
    },
  },
});
