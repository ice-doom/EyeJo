import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Row, Col, Input, Form, Button } from 'antd'
import { ContainerOutlined } from '@ant-design/icons'
import { Trans, withI18n } from '@lingui/react'
import styles from './List.less'

const { Search } = Input

@withI18n()
class List extends PureComponent {
  formRef = React.createRef()
  getColumns = (activeKey) => {
    const { onDetails } = this.props
    let arr = []
    switch (activeKey) {
      case '1':
        arr = [
          {
            title: <Trans>URL</Trans>,
            dataIndex: 'url',
            key: 'url',
            width: 100,
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>payload</Trans>,
            dataIndex: 'payload',
            key: 'payload',
            width: 100,
          },
          {
            title: <Trans>请求数据</Trans>,
            dataIndex: 'snapshot_req',
            key: 'snapshot_req',
            width: 200,
          },
          {
            title: <Trans>漏洞类型</Trans>,
            dataIndex: 'vulntype',
            key: 'vulntype',
            width: 100,
          },
        ]
        break
      case '2':
        arr = [
          {
            title: <Trans>URL</Trans>,
            dataIndex: 'poc_url',
            key: 'poc_url',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>POC名称</Trans>,
            dataIndex: 'poc_name',
            key: 'poc_name',
          },
          {
            title: <Trans>检验信息</Trans>,
            dataIndex: 'verifyinfo',
            key: 'verifyinfo',
          },
          {
            title: <Trans>检测结果</Trans>,
            dataIndex: 'result_code',
            key: 'result_code',
          },
        ]
        break
      case '3':
        arr = [
          {
            title: <Trans>url</Trans>,
            dataIndex: 'url',
            key: 'url',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>count</Trans>,
            dataIndex: 'count',
            key: 'count',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>操作</Trans>,
            key: '操作',
            show: true,
            sorter: false,
            render: (text, record) => {
              return (
                <Button
                  type="primary"
                  onClick={() => onDetails(record)}
                  title="查看详情"
                  shape="circle"
                  icon={<ContainerOutlined />}
                >
                  {/* 查看详情 */}
                </Button>
              )
            },
          },
        ]
        break
      case '4':
        arr = [
          {
            title: <Trans>ip地址</Trans>,
            dataIndex: 'ip_address',
            key: 'ip_address',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>端口</Trans>,
            dataIndex: 'port',
            key: 'port',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>服务</Trans>,
            dataIndex: 'service',
            key: 'service',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>用户名</Trans>,
            dataIndex: 'username',
            key: 'username',
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>密码</Trans>,
            dataIndex: 'password',
            key: 'password',
            render: (text) => <span>{text}</span>,
          },
        ]
        break
      default:
        break
    }
    return arr
  }
  getPlaceholder = () => {
    const { activeKey } = this.props
    let str = ''
    switch (activeKey) {
      case '1':
        str = '请输入url'
        break
      case '2':
        str = '请输入url'
        break
      case '3':
        str = '请输入url'
        break
      default:
        break
    }
    return str
  }

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    onFilterChange(values)
  }

  render() {
    const { activeKey, filter, ...tableProps } = this.props
    const { query } = filter
    let columns = this.getColumns(activeKey)
    let placeholder = this.getPlaceholder()

    return (
      <>
        <Row gutter={24}>
          <Col>
            <Form
              ref={this.formRef}
              name="control-ref"
              initialValues={{ query }}
            >
              {['1', '3'].includes(activeKey) ? (
                <Form.Item name="url">
                  <Search
                    placeholder={placeholder}
                    onSearch={this.handleSubmit}
                  />
                </Form.Item>
              ) : null}
              {activeKey === '2' ? (
                <Form.Item name="poc_url">
                  <Search
                    placeholder={placeholder}
                    onSearch={this.handleSubmit}
                  />
                </Form.Item>
              ) : null}
            </Form>
          </Col>
        </Row>
        <Table
          {...tableProps}
          pagination={{
            ...tableProps.pagination,
            showTotal: (total) => `Total ${total} Items`,
          }}
          className={styles.table}
          bordered
          columns={columns}
          simple
          rowKey={(record) => record.id || record.url}
        />
      </>
    )
  }
}

List.propTypes = {
  location: PropTypes.object,
  filter: PropTypes.object,
  onFilterChange: PropTypes.func,
  onDetails: PropTypes.func,
}

export default List
