import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { isEmpty, cloneDeep } from 'lodash'
import {
  Table,
  Checkbox,
  Menu,
  Dropdown,
  Button,
  Row,
  Col,
  Input,
  Form,
  Image,
  Modal,
  Space,
  Popconfirm,
  Tag,
  Pagination,
  Select,
} from 'antd'
import {
  ContainerOutlined,
  DeleteOutlined,
  FolderAddOutlined,
} from '@ant-design/icons'
import { Trans, withI18n } from '@lingui/react'
import styles from './List.less'

const { confirm } = Modal
const { Option } = Select

@withI18n()
class List extends PureComponent {
  formRef = React.createRef()
  state = {
    visibleMenuSettings: false,
    checkedColumns: [],
    columns: [],
    initialColumns: [],
  }
  componentDidMount() {
    // 把子组件暴露给父组件
    // this.props.onListRef(this)

    let arr = this.getColumns()
    let showArr = arr.filter((item) => item.show)
    this.setState({ columns: showArr })
    this.setState({ initialColumns: arr })
  }

  getColumns = (sorter = {}, tabkey = null) => {
    let {
      activeKey,
      onAddAssets,
      onDetails,
      onIpSideDetails,
      onIpCDetails,
    } = this.props
    activeKey = tabkey ? tabkey : activeKey
    // console.log('getColumns', tabkey, activeKey)
    let imgUrl = window.location.origin + '/'
    let arr = []
    switch (activeKey) {
      case '1':
        arr = [
          {
            title: <Trans>网址</Trans>,
            dataIndex: 'url',
            key: 'url',
            width: 130,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'url' && sorter.order,
            render: (text) => (
              <p style={{ fontSize: '12px' }}>
                <a href={text} target="_blank" rel="noreferrer">
                  {text}
                </a>
              </p>
            ),
          },
          {
            title: <Trans>状态码</Trans>,
            dataIndex: 'status_code',
            key: 'status_code',
            width: 100,
            align: 'center',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'status_code' && sorter.order,
            render: (text, record) =>
              record.status_code ? (
                <Tag color={this.getCodeColor(text)}>{text}</Tag>
              ) : null,
          },
          {
            title: <Trans>图标</Trans>,
            dataIndex: 'icons',
            key: 'icons',
            width: 100,
            align: 'center',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'icons' && sorter.order,
            render: (text, record) =>
              record.icons ? (
                <Image
                  preview={false}
                  width={30}
                  src={imgUrl + record.icons}
                  data-hash={record.icons_hash}
                  onClick={this.onIconsClick}
                />
              ) : null,
          },
          {
            title: <Trans>标题</Trans>,
            dataIndex: 'title',
            key: 'title',
            align: 'center',
            width: 130,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'title' && sorter.order,
            render: (text) => (
              <span style={{ fontSize: '12px' }}>{text || '—'}</span>
            ),
          },
          {
            title: <Trans>响应头</Trans>,
            dataIndex: 'headers',
            key: 'headers',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'headers' && sorter.order,
            render: (text) => {
              // console.log('headers', text)
              if (!text) return []
              let headerItems = []
              let obj = JSON.parse(text)
              if (!isEmpty(obj)) {
                for (const key in obj) {
                  headerItems.push(
                    <p key={key} style={{ marginBottom: '5px' }}>
                      <span>
                        <b>{key}: </b>
                      </span>
                      <span>{obj[key]}</span>
                    </p>
                  )
                }
              }
              return (
                <div
                  style={{
                    maxWidth: '300px',
                    whiteSpace: 'nowrap',
                    overflowX: 'auto',
                    fontSize: '12px',
                  }}
                >
                  {headerItems}
                </div>
              )
            },
          },
          // {
          //   title: <Trans>创建时间</Trans>,
          //   dataIndex: 'create_time',
          //   key: 'create_time',
          //   width: 160,
          //   show: false,
          //   sorter: true,
          //   sortOrder: sorter.field === 'create_time' && sorter.order,
          // },
          {
            title: <Trans>标签</Trans>,
            dataIndex: 'tags',
            key: 'tags',
            width: 100,
            show: false,
            sorter: true,
            sortOrder: sorter.field === 'tags' && sorter.order,
          },
          {
            title: <Trans>版权所有</Trans>,
            dataIndex: 'html_copyright',
            key: 'html_copyright',
            width: 130,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'html_copyright' && sorter.order,
            render: (text) => (
              <span style={{ fontSize: '12px' }}>{text || '-'}</span>
            ),
          },
          {
            title: <Trans>证书</Trans>,
            dataIndex: 'ssl_Organization',
            key: 'ssl_Organization',
            width: 130,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'ssl_Organization' && sorter.order,
            render: (text) => (
              <span style={{ fontSize: '12px' }}>{text || '-'}</span>
            ),
          },
          {
            title: <Trans>指纹</Trans>,
            dataIndex: 'finger',
            key: 'finger',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'finger' && sorter.order,
            render: (text) => {
              // console.log('finger', text)
              if (!text) return []
              let fingerItems = []
              let obj = JSON.parse(text)
              // console.log(obj)
              if (!isEmpty(obj)) {
                for (const key in obj) {
                  if (key === 'Web servers') {
                    // console.log(obj[key])
                    let arr = []
                    obj[key].forEach((v, idx) => {
                      if (idx === 0) {
                        arr.push(
                          <p key={idx} style={{ marginBottom: '5px' }}>
                            <span>
                              <b>{key}: </b>
                            </span>
                            <span>{v}</span>
                          </p>
                        )
                      } else {
                        arr.push(
                          <p key={idx} style={{ marginBottom: '5px' }}>
                            <span style={{ visibility: 'hidden' }}>
                              <b>{key}: </b>
                            </span>
                            <span>{v}</span>
                          </p>
                        )
                      }
                    })
                    fingerItems = [fingerItems, ...arr]
                  } else {
                    fingerItems.push(
                      <p key={key} style={{ marginBottom: '5px' }}>
                        <span>
                          <b>{key}: </b>
                        </span>
                        <span>{obj[key]}</span>
                      </p>
                    )
                  }
                }
              }
              if (fingerItems.length === 0) fingerItems = '-'
              return (
                <div
                  style={{
                    maxWidth: '180px',
                    whiteSpace: 'nowrap',
                    overflowX: 'auto',
                    fontSize: '12px',
                  }}
                >
                  {fingerItems}
                </div>
              )
              // return fingerItems
            },
          },
          {
            title: <Trans>截图</Trans>,
            dataIndex: 'pic',
            key: 'pic',
            align: 'center',
            // width: 200,
            width: 340,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'pic' && sorter.order,
            render: (text, record) =>
              record.pic ? (
                <Image
                  preview={false}
                  width={300}
                  style={{ border: '2px solid #ccc' }}
                  src={imgUrl + record.pic}
                  data-hash={record.pic_hash}
                  onClick={this.onImgClick}
                />
              ) : null,
          },
        ]
        break
      case '2':
        arr = [
          {
            title: <Trans>子域名</Trans>,
            dataIndex: 'subdomain',
            key: 'subdomain',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'subdomain' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>主域名</Trans>,
            dataIndex: 'm_domain',
            key: 'm_domain',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'm_domain' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>来源</Trans>,
            dataIndex: 'source',
            key: 'source',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'source' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>IP地址</Trans>,
            dataIndex: 'ip',
            key: 'ip',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'ip' && sorter.order,
            render: (text) => (
              <span>{text && text.ip_address ? text.ip_address : ''}</span>
            ),
            // render: (text) => {
            //   // console.log('headers', text)
            //   if (!text) return []
            //   let headerItems = []
            //   if (!isEmpty(text)) {
            //     text.map((item, key) => {
            //       headerItems.push(<p key={key}>{item}</p>)
            //     })
            //   }
            //   return <div>{headerItems}</div>
            // },
          },
        ]
        break
      case '3':
        arr = [
          {
            title: <Trans>IP地址</Trans>,
            dataIndex: 'ip_address',
            key: 'ip_address',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'ip_address' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>IP所属国家/省/城市</Trans>,
            dataIndex: 'country',
            key: 'country',
            show: true,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: (
                  <span>
                    {(row.country || '') +
                      ' / ' +
                      (row.regionName || '') +
                      ' / ' +
                      (row.city || '')}
                  </span>
                ),
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>IP所属运营商</Trans>,
            dataIndex: 'isp',
            key: 'isp',
            width: 200,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'isp' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>ASN号</Trans>,
            dataIndex: 'asn',
            key: 'asn',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'asn' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>CDN</Trans>,
            dataIndex: 'cdn',
            key: 'cdn',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'cdn' && sorter.order,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let obj = {
                children: value === 0 ? '不存在' : '存在',
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
          {
            title: <Trans>来源</Trans>,
            dataIndex: 'source',
            key: 'source',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'source' && sorter.order,
          },
          {
            title: <Trans>端口</Trans>,
            dataIndex: 'port',
            key: 'port',
            show: true,
          },
          {
            title: <Trans>协议</Trans>,
            dataIndex: 'protocol',
            key: 'protocol',
            show: true,
          },
          {
            title: <Trans>组件</Trans>,
            dataIndex: 'product',
            key: 'product',
            show: true,
          },
          {
            title: <Trans>版本</Trans>,
            dataIndex: 'version',
            key: 'version',
            show: true,
          },
          {
            title: <Trans>操作</Trans>,
            key: '操作',
            show: true,
            sorter: false,
            render: (value, row, index) => {
              // console.log(value, row, index)
              let elm = (
                <Space>
                  <Button type="primary" onClick={() => onIpSideDetails(row)}>
                    查看旁站
                  </Button>
                  <Button type="primary" onClick={() => onIpCDetails(row)}>
                    查看C段
                  </Button>
                </Space>
              )
              let obj = {
                children: elm,
                props: {},
              }
              obj.props.rowSpan = row.colSpan
              return obj
            },
          },
        ]
        break
      case '4':
        arr = [
          {
            title: <Trans>URL</Trans>,
            dataIndex: 'url',
            key: 'url',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'url' && sorter.order,
          },
          {
            title: <Trans>登录接口</Trans>,
            dataIndex: 'crawl_url',
            key: 'crawl_url',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'crawl_url' && sorter.order,
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>请求方法</Trans>,
            dataIndex: 'method',
            key: 'method',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'method' && sorter.order,
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>请求头</Trans>,
            dataIndex: 'headers',
            key: 'headers',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'headers' && sorter.order,
            render: (text) => {
              // console.log('headers', text)
              if (!text) return []
              let headerItems = []
              let obj = JSON.parse(text)
              if (!isEmpty(obj)) {
                for (const key in obj) {
                  headerItems.push(
                    <p key={key} style={{ marginBottom: '5px' }}>
                      <span>
                        <b>{key}:</b>
                      </span>
                      <span>{obj[key]}</span>
                    </p>
                  )
                }
              }
              return (
                <div
                  style={{
                    maxWidth: '300px',
                    whiteSpace: 'nowrap',
                    overflowX: 'auto',
                    fontSize: '12px',
                  }}
                >
                  {headerItems}
                </div>
              )
            },
          },
          {
            title: <Trans>请求体</Trans>,
            dataIndex: 'req_data',
            key: 'req_data',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'req_data' && sorter.order,
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>创建时间</Trans>,
            dataIndex: 'create_time',
            key: 'create_time',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'create_time' && sorter.order,
            render: (text) => <span>{text}</span>,
          },
        ]
        break
      case '5':
        arr = [
          {
            title: <Trans>资产组名称</Trans>,
            dataIndex: 'name',
            key: 'name',
            ellipsis: true,
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'name' && sorter.order,
            render: (text) => <span>{text}</span>,
          },
          {
            title: <Trans>创建时间</Trans>,
            dataIndex: 'create_time',
            key: 'create_time',
            show: true,
            sorter: true,
            sortOrder: sorter.field === 'create_time' && sorter.order,
          },
          {
            title: <Trans>操作</Trans>,
            key: '操作',
            show: true,
            sorter: false,
            render: (text, record) => {
              return (
                <Space>
                  <Button
                    type="primary"
                    onClick={() => onDetails(record)}
                    title="查看详情"
                    shape="circle"
                    icon={<ContainerOutlined />}
                  >
                    {/* 查看详情 */}
                  </Button>
                  <Button
                    type="primary"
                    onClick={() => onAddAssets(record)}
                    title="新增资产"
                    shape="circle"
                    icon={<FolderAddOutlined />}
                  >
                    {/* 新增资产 */}
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
                </Space>
              )
            },
          },
        ]
        break
      default:
        break
    }
    return arr
  }
  // 父组件触发该方法：用于解决排序切换tab排序图标不清空
  resetColumns = (activeKey) => {
    // console.log(666)
    // this.formRef.current.resetFields()
    // let arr = this.getColumns({}, activeKey)
    // let showArr = arr.filter((item) => item.show)
    // this.setState({ columns: showArr })
    // this.formRef.current.setFieldsValue({
    //   url: '',
    // })
  }

  getCodeColor = (code) => {
    // console.log(code)
    let str = '#1890ff'
    if (code.startsWith('2')) {
      str = '#52c41a'
    }
    if (code.startsWith('3')) {
      str = '#1890ff'
    }
    if (code.startsWith('4')) {
      str = '#faad14'
    }
    if (code.startsWith('5')) {
      str = '#ff4d4f'
    }
    return str
  }
  onIconsClick = (e) => {
    // console.log('Content: ',e.currentTarget.dataset.id)
    const { onFilterChange } = this.props
    let hash = e.currentTarget.dataset.hash
    this.formRef.current.setFieldsValue({
      icons_hash: hash,
    })
    onFilterChange({ icons_hash: hash })
  }
  onImgClick = (e) => {
    // console.log('Content: ',e.currentTarget.dataset.id)
    const { onFilterChange } = this.props
    let hash = e.currentTarget.dataset.hash
    this.formRef.current.setFieldsValue({
      pic_hash: hash,
    })
    onFilterChange({ pic_hash: hash })
  }
  handleCheckboxChange = (e) => {
    // console.log(e, e.target.id)
    let checkedColumns = this.state.checkedColumns
    let filtered = this.state.initialColumns

    if (e.target.checked) {
      checkedColumns = checkedColumns.filter((id) => {
        return id !== e.target.id
      })
    } else if (!e.target.checked) {
      checkedColumns.push(e.target.id)
    }
    for (let i = 0; i < checkedColumns.length; i++)
      // eslint-disable-next-line no-loop-func
      filtered = filtered.filter((el) => {
        return el.dataIndex !== checkedColumns[i]
      })

    this.setState({ columns: filtered, checkedColumns: checkedColumns })
  }

  handleVisibleChange = (flag) => {
    this.setState({ visibleMenuSettings: flag })
  }

  getMenu = () => {
    const { initialColumns } = this.state
    const menuItems = initialColumns.map((item, idx) => (
      <Menu.Item key={idx}>
        <Checkbox
          id={item.key}
          defaultChecked={item.show}
          onChange={this.handleCheckboxChange}
        >
          {item.title}
        </Checkbox>
      </Menu.Item>
    ))
    return <Menu>{menuItems}</Menu>
  }

  getPlaceholder = () => {
    const { activeKey } = this.props
    let str = ''
    switch (activeKey) {
      case '2':
        str = '请输入子域名'
        break
      case '4':
        str = '请输入url'
        break
      case '5':
        str = '请输入资产组名称'
        break
      default:
        break
    }
    return str
  }

  getTableData = (dataSource, activeKey) => {
    let arr = []
    arr = cloneDeep(dataSource)
    // console.log(arr)
    if (activeKey === '2') {
      let list = []
      arr.forEach((item) => {
        // console.log(item.ip_domain_relationship_set)
        if (
          item.ip_domain_relationship_set &&
          item.ip_domain_relationship_set.length
        ) {
          item.ip_domain_relationship_set.forEach((val, idx) => {
            // console.log(item.id, idx, item.id + '_' + idx)
            let obj = {
              ...item,
              ...val,
              id: item.id + '_' + idx,
            }
            if (idx === 0) {
              obj.colSpan = item.ip_domain_relationship_set.length
            } else {
              obj.colSpan = 0
            }
            list.push(obj)
          })
        } else {
          list.push(item)
        }
      })
      // console.log(list)
      arr = list
    }
    if (activeKey === '3') {
      let list = []
      arr.forEach((item) => {
        // console.log(item.port_set)
        if (item.port_set && item.port_set.length) {
          item.port_set.forEach((val, idx) => {
            // console.log(idx)
            let obj = {
              ...item,
              ...val,
            }
            if (idx === 0) {
              obj.colSpan = item.port_set.length
            } else {
              obj.colSpan = 0
            }
            list.push(obj)
          })
        } else {
          list.push(item)
        }
      })
      // console.log(list)
      arr = list
    }
    if (activeKey === '4') {
      let list = []
      arr.forEach((item) => {
        // console.log(item.login_site_set)
        let tempObj = item.login_site_set
        // console.log(tempObj)
        if (tempObj && tempObj.length) {
          let obj = {
            ...item,
            id: tempObj[0].id,
            url: tempObj[0].url,
            create_time: tempObj[0].create_time,
          }
          list.push(obj)
        } else {
          list.push(item)
        }
      })
      // console.log(list)
      arr = list
    }
    // console.log(arr)
    return arr
  }

  // 表格排序触发方法
  onChange = (page, filters, sorter) => {
    // console.log(sorter)
    const { onSortChange } = this.props
    let obj = {}
    if (sorter.order) {
      obj = {
        field: sorter.field,
        order: sorter.order === 'ascend' ? 'asc' : 'desc',
      }
    }
    onSortChange(obj)

    let arr = this.getColumns(sorter)
    let showArr = arr.filter((item) => item.show)
    this.setState({ columns: showArr })
  }

  // 使用单独分页组件，使用表格自带分页和表格合并两个会产生冲突，造成显示异常
  onShowSizeChange = (current, pageSize) => {
    // console.log(current, pageSize)
    const { onPaginaionChange } = this.props
    let obj = {
      page: current,
      limit: pageSize,
    }
    onPaginaionChange(obj)
  }

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    // console.log(values)
    onFilterChange(values)
  }
  handleReset = () => {
    const { onFilterChange } = this.props
    this.formRef.current.resetFields()
    const values = this.formRef.current.getFieldsValue()
    // console.log(values)
    onFilterChange(values)
  }

  handleDel = (record) => {
    const { onDeleteItem } = this.props
    confirm({
      title: '你确定要删除吗？',
      onOk() {
        onDeleteItem(record.id)
      },
    })
  }

  render() {
    const {
      activeKey,
      selectedRowKeys,
      onAdd,
      onTagsSetting,
      onAddTags,
      onExportUrl,
      onDeleteList,
      dataSource,
      tagsList,
      ...tableProps
    } = this.props
    // console.log(tableProps.pagination)
    // console.log('render')
    let menu = this.getMenu()
    let placeholder = this.getPlaceholder()
    if (!['1', '5'].includes(activeKey)) {
      delete tableProps.rowSelection
    }

    const tableData = this.getTableData(dataSource, activeKey)

    let portItems = []
    if (tagsList.length) {
      portItems = tagsList.map((item) => (
        <Option key={item.name} value={item.name}>
          {item.name}
        </Option>
      ))
    }

    return (
      <>
        <Row gutter={24} justify="space-between">
          <Col style={{ marginBottom: '10px' }}>
            <Row gutter={24}>
              <Col>
                <Form
                  ref={this.formRef}
                  name="control-ref"
                  // initialValues={{ query }}
                  layout="inline"
                >
                  {activeKey === '1' ? (
                    <>
                      <Form.Item name="icons_hash">
                        <Input placeholder="请输入图标的hash值" />
                      </Form.Item>
                      <Form.Item name="pic_hash">
                        <Input placeholder="请输入截图的hash值" />
                      </Form.Item>
                      <Form.Item name="url">
                        <Input placeholder="请输入网址" />
                      </Form.Item>
                      <Form.Item name="title">
                        <Input placeholder="请输入网址标题" />
                      </Form.Item>
                      <Form.Item name="finger">
                        <Input placeholder="请输入网站指纹" />
                      </Form.Item>
                      <Form.Item name="tag_name">
                        <Select
                          showSearch
                          placeholder="请选择tag"
                          allowClear
                          onChange={this.handleSubmit}
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
                    </>
                  ) : null}
                  {['2'].includes(activeKey) ? (
                    <>
                      <Form.Item name="subdomain">
                        <Input placeholder={placeholder} />
                      </Form.Item>
                      <Form.Item name="ip_address">
                        <Input placeholder="请输入IP地址" />
                      </Form.Item>
                    </>
                  ) : null}
                  {activeKey === '3' ? (
                    <>
                      <Form.Item name="ip_address">
                        <Input placeholder="请输入IP地址" />
                      </Form.Item>
                      <Form.Item name="port">
                        <Input placeholder="请输入端口号" />
                      </Form.Item>
                      <Form.Item name="protocol">
                        <Input placeholder="请输入协议" />
                      </Form.Item>
                    </>
                  ) : null}
                  {['4'].includes(activeKey) ? (
                    <Form.Item name="url">
                      <Input placeholder={placeholder} />
                    </Form.Item>
                  ) : null}
                  {['5'].includes(activeKey) ? (
                    <Form.Item name="name">
                      <Input placeholder={placeholder} />
                    </Form.Item>
                  ) : null}

                  <Form.Item>
                    <Button
                      type="primary"
                      shape="round"
                      onClick={() => this.handleSubmit()}
                    >
                      搜索
                    </Button>
                  </Form.Item>
                  <Form.Item>
                    <Button
                      type="primary"
                      shape="round"
                      onClick={() => this.handleReset()}
                    >
                      重置
                    </Button>
                  </Form.Item>
                </Form>
              </Col>
              {activeKey === '5' ? (
                <Col>
                  <Button type="primary" shape="round" onClick={onAdd}>
                    <Trans>新增资产组</Trans>
                  </Button>
                </Col>
              ) : null}
            </Row>
          </Col>
          <Col>
            <Space>
              {activeKey === '1' ? (
                <>
                  <Button type="primary" shape="round" onClick={onTagsSetting}>
                    tags管理
                  </Button>
                  <Button type="primary" shape="round" onClick={onExportUrl}>
                    导出excel
                  </Button>
                </>
              ) : null}
              <Dropdown
                overlay={menu}
                onVisibleChange={this.handleVisibleChange}
                visible={this.state.visibleMenuSettings}
              >
                <Button type="primary" shape="round">
                  显示列
                </Button>
              </Dropdown>
            </Space>
          </Col>
        </Row>
        {(activeKey === '5' && selectedRowKeys.length) > 0 && (
          <Row
            style={{
              marginTop: 15,
              marginBottom: 15,
              textAlign: 'right',
              fontSize: 13,
            }}
          >
            <Col>
              {`Selected ${selectedRowKeys.length} items `}
              <Popconfirm
                title="你确定要删除吗？"
                placement="left"
                onConfirm={onDeleteList}
              >
                <Button type="primary" style={{ marginLeft: 8 }}>
                  删除
                </Button>
              </Popconfirm>
            </Col>
          </Row>
        )}
        {(activeKey === '1' && selectedRowKeys.length) > 0 && (
          <Row
            style={{
              marginTop: 15,
              marginBottom: 15,
              textAlign: 'right',
              fontSize: 13,
            }}
          >
            <Col>
              {`Selected ${selectedRowKeys.length} items `}
              <Button
                type="primary"
                shape="round"
                style={{ marginLeft: 8 }}
                onClick={onAddTags}
              >
                添加到tags
              </Button>
            </Col>
          </Row>
        )}
        <Table
          {...tableProps}
          dataSource={tableData}
          pagination={false}
          onChange={this.onChange}
          // pagination={{
          //   ...tableProps.pagination,
          //   showTotal: (total) => `Total ${total} Items`,
          // }}
          className={styles.table}
          bordered
          // scroll={{ x: 1200 }}
          columns={this.state.columns}
          simple
          rowKey={(record) => record.id}
          style={{ marginTop: 8 }}
        />
        {tableProps.pagination && tableProps.pagination.total ? (
          <Pagination
            {...tableProps.pagination}
            showTotal={(total) => `Total ${total} Items`}
            style={{ textAlign: 'right', marginTop: '20px' }}
            onChange={this.onShowSizeChange}
          />
        ) : null}
      </>
    )
  }
}

List.propTypes = {
  location: PropTypes.object,
  onFilterChange: PropTypes.func,
  onPaginaionChange: PropTypes.func,
  onSortChange: PropTypes.func,
  onAdd: PropTypes.func,
  onTagsSetting: PropTypes.func,
  onAddTags: PropTypes.func,
  onDeleteList: PropTypes.func,
  onDetails: PropTypes.func,
  onAddAssets: PropTypes.func,
  onIpSideDetails: PropTypes.func,
  onIpCDetails: PropTypes.func,
  onDeleteItem: PropTypes.func,
}

export default List
