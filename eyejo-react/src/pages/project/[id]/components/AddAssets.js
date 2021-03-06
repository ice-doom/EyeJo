import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import {
  Form,
  Input,
  Checkbox,
  Modal,
  Tabs,
  Row,
  Col,
  Table,
  Button,
  message,
} from 'antd'
import { Trans } from '@lingui/react'
import { hasSelected, addItem, removeItem } from '@/utils/table.js'

const FormItem = Form.Item
const { TextArea, Search } = Input
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
  }

  formRef = React.createRef()
  formRefHas = React.createRef()

  componentDidMount() {
    this.handleRefresh()
  }

  handleRefresh = (payload = {}) => {
    const { getTagInfo, currentItem } = this.props
    const { pagination } = this.state
    const { current, pageSize } = pagination

    const obj = {
      page: current,
      limit: pageSize,
      project_id: currentItem.project,
    }

    getTagInfo({ ...obj, ...payload }).then((data) => {
      // console.log(data)
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

  handleTabChange = (tab) => {
    // console.log(tab)
    this.setState({ activeTab: tab })
  }

  handleSubmit = () => {
    const values = this.formRefHas.current.getFieldsValue()
    // console.log(values)
    this.handleRefresh(values)
  }

  addUrl = (item) => {
    const { tableDataLeft, tableDataRight } = this.state
    let arr = addItem(item, tableDataLeft, tableDataRight, 'name')
    this.setState({ tableDataRight: arr })
  }

  removeUrl = (item) => {
    const { tableDataRight } = this.state
    let arr = removeItem(item, tableDataRight, 'name')
    this.setState({ tableDataRight: arr })
  }

  handleOk = () => {
    const { onOk, currentItem } = this.props
    const { tableDataRight, activeTab } = this.state
    // console.log(this.props)

    let obj = {
      project_id: currentItem.project,
      id: currentItem.id,
    }
    if (activeTab === '1') {
      if (!tableDataRight.length) {
        message.error('?????????tag???????????????')
        return
      }
      let arr = []
      tableDataRight.map((item) => arr.push(item.name))
      obj.tag_name = arr
      // console.log(obj)
      onOk(obj)
    } else {
      this.formRef.current
        .validateFields()
        .then((values) => {
          // console.log(values)
          obj = {
            ...obj,
            ...values,
          }
          // console.log(obj)
          onOk(obj)
        })
        .catch(() => {})
    }
  }

  render() {
    const { onOk, form, ...modalProps } = this.props
    const { tableDataLeft, pagination, tableDataRight, activeTab } = this.state

    const columns = [
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
              onClick={() => this.addUrl(record)}
            >
              ??????
            </Button>
          )
        },
        title: ({ sortOrder, sortColumn, filters }) => (
          <Button
            type="primary"
            disabled={!tableDataLeft.length}
            onClick={() => this.addUrl()}
          >
            ????????????
          </Button>
        ),
      },
    ]

    const columnsRight = [
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
            <Button type="primary" onClick={() => this.removeUrl(record)}>
              ??????
            </Button>
          )
        },
        title: () => (
          <Button
            type="primary"
            disabled={!tableDataRight.length}
            onClick={() => this.removeUrl()}
          >
            ????????????
          </Button>
        ),
      },
    ]

    return (
      <Modal {...modalProps} onOk={this.handleOk}>
        <Tabs
          onChange={this.handleTabChange}
          type="card"
          activeKey={activeTab}
          style={{ minHeight: '543px' }}
        >
          <TabPane tab="???tags????????????" key="1">
            <Row style={{ marginBottom: '10px' }}>
              <Col>
                <Form ref={this.formRefHas} name="control-ref" layout="inline">
                  <FormItem name="query">
                    <Search
                      placeholder="?????????tag??????"
                      onSearch={this.handleSubmit}
                    />
                  </FormItem>
                </Form>
              </Col>
            </Row>
            <Row gutter={24}>
              <Col span={12}>
                <Table
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
          <TabPane tab="??????????????????" key="2">
            <Form
              ref={this.formRef}
              initialValues={{ url: '', is_domain_resolution: false }}
              name="control-ref"
              layout="horizontal"
            >
              <FormItem
                name="url"
                rules={[{ required: true }]}
                label="url"
                labelAlign="left"
                hasFeedback
              >
                <TextArea placeholder="?????????url" rows={4} />
              </FormItem>
              <FormItem
                name="is_domain_resolution"
                labelAlign="left"
                hasFeedback
                valuePropName="checked"
              >
                <Checkbox>????????????????????????IP?????????????????????</Checkbox>
              </FormItem>
            </Form>
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
