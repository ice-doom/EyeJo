import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Input, Modal, Form, Tabs, Row, Col, Select } from 'antd'
const { pathToRegexp } = require('path-to-regexp')

const { TabPane } = Tabs
const { Option } = Select

class TaskAddModal extends PureComponent {
  state = {
    tagList: [],
    activeTab: '1',
  }

  formRef = React.createRef()
  formRefHas = React.createRef()

  componentDidMount() {
    this.handleRefresh()
  }

  handleRefresh = () => {
    const { getTagInfo, location } = this.props
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    const id = match[1]
    let obj = {
      page: 1,
      limit: 10000,
      project_id: id,
    }
    // console.log(activeTab)
    getTagInfo(obj).then((data) => {
      this.setState({ tagList: data.data })
    })
  }

  handleTabChange = (tab) => {
    // console.log(tab)
    this.setState({ activeTab: tab })
  }

  handleOk = () => {
    const { onOk, selectedRowKeys, location } = this.props
    const { activeTab } = this.state
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    const id = match[1]
    // console.log(this.props)

    let obj = {
      id: selectedRowKeys,
      project_id: id,
    }
    if (activeTab === '1') {
      this.formRefHas.current
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
    const { onCancel, form, ...modalProps } = this.props
    const { activeTab, tagList } = this.state
    // console.log(pagination)

    let portItems = []
    if (tagList.length) {
      portItems = tagList.map((item) => (
        <Option key={item.name} value={item.name}>
          {item.name}
        </Option>
      ))
    }

    return (
      <Modal {...modalProps} onCancel={onCancel} onOk={this.handleOk}>
        <Tabs
          onChange={this.handleTabChange}
          type="card"
          activeKey={activeTab}
          style={{ minHeight: '200px' }}
        >
          <TabPane tab="从已有tag中添加" key="1">
            <Row style={{ marginBottom: '10px' }}>
              <Col>
                <Form ref={this.formRefHas} name="control-ref" layout="inline">
                  <Form.Item
                    name="name"
                    label="tag名称"
                    rules={[{ required: true }]}
                  >
                    <Select
                      style={{ width: '160px' }}
                      showSearch
                      placeholder="请选择tag"
                      allowClear
                      optionFilterProp="children"
                      filterOption={(input, option) =>
                        option.children
                          .toLowerCase()
                          .indexOf(input.toLowerCase()) >= 0
                      }
                    >
                      {portItems}
                    </Select>
                  </Form.Item>
                </Form>
              </Col>
            </Row>
          </TabPane>
          <TabPane tab="添加到新tag" key="2">
            <Form ref={this.formRef} name="control-ref" layout="horizontal">
              <Form.Item
                name="name"
                rules={[{ required: true }]}
                label="tag名称"
                labelAlign="left"
              >
                <Input placeholder="请输入tag名称" />
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Modal>
    )
  }
}

TaskAddModal.propTypes = {
  onCancel: PropTypes.func,
  onOk: PropTypes.func,
}

export default TaskAddModal
