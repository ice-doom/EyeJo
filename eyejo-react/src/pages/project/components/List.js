import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Modal, Button, Space } from 'antd'
import {
  ContainerOutlined,
  DeleteOutlined,
  BarsOutlined,
} from '@ant-design/icons'
import { Trans, withI18n } from '@lingui/react'
import { Link, history } from 'umi'
import styles from './List.less'

const { confirm } = Modal

@withI18n()
class List extends PureComponent {
  handleDel = (record) => {
    const { onDeleteItem } = this.props
    confirm({
      title: '你确定要删除吗？',
      onOk() {
        onDeleteItem(record.id)
      },
    })
  }

  handleDetails = (url) => {
    history.push(url)
  }
  handleTask = (record) => {
    // console.log(record)
    history.push({
      pathname: '/task',
      params: {
        project_id: record.id,
      },
    })
  }

  render() {
    const { ...tableProps } = this.props

    const columns = [
      {
        title: <Trans>项目名称</Trans>,
        dataIndex: 'name',
        key: 'name',
        render: (text, record) => (
          <Link to={`project/${record.id}`}>{text}</Link>
        ),
        // render: (text) => <span>{text}</span>,
      },
      {
        title: <Trans>结果统计</Trans>,
        dataIndex: 'project_count_for_dep',
        key: 'project_count_for_dep',
        render: (row) => {
          return (
            <div>
              <p style={{ marginBottom: '0px' }}>站点数量：{row.site_count}</p>
              <p style={{ marginBottom: '0px' }}>
                域名数量：{row.domain_count}
              </p>
              <p style={{ marginBottom: '0px' }}>IP数量：{row.ip_count}</p>
            </div>
          )
        },
      },
      {
        title: <Trans>创建时间</Trans>,
        dataIndex: 'create_time',
        key: 'create_time',
      },
      {
        title: <Trans>操作</Trans>,
        key: 'operation',
        fixed: 'right',
        render: (text, record) => {
          return (
            <Space>
              <Button
                type="primary"
                onClick={() => this.handleDetails(`project/${record.id}`)}
                // href={`project/${record.id}`}
                title="查看详情"
                shape="circle"
                icon={<ContainerOutlined />}
              ></Button>
              <Button
                type="primary"
                onClick={() => this.handleTask(record)}
                title="任务列表"
                shape="circle"
                icon={<BarsOutlined />}
              ></Button>
              <Button
                type="primary"
                danger
                onClick={() => this.handleDel(record)}
                title="删除"
                shape="circle"
                icon={<DeleteOutlined />}
              ></Button>
            </Space>
          )
        },
      },
    ]

    return (
      <Table
        {...tableProps}
        pagination={{
          ...tableProps.pagination,
          showTotal: (total) => `Total ${total} Items`,
        }}
        className={styles.table}
        bordered
        scroll={{ x: 1200 }}
        columns={columns}
        simple
        rowKey={(record) => record.id}
      />
    )
  }
}

List.propTypes = {
  onDeleteItem: PropTypes.func,
  location: PropTypes.object,
}

export default List
