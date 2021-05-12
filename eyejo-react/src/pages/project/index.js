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
@connect(({ project, loading }) => ({ project, loading }))
class Project extends PureComponent {
  handleRefresh = (newQuery) => {
    const { dispatch } = this.props
    // console.log(newQuery)
    dispatch({
      type: 'project/query',
      payload: newQuery,
    })
  }

  handleDeleteItems = () => {
    const { dispatch, project } = this.props
    const { list, pagination, selectedRowKeys } = project

    dispatch({
      type: 'project/multiDelete',
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
    const { dispatch, project, loading } = this.props
    const { modalVisible, modalType } = project

    return {
      visible: modalVisible,
      destroyOnClose: true,
      maskClosable: false,
      confirmLoading: loading.effects[`project/${modalType}`],
      title: '新增项目',
      width: 900,
      centered: true,
      onOk: (data) => {
        dispatch({
          type: `project/${modalType}`,
          payload: data,
        }).then((res) => {
          if (res.success) this.handleRefresh()
        })
      },
      checkName: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'project/check',
            payload: { resolve, reject, parameter },
          })
        })
      },
      handleAddInfo: () => {
        return new Promise((resolve, reject) => {
          dispatch({ type: 'project/addInfo', payload: { resolve, reject } })
        })
      },
      onCancel() {
        dispatch({
          type: 'project/hideModal',
        })
      },
    }
  }

  get listProps() {
    const { dispatch, project, loading } = this.props
    const { list, pagination, selectedRowKeys } = project
    // console.log(pagination)
    return {
      dataSource: list,
      loading: loading.effects['project/query'],
      pagination,
      onChange: (page) => {
        this.handleRefresh({
          page: page.current,
          limit: page.pageSize,
        })
      },
      onDeleteItem: (id) => {
        dispatch({
          type: 'project/delete',
          payload: id,
        }).then((res) => {
          // console.log(res)
          if (res.success) {
            this.handleRefresh({
              page:
                list.length === 1 && pagination.current > 1
                  ? pagination.current - 1
                  : pagination.current,
            })
          }
        })
      },
      rowSelection: {
        selectedRowKeys,
        onChange: (keys) => {
          dispatch({
            type: 'project/updateState',
            payload: {
              selectedRowKeys: keys,
            },
          })
        },
      },
    }
  }

  get filterProps() {
    const { location, dispatch, i18n } = this.props
    const { query } = location

    return {
      i18n,
      filter: {
        ...query,
      },
      onFilterChange: (value) => {
        this.handleRefresh({
          ...value,
        })
      },
      onAdd() {
        dispatch({
          type: 'project/showModal',
          payload: {
            modalType: 'create',
          },
        })
      },
    }
  }

  render() {
    const { project } = this.props
    const { selectedRowKeys, modalVisible } = project

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

Project.propTypes = {
  project: PropTypes.object,
  location: PropTypes.object,
  dispatch: PropTypes.func,
  loading: PropTypes.object,
}

export default Project
