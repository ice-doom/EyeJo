import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import {
  Table,
  Input,
  Modal,
  Row,
  Col,
  Form,
  Button,
  Popconfirm,
  Select,
} from 'antd'
import { DeleteOutlined } from '@ant-design/icons'
import { Trans } from '@lingui/react'

const { Search } = Input
const { Option } = Select
const { confirm } = Modal

class TaskModal extends PureComponent {
  formRef = React.createRef()

  state = {
    selectedRowKeys: [],
  }

  componentDidMount() {
    const { handleDetailsInfo } = this.props
    handleDetailsInfo()
  }

  onSelectChange = (keys) => {
    // console.log(keys)
    this.setState({ selectedRowKeys: keys })
  }

  handleDel = (item) => {
    // console.log(item)
    const { onDeleteItem } = this.props
    confirm({
      title: '你确定要删除吗？',
      onOk() {
        onDeleteItem(item.id)
      },
    })
  }
  handleDeleteList = () => {
    const { selectedRowKeys } = this.state
    const { onDeleteList } = this.props
    onDeleteList(selectedRowKeys)
  }

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    onFilterChange(values)
  }

  render() {
    const {
      currentItem,
      onCancel,
      onChange,
      pagination,
      dataSource,
      ...modalProps
    } = this.props
    const { selectedRowKeys } = this.state
    const rowSelection = {
      selectedRowKeys,
      onChange: this.onSelectChange,
    }
    const columns = [
      {
        title: <Trans>名称</Trans>,
        dataIndex: 'name',
        key: 'name',
        render: (text) => <span>{currentItem.name}</span>,
      },
      {
        title: <Trans>url</Trans>,
        dataIndex: 'url',
        key: 'url',
        sorter: true,
      },
      {
        title: <Trans>状态</Trans>,
        dataIndex: 'status',
        key: 'status',
        sorter: true,
      },
      {
        title: <Trans>创建时间</Trans>,
        dataIndex: 'create_time',
        key: 'create_time',
        sorter: true,
      },
      {
        title: <Trans>操作</Trans>,
        key: '操作',
        show: true,
        sorter: false,
        width: 60,
        render: (text, record) => {
          return (
            <Button
              type="primary"
              danger
              onClick={() => this.handleDel(record)}
              title="删除"
              shape="circle"
              icon={<DeleteOutlined />}
            >
              {/* 删除 */}
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
        <Row gutter={24}>
          <Col>
            <Form ref={this.formRef} name="control-ref" layout="inline">
              <Form.Item name="url">
                <Search placeholder="请输入url" onSearch={this.handleSubmit} />
              </Form.Item>
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
        {selectedRowKeys.length > 0 && (
          <Row style={{ marginBottom: 24, textAlign: 'right', fontSize: 13 }}>
            <Col>
              {`Selected ${selectedRowKeys.length} items `}
              <Popconfirm
                title="你确定要删除吗？"
                placement="left"
                onConfirm={this.handleDeleteList}
              >
                <Button type="primary" style={{ marginLeft: 8 }}>
                  Remove
                </Button>
              </Popconfirm>
            </Col>
          </Row>
        )}
        <Table
          onChange={onChange}
          dataSource={dataSource}
          pagination={{
            ...pagination,
            showTotal: (total) => `Total ${total} Items`,
          }}
          rowSelection={rowSelection}
          bordered
          columns={columns}
          simple
          scroll={{ y: 300 }}
          rowKey={(record) => record.id}
          style={{ marginTop: 8 }}
        />
      </Modal>
    )
  }
}

TaskModal.propTypes = {
  onCancel: PropTypes.func,
}

export default TaskModal
