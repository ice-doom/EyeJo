import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Modal, Button } from 'antd'
import { Trans } from '@lingui/react'

class TaskModal extends PureComponent {
  formRef = React.createRef()

  componentDidMount() {
    const { handleDetailsInfo } = this.props
    handleDetailsInfo()
  }

  render() {
    const {
      loading,
      onCancel,
      onChange,
      pagination,
      dataSource,
      ...modalProps
    } = this.props
    const columns = [
      {
        title: <Trans>域名</Trans>,
        dataIndex: 'subdomain',
        key: 'subdomain',
        sorter: true,
      },
      {
        title: <Trans>标题</Trans>,
        dataIndex: 'title',
        key: 'title',
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
        <Table
          loading={loading}
          onChange={onChange}
          dataSource={dataSource}
          pagination={{
            ...pagination,
            showTotal: (total) => `Total ${total} Items`,
          }}
          bordered
          columns={columns}
          simple
          scroll={{ y: 400 }}
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
