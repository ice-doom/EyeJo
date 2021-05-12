import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Input, Modal, Form, Table, Button } from 'antd'
import { Trans } from '@lingui/react'
const { pathToRegexp } = require('path-to-regexp')

const { Search } = Input
const { confirm } = Modal

class TaskAddModal extends PureComponent {
  state = {
    // tableData: [],
    pagination: {
      size: 'small',
      showSizeChanger: true,
      showQuickJumper: false,
      current: 1,
      total: 0,
      pageSize: 10,
    },
  }

  formRef = React.createRef()

  handleRefresh = (payload = {}) => {
    const { getTagInfo, location } = this.props
    const { pagination } = this.state
    const { current, pageSize } = pagination
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    const id = match[1]
    let obj = {
      page: current,
      limit: pageSize,
      project_id: id,
    }
    // console.log(activeTab)
    getTagInfo({ ...obj, ...payload }).then((data) => {
      this.setState((state) => ({
        ...state,
        // tableData: data.data,
        pagination: {
          ...state.pagination,
          total: data.total,
        },
      }))
    })
  }

  handleDel = (item) => {
    // console.log(item)
    const { onDeleteItem, location } = this.props
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    const id = match[1]
    confirm({
      title: '你确定要删除吗？',
      onOk() {
        onDeleteItem({
          name: item.name,
          project_id: id,
        })
      },
    })
  }

  componentDidMount() {
    this.handleRefresh()
  }

  handleSubmit = () => {
    const values = this.formRef.current.getFieldsValue()
    this.handleRefresh(values)
  }

  onChange = (page, filters, sorter) => {
    // console.log(page)
    let sortData = {}
    if (sorter.order) {
      sortData = {
        field: sorter.field,
        order: sorter.order === 'ascend' ? 'asc' : 'desc',
      }
    }
    this.setState((state) => ({
      ...state,
      sortData,
      pagination: {
        ...state.pagination,
        current: page.current,
        pageSize: page.pageSize,
      },
    }))
    // this.handleRefresh()
    this.handleRefresh({
      page: page.current,
      limit: page.pageSize,
    })
  }

  render() {
    const {
      tagsSettingData,
      onCancel,
      form,
      loading,
      ...modalProps
    } = this.props
    const { pagination } = this.state
    // const { tableData, pagination } = this.state
    // console.log(pagination)

    const columns = [
      {
        title: <Trans>tag</Trans>,
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: <Trans>操作</Trans>,
        dataIndex: 'operation',
        key: 'operation',
        render: (text, record) => {
          return (
            <Button
              danger
              type="primary"
              onClick={() => this.handleDel(record)}
            >
              删除
            </Button>
          )
        },
      },
    ]

    return (
      <Modal
        {...modalProps}
        onCancel={onCancel}
        footer={[
          <Button key="back" onClick={onCancel}>
            关闭
          </Button>,
        ]}
      >
        <Form
          ref={this.formRef}
          name="control-ref"
          layout="inline"
          style={{ marginBottom: '10px' }}
        >
          <Form.Item name="query">
            <Search placeholder="请输入tag名称" onSearch={this.handleSubmit} />
          </Form.Item>
        </Form>
        <Table
          loading={loading}
          dataSource={tagsSettingData}
          pagination={{
            ...pagination,
            showTotal: (total) => `Total ${total}`,
          }}
          onChange={this.onChange}
          bordered
          columns={columns}
          simple
          scroll={{ y: 330 }}
          rowKey={(record) => record.name}
          key="tableLeft"
        />
      </Modal>
    )
  }
}

TaskAddModal.propTypes = {
  onCancel: PropTypes.func,
}

export default TaskAddModal
