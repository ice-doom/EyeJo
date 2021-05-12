import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import {
  Form,
  Input,
  Modal,
  Row,
  Col,
  Table,
  Button,
  Tabs,
  Checkbox,
  Select,
} from 'antd'
import { Trans } from '@lingui/react'
import { hasSelected, addItem, removeItem } from '@/utils/table.js'
const { pathToRegexp } = require('path-to-regexp')

const FormItem = Form.Item
const { Search, TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

class TaskAddModal extends PureComponent {
  state = {
    tableDataLeft: [],
    tableDataRight: [],
    pagination: {
      size: 'small',
      showSizeChanger: true,
      showQuickJumper: false,
      current: 1,
      total: 0,
      pageSize: 10,
    },
    activeTab: '1',
    inputURL: '', // 手动输入url存放的内容
    checkValue: false, // 手动输入复选框存放的内容
    sortData: {},
  }

  formRef = React.createRef()
  formRefHas = React.createRef()
  formRefTag = React.createRef()

  handleRefresh = (payload = {}) => {
    const { getUrlInfo, getTagInfo, location } = this.props
    const { pagination, sortData, activeTab } = this.state
    const { current, pageSize } = pagination
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    const id = match[1]
    let obj = {
      page: current,
      limit: pageSize,
      ...sortData,
      id,
    }
    let method = getUrlInfo
    if (activeTab === '2') {
      method = getTagInfo
      obj = {
        page: current,
        limit: pageSize,
        project_id: id,
      }
    }
    // console.log(activeTab)
    method({ ...obj, ...payload }).then((data) => {
      this.setState((state) => ({
        ...state,
        tableDataLeft: data.data,
        pagination: {
          ...state.pagination,
          total: data.total,
        },
      }))
    })
  }

  componentDidMount() {
    this.handleRefresh()
  }

  handleTabChange = (tab) => {
    // console.log('tab', tab)
    this.setState({ activeTab: tab }, () => {
      // 切换tab情况数据，重新获取数据
      if (['1', '2'].includes(tab)) {
        this.setState({ tableDataRight: [] })
        if (tab === '1') this.formRefHas.current.resetFields()
        if (tab === '2') this.formRefTag.current.resetFields()
        this.handleRefresh()
      }
    })
  }

  handleSubmit = () => {
    const { activeTab } = this.state
    let values = {}
    if (activeTab === '1') values = this.formRefHas.current.getFieldsValue()
    if (activeTab === '2') values = this.formRefTag.current.getFieldsValue()
    // console.log(values)
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
      ...sortData,
    })
  }

  onInputChange = (e) => {
    this.setState({ inputURL: e.target.value })
  }
  onCheckChange = (e) => {
    // console.log(e)
    this.setState({ checkValue: e.target.checked })
  }

  addUrl = (key, item) => {
    const { tableDataLeft, tableDataRight } = this.state
    let arr = addItem(item, tableDataLeft, tableDataRight, key)
    this.setState({ tableDataRight: arr })
  }

  removeUrl = (key, item) => {
    const { tableDataRight } = this.state
    let arr = removeItem(item, tableDataRight, key)
    this.setState({ tableDataRight: arr })
  }

  handleOk = () => {
    const { onOk, location } = this.props
    const { tableDataRight, activeTab, inputURL, checkValue } = this.state
    // console.log(this.props)

    this.formRef.current
      .validateFields()
      .then((values) => {
        // console.log(values, tableDataRight)
        let obj = {}
        const { pathname } = location
        const match = pathToRegexp('/project/:id').exec(pathname)
        const id = match[1]
        if (activeTab === '1') {
          let arr = []
          tableDataRight.map((item) => arr.push(item.url))
          obj = {
            project_id: id,
            input_type: Number(activeTab),
            url: arr.join(','),
            ...values,
          }
        }
        if (activeTab === '2') {
          let arr = []
          tableDataRight.map((item) => arr.push(item.name))
          obj = {
            project_id: id,
            tag_name: arr,
            ...values,
          }
        }

        if (activeTab === '3') {
          // console.log(checkValue, values)
          let urlStr = inputURL.split('\n')
          // 去除空行
          urlStr = urlStr.filter((item) => item !== '')
          obj = {
            project_id: id,
            is_domain_resolution: checkValue,
            input_type: Number(activeTab),
            url: urlStr.join(','),
            ...values,
          }
        }
        // console.log(obj)
        onOk(obj)
      })
      .catch((errorInfo) => {
        // console.log(errorInfo)
      })
  }

  render() {
    const { onOk, form, loading, ...modalProps } = this.props
    const {
      tableDataLeft,
      pagination,
      tableDataRight,
      activeTab,
      inputURL,
      checkValue,
    } = this.state
    // console.log(pagination)

    let columns = []
    let columnsRight = []
    if (activeTab === '1') {
      columns = [
        {
          title: <Trans>url</Trans>,
          dataIndex: 'url',
          key: 'url',
          sorter: true,
        },
        {
          dataIndex: 'operation',
          key: 'operation',
          render: (text, record) => {
            return (
              <Button
                type="primary"
                disabled={
                  hasSelected(record, tableDataRight, 'url') ? true : false
                }
                onClick={() => this.addUrl('url', record)}
              >
                添加
              </Button>
            )
          },
          title: ({ sortOrder, sortColumn, filters }) => (
            <Button
              type="primary"
              disabled={!tableDataLeft.length}
              onClick={() => this.addUrl('url')}
            >
              全部添加
            </Button>
          ),
        },
      ]

      columnsRight = [
        {
          title: <Trans>url</Trans>,
          dataIndex: 'url',
          key: 'url',
        },
        {
          dataIndex: 'operation',
          key: 'operation',
          render: (text, record) => {
            return (
              <Button
                type="primary"
                onClick={() => this.removeUrl('url', record)}
              >
                移除
              </Button>
            )
          },
          title: () => (
            <Button
              type="primary"
              disabled={!tableDataRight.length}
              onClick={() => this.removeUrl('url')}
            >
              全部移除
            </Button>
          ),
        },
      ]
    }
    if (activeTab === '2') {
      columns = [
        {
          title: <Trans>tag</Trans>,
          dataIndex: 'name',
          key: 'name',
        },
        {
          dataIndex: 'operation',
          key: 'operation',
          render: (text, record) => {
            return (
              <Button
                type="primary"
                disabled={
                  hasSelected(record, tableDataRight, 'name') ? true : false
                }
                onClick={() => this.addUrl('name', record)}
              >
                添加
              </Button>
            )
          },
          title: ({ sortOrder, sortColumn, filters }) => (
            <Button
              type="primary"
              disabled={!tableDataLeft.length}
              onClick={() => this.addUrl('name')}
            >
              全部添加
            </Button>
          ),
        },
      ]

      columnsRight = [
        {
          title: <Trans>tag</Trans>,
          dataIndex: 'name',
          key: 'name',
        },
        {
          dataIndex: 'operation',
          key: 'operation',
          render: (text, record) => {
            return (
              <Button
                type="primary"
                onClick={() => this.removeUrl('name', record)}
              >
                移除
              </Button>
            )
          },
          title: () => (
            <Button
              type="primary"
              disabled={!tableDataRight.length}
              onClick={() => this.removeUrl('name')}
            >
              全部移除
            </Button>
          ),
        },
      ]
    }

    return (
      <Modal {...modalProps} onOk={this.handleOk}>
        <Form ref={this.formRef} name="control-ref" layout="horizontal">
          <FormItem
            name="name"
            rules={[{ required: true }]}
            label="资产组名称"
            labelAlign="left"
            hasFeedback
          >
            <Input placeholder="请输入资产组名称" />
          </FormItem>
        </Form>
        <Tabs
          onChange={this.handleTabChange}
          type="card"
          activeKey={activeTab}
          style={{ minHeight: '543px' }}
        >
          <TabPane tab="添加已有资产" key="1">
            <Row style={{ marginBottom: '10px' }}>
              <Col>
                <Form ref={this.formRefHas} name="control-ref" layout="inline">
                  <FormItem name="url">
                    <Search
                      placeholder="请输入url"
                      onSearch={this.handleSubmit}
                    />
                  </FormItem>
                  <Form.Item name="status">
                    <Select
                      placeholder="请选择状态"
                      allowClear
                      style={{ width: 120 }}
                      onChange={this.handleSubmit}
                    >
                      <Option value="uncheck">uncheck</Option>
                      <Option value="access">access</Option>
                      <Option value="unaccess">unaccess</Option>
                      <Option value="inactivation">inactivation</Option>
                      <Option value="comfirm_inactivation">
                        comfirm_inactivation
                      </Option>
                    </Select>
                  </Form.Item>
                </Form>
              </Col>
            </Row>
            <Row gutter={24}>
              <Col span={12}>
                <Table
                  loading={loading}
                  dataSource={tableDataLeft}
                  pagination={{
                    ...pagination,
                    showTotal: (total) => `Total ${total}`,
                  }}
                  onChange={this.onChange}
                  bordered
                  columns={columns}
                  simple
                  scroll={{ y: 330 }}
                  rowKey={(record) => record.url}
                  key="tableLeft"
                />
              </Col>
              <Col span={12}>
                <Table
                  pagination={false}
                  dataSource={tableDataRight}
                  bordered
                  columns={columnsRight}
                  simple
                  scroll={{ y: 330 }}
                  rowKey={(record) => record.url}
                  key="tableRight"
                />
              </Col>
            </Row>
          </TabPane>
          <TabPane tab="从tags添加资产" key="2">
            <Row style={{ marginBottom: '10px' }}>
              <Col>
                <Form ref={this.formRefTag} name="control-ref" layout="inline">
                  <FormItem name="query">
                    <Search
                      placeholder="请输入tag名称"
                      onSearch={this.handleSubmit}
                    />
                  </FormItem>
                </Form>
              </Col>
            </Row>
            <Row gutter={24}>
              <Col span={12}>
                <Table
                  loading={loading}
                  dataSource={tableDataLeft}
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
              </Col>
              <Col span={12}>
                <Table
                  pagination={false}
                  dataSource={tableDataRight}
                  bordered
                  columns={columnsRight}
                  simple
                  scroll={{ y: 330 }}
                  rowKey={(record) => record.name}
                  key="tableRight"
                />
              </Col>
            </Row>
          </TabPane>
          <TabPane tab="手动输入资产" key="3">
            <TextArea
              rows={8}
              placeholder="请输入url"
              value={inputURL}
              onChange={this.onInputChange}
            />
            <Checkbox checked={checkValue} onChange={this.onCheckChange}>
              是否将域名解析的IP也加入资产组中
            </Checkbox>
          </TabPane>
        </Tabs>
      </Modal>
    )
  }
}

TaskAddModal.propTypes = {
  onOk: PropTypes.func,
}

export default TaskAddModal
