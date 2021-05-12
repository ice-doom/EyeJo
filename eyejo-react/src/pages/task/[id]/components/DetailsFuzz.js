import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Input, Modal, Row, Col, Form, Button } from 'antd'
import { Trans } from '@lingui/react'
import styles from './DetailsFuzz.less'

const { Search } = Input

class TaskModal extends PureComponent {
  formRef = React.createRef()

  componentDidMount() {
    const { handleDetailsInfo } = this.props
    handleDetailsInfo()
  }

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    onFilterChange(values)
  }

  render() {
    const {
      onCancel,
      onChange,
      pagination,
      dataSource,
      ...modalProps
    } = this.props
    const columns = [
      {
        title: <Trans>Fuzz url</Trans>,
        dataIndex: 'fuzz_url',
        key: 'fuzz_url',
        sorter: true,
        render: (text) => <span>{text}</span>,
      },
      {
        title: <Trans>状态码</Trans>,
        dataIndex: 'status_code',
        key: 'status_code',
        sorter: true,
      },
      {
        title: <Trans>响应包行数</Trans>,
        dataIndex: 'lines',
        key: 'lines',
        sorter: true,
      },
      {
        title: <Trans>响应包字符数</Trans>,
        dataIndex: 'words',
        key: 'words',
        sorter: true,
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
            <Form ref={this.formRef} name="control-ref">
              <Form.Item name="fuzz_url">
                <Search
                  placeholder="请输入Fuzz url"
                  onSearch={this.handleSubmit}
                />
              </Form.Item>
            </Form>
          </Col>
        </Row>
        <Table
          onChange={onChange}
          dataSource={dataSource}
          pagination={{
            ...pagination,
            showTotal: (total) => `Total ${total} Items`,
          }}
          bordered
          columns={columns}
          simple
          rowKey={(record) => record.id}
          className={styles.table}
          scroll={{ y: 300 }}
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
