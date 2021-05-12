import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Table, Modal, Button, Space, Tag } from 'antd'
import {
  ContainerOutlined,
  DeleteOutlined,
  StopOutlined,
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
  handlePause = (record) => {
    const { onPauseItem } = this.props
    confirm({
      title: '你确定要暂停吗？',
      onOk() {
        onPauseItem(record.id)
      },
    })
  }

  getCodeColor = (code) => {
    // console.log(code)
    let str = ''
    switch (code) {
      case 'done':
        str = '#87d068'
        break
      case 'stop':
        str = '#faad14'
        break
      case 'vul':
        str = '#2db7f5'
        break
      default:
        str = '#108ee9'
        break
    }
    return str
  }

  getTaskSetting = (row) => {
    const taskObj = {
      subdomain_collect: '子域名收集',
      port_scan: '端口扫描',
      sf_info: 'shodan&fofa',
      screen_info: '截图',
      request_site: '请求站点',
      poc_scan: 'POC检测',
      fuzz: 'FUZZ',
      identify_login: '登录识别',
      vul: '漏洞检测',
      brute: '服务爆破',
    }
    let arr = []
    for (let item in row) {
      arr.push(taskObj[item])
    }
    return arr
  }

  handleDetails = (url) => {
    history.push(url)
  }

  render() {
    const { onDeleteItem, ...tableProps } = this.props

    const columns = [
      {
        title: <Trans>任务名称</Trans>,
        dataIndex: 'name',
        key: 'name',
        render: (text, record) => <Link to={`task/${record.id}`}>{text}</Link>,
        // render: (text) => <span>{text}</span>,
      },
      {
        title: <Trans>结果统计</Trans>,
        dataIndex: 'task_count_for_dep',
        key: 'task_count_for_dep',
        render: (row) => {
          return (
            <div>
              <p style={{ marginBottom: '0px' }}>漏洞数量：{row.vul_count}</p>
              <p style={{ marginBottom: '0px' }}>POC数量：{row.poc_count}</p>
              <p style={{ marginBottom: '0px' }}>FUZZ数量：{row.fuzz_count}</p>
              <p style={{ marginBottom: '0px' }}>
                服务爆破数量：{row.brute_count}
              </p>
            </div>
          )
        },
      },
      {
        title: <Trans>任务配置</Trans>,
        dataIndex: 'options_for_dep',
        key: 'options_for_dep',
        render: (row) => {
          return (
            <div>
              {this.getTaskSetting(row).map((item, idx) => (
                <p key={idx} style={{ marginBottom: '0px' }}>
                  {item}
                </p>
              ))}
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
        title: <Trans>结束时间</Trans>,
        dataIndex: 'end_time',
        key: 'end_time',
      },
      {
        title: <Trans>状态</Trans>,
        dataIndex: 'status',
        key: 'status',
        render: (text, record) =>
          record.status ? (
            <Tag color={this.getCodeColor(text)}>{text}</Tag>
          ) : null,
      },
      {
        title: <Trans>操作</Trans>,
        key: 'operation',
        render: (text, record) => {
          return (
            <Space>
              <Button
                type="primary"
                onClick={() => this.handleDetails(`task/${record.id}`)}
                // href={`task/${record.id}`}
                title="查看详情"
                shape="circle"
                icon={<ContainerOutlined />}
              >
                {/* 查看详情 */}
              </Button>
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
              <Button
                type="primary"
                danger
                disabled={['done', 'stop'].includes(record.status)}
                onClick={() => this.handlePause(record)}
                title="停止"
                shape="circle"
                icon={<StopOutlined />}
              >
                {/* 停止 */}
              </Button>
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
  onPauseItem: PropTypes.func,
  location: PropTypes.object,
}

export default List
