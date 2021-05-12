import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'umi'
import { Row, Col, Button, Popconfirm } from 'antd'
import { withI18n } from '@lingui/react'
import { Page } from 'components'
import List from './components/List'
import Filter from './components/Filter'
import Modal from './components/Modal'

@withI18n()
@connect(({ task, loading }) => ({ task, loading }))
class Task extends PureComponent {
  handleRefresh = (newQuery) => {
    const { dispatch } = this.props
    // console.log(newQuery)
    dispatch({
      type: 'task/query',
      payload: newQuery,
    })
  }

  handleDeleteItems = () => {
    const { dispatch, task } = this.props
    const { list, pagination, selectedRowKeys } = task

    dispatch({
      type: 'task/multiDelete',
      payload: {
        id: selectedRowKeys,
      },
    }).then(() => {
      this.handleRefresh({
        page:
          list.length === selectedRowKeys.length && pagination.current > 1
            ? pagination.current - 1
            : pagination.current,
      })
    })
  }

  get modalProps() {
    const { dispatch, task, loading, i18n } = this.props
    const { modalVisible, modalType } = task

    return {
      i18n,
      visible: modalVisible,
      destroyOnClose: true,
      maskClosable: false,
      confirmLoading: loading.effects[`task/${modalType}`],
      title: '新增任务',
      width: 900,
      centered: true,
      onOk: (data) => {
        dispatch({
          type: `task/${modalType}`,
          payload: data,
        }).then((res) => {
          // console.log('res', res)
          if (res.success) this.handleRefresh()
        })
      },
      handleAddInfo: () => {
        return new Promise((resolve, reject) => {
          dispatch({ type: 'project/addInfo', payload: { resolve, reject } })
        })
      },
      getProjectData: () => {
        return new Promise((resolve, reject) => {
          dispatch({ type: 'task/queryProject', payload: { resolve, reject } })
        })
      },
      getAssetsData: (id) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'task/queryAssets',
            payload: { id, resolve, reject },
          })
        })
      },
      checkName: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'task/check',
            payload: { resolve, reject, parameter },
          })
        })
      },
      onCancel() {
        dispatch({
          type: 'task/hideModal',
        })
      },
    }
  }

  get listProps() {
    const { dispatch, task, loading } = this.props
    const { list, pagination, selectedRowKeys } = task
    return {
      dataSource: list,
      loading: loading.effects['task/query'],
      pagination,
      onChange: (page) => {
        this.handleRefresh({
          page: page.current,
          limit: page.pageSize,
        })
      },
      onDeleteItem: (id) => {
        dispatch({
          type: 'task/delete',
          payload: id,
        }).then(() => {
          this.handleRefresh({
            page:
              list.length === 1 && pagination.current > 1
                ? pagination.current - 1
                : pagination.current,
          })
        })
      },
      onPauseItem: (id) => {
        dispatch({
          type: 'task/pause',
          payload: id,
        }).then(() => {
          this.handleRefresh({
            page:
              list.length === 1 && pagination.current > 1
                ? pagination.current - 1
                : pagination.current,
          })
        })
      },
      rowSelection: {
        selectedRowKeys,
        onChange: (keys) => {
          dispatch({
            type: 'task/updateState',
            payload: {
              selectedRowKeys: keys,
            },
          })
        },
      },
    }
  }

  get filterProps() {
    const { location, dispatch, i18n, task } = this.props
    const { project_id } = task
    const { query } = location

    return {
      i18n,
      project_id,
      filter: {
        ...query,
      },
      onFilterChange: (value) => {
        this.handleRefresh({
          ...value,
        })
      },
      getProjectData: () => {
        return new Promise((resolve, reject) => {
          dispatch({ type: 'task/queryProject', payload: { resolve, reject } })
        })
      },
      onAdd() {
        dispatch({
          type: 'task/showModal',
          payload: {
            modalType: 'create',
          },
        })
      },
    }
  }

  render() {
    const { task } = this.props
    const { selectedRowKeys, modalVisible } = task

    return (
      <Page inner>
        <Filter {...this.filterProps} />
        {selectedRowKeys.length > 0 && (
          <Row style={{ marginBottom: 24, textAlign: 'right', fontSize: 13 }}>
            <Col>
              {`Selected ${selectedRowKeys.length} items `}
              <Popconfirm
                title="你确定要删除吗？"
                placement="left"
                onConfirm={this.handleDeleteItems}
              >
                <Button type="primary" style={{ marginLeft: 8 }}>
                  Remove
                </Button>
              </Popconfirm>
            </Col>
          </Row>
        )}
        <List {...this.listProps} />
        {modalVisible ? <Modal {...this.modalProps} /> : <></>}
      </Page>
    )
  }
}

Task.propTypes = {
  task: PropTypes.object,
  location: PropTypes.object,
  dispatch: PropTypes.func,
  loading: PropTypes.object,
}

export default Task
