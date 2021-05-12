import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Modal, Button, Spin } from 'antd'
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
        title: <Trans>ip</Trans>,
        dataIndex: 'ip_address',
        key: 'ip_address',
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
        <Spin
          spinning={loading}
          tip="正在检测C段，请勿未检测完毕重新点开，避免再次检测C段"
        >
          <Table
            // loading={loading}
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
        </Spin>
      </Modal>
    )
  }
}

TaskModal.propTypes = {
  onCancel: PropTypes.func,
}

export default TaskModal
