import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import {
  Form,
  Input,
  Modal,
  Divider,
  Tag,
  Select,
  Tree,
  Tabs,
  Checkbox,
  message,
} from 'antd'

const FormItem = Form.Item
const { TextArea, Search } = Input
const { Option } = Select
const { CheckableTag } = Tag
const { TabPane } = Tabs
const CheckboxGroup = Checkbox.Group

const tabsValue = [
  // 'option_sf_info',
  'option_port_scan',
  'option_fuzz',
  'option_poc_scan',
  'option_brute',
]
class TaskModal extends PureComponent {
  state = {
    selectedTags: [],
    option_pocss: [],
    tabsList: [],
    addInfo: {},
    treeData: [],
    initialTreeData: [],
    tagsData: [
      {
        text: '子域名收集',
        value: 'option_subdomain_collect',
      },
      {
        text: 'shodan&fofa',
        value: 'option_sf_info',
      },
      {
        text: '端口扫描',
        value: 'option_port_scan',
      },
      {
        text: '请求站点',
        value: 'option_request_site',
      },
      // {
      //   text: '截图',
      //   value: 'option_screen_info',
      // },
      {
        text: '登录识别',
        value: 'option_identify_login',
      },
      {
        text: 'FUZZ',
        value: 'option_fuzz',
      },
      {
        text: 'POC检测',
        value: 'option_poc_scan',
      },
      {
        text: '漏洞检测',
        value: 'option_vul',
      },
      {
        text: '服务爆破',
        value: 'option_brute',
      },
    ],
    plainOptions: [],
    checkedList: [],
    indeterminate: true,
    checkAll: false,
  }

  formRef = React.createRef()

  componentDidMount() {
    const { handleAddInfo } = this.props
    handleAddInfo().then((data) => {
      this.setState({ plainOptions: data.brute_file })
      this.setState({ addInfo: data })
      let arr = []
      arr = this.getTreeData(data.pocss)
      this.setState({ treeData: arr })
      this.setState({ initialTreeData: arr })
    })
  }

  handleChange(tag, checked) {
    // console.log(tag, checked)
    const { selectedTags, tagsData, tabsList } = this.state
    const nextSelectedTags = checked
      ? [...selectedTags, tag]
      : selectedTags.filter((t) => t !== tag)
    this.setState({ selectedTags: nextSelectedTags })

    // 点击请求站点显示截图
    if (tag === 'option_request_site') {
      let newData = [...tagsData]
      if (checked) {
        newData.splice(4, 0, {
          text: '截图',
          value: 'option_screen_info',
        })
      } else {
        newData.splice(4, 1)
      }
      this.setState({ tagsData: newData })
    }

    // 点击展示其他内容
    if (tabsValue.includes(tag)) {
      const nextTabList = checked
        ? [...tabsList, tag]
        : tabsList.filter((t) => t !== tag)
      this.setState({ tabsList: nextTabList })
    }
  }

  // 更改端口默认数据结构
  getNewPorts(data) {
    let arr = []
    for (let item in data) {
      let obj = {
        se: item,
        text: data[item],
      }
      arr.push(obj)
    }
    return arr
  }
  handleFuzzChange = (value) => {
    // console.log(this.formRef)
    const { addInfo } = this.state
    const { ports } = addInfo
    let arr = this.getNewPorts(ports)
    let text = arr.find((val) => val.se === value)['text']
    this.formRef.current.setFieldsValue({ option_ports: text })
  }

  getTreeData(data) {
    let arr = [
      {
        title: '根',
        key: 'root-0',
        children: [],
      },
    ]
    if (data) {
      for (let item in data) {
        // console.log(data[item])
        let children = data[item].map((val) => {
          return {
            title: val,
            key: item + '/' + val,
          }
        })
        let obj = {
          title: item,
          key: item,
          children: children,
        }
        arr[0].children.push(obj)
      }
    }
    return arr
  }
  onTreeChange = (value) => {
    const { initialTreeData } = this.state
    // console.log(value, initialTreeData)
    let list = initialTreeData[0].children
    const expandedKeys = list
      .map((item) => {
        let arr = item.children.filter((item) => {
          return item.title.indexOf(value) > -1
        })
        if (arr.length) {
          item.children = arr
          return item
        }
        return null
      })
      .filter((item) => item)
    // console.log(expandedKeys)

    let arr = [
      {
        title: '根',
        key: 'root-0',
        children: expandedKeys,
      },
    ]
    this.setState({ treeData: arr })
  }
  onCheck = (checkedKeys, info) => {
    // console.log('onCheck', checkedKeys, info)
    this.setState({ option_pocss: checkedKeys })
  }

  onCheckAllChange = (e) => {
    // console.log(checkedValue)
    const { plainOptions } = this.state
    this.setState({ checkedList: e.target.checked ? plainOptions : [] })
    this.setState({ indeterminate: false })
    this.setState({ checkAll: e.target.checked })
  }
  onCheckBoxChange = (list) => {
    // console.log(lsit)
    const { plainOptions } = this.state
    this.setState({ checkedList: list })
    this.setState({
      indeterminate: !!list.length && list.length < plainOptions.length,
    })
    this.setState({ checkAll: list.length === plainOptions.length })
  }

  checkName = (value) => {
    const { checkName } = this.props
    // console.log(value)
    return new Promise((resolve, reject) => {
      // 返回一个promise
      if (value) {
        checkName({ query: value })
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      } else {
        resolve(false)
      }
    })
  }

  handleOk = () => {
    const { onOk } = this.props
    let { selectedTags, option_pocss, checkedList } = this.state
    // console.log(checkedList, checkedList.join(','))
    let selectArr = {}
    selectedTags.map((val) => (selectArr[val] = true))
    if (
      selectedTags.includes('option_screen_info') &&
      !selectedTags.includes('option_request_site')
    ) {
      delete selectArr.option_screen_info
    }
    this.formRef.current
      .validateFields()
      .then((values) => {
        // console.log(values)
        // console.log(selectedTags)
        // 限制至少勾选一项内容
        if (!selectedTags.length) {
          message.error('至少要勾选一项之后再提交')
          return
        }
        // 端口扫描
        if (selectedTags.includes('option_port_scan')) {
          // 删除端口扫描中下拉选择框数据
          delete values.port_se
        }
        // 服务爆破
        if (selectedTags.includes('option_brute')) {
          if (!checkedList.length) {
            message.error('服务爆破必须选择一项')
            return
          }
          values.option_brute_type = checkedList.join(',')
        }
        // POC检测
        let index = option_pocss.findIndex((n) => n === 'root-0')
        if (index >= 0) {
          delete option_pocss[index]
        }
        option_pocss = option_pocss.filter((item) => item.includes('/'))
        const data = {
          option_pocss,
          ...values,
          ...selectArr,
        }
        // console.log(data)
        onOk(data)
      })
      .catch((errorInfo) => {})
  }

  render() {
    const { onOk, ...modalProps } = this.props
    const {
      selectedTags,
      addInfo,
      treeData,
      tabsList,
      tagsData,
      plainOptions,
      checkedList,
      checkAll,
      indeterminate,
    } = this.state
    const { fuzz_file, ports } = addInfo
    // console.log(addInfo)
    // console.log(checkAll)

    let fuzzItems = []
    if (fuzz_file) {
      fuzzItems = fuzz_file.map((item) => (
        <Option key={item} value={item}>
          {item}
        </Option>
      ))
    }
    // console.log(fuzzItems)

    let portItems = []
    if (ports) {
      let arr = this.getNewPorts(ports)
      portItems = arr.map((item) => (
        <Option key={item.se} value={item.se}>
          {item.se}
        </Option>
      ))
    }

    return (
      <Modal {...modalProps} onOk={this.handleOk}>
        <Form ref={this.formRef} name="control-ref" layout="horizontal">
          <FormItem
            name="project_name"
            rules={[
              { required: true },
              { type: 'string', max: 200 },
              {
                validator: (rule, value, callback) => {
                  // console.log('validator', res)
                  this.checkName(value).then((res) => {
                    if (res) {
                      callback('项目名称已存在')
                    } else {
                      callback()
                    }
                  })
                },
              },
            ]}
            label="项目名称"
            hasFeedback
          >
            <Input placeholder="请输入项目名称" style={{ width: '20vw' }} />
          </FormItem>
          <FormItem
            name="targets"
            label="测试目标"
            rules={[
              { required: true },
              {
                validator: (_, value) => {
                  let reg = /[\u4e00-\u9fa5]+/g
                  reg.lastIndex = 0
                  if (reg.test(value)) {
                    return Promise.reject('测试目标不能输入中文')
                  } else {
                    return Promise.resolve()
                  }
                },
              },
            ]}
          >
            <TextArea
              rows={4}
              placeholder="请输入测试目标，支持域名、IP、IP段格式"
            />
          </FormItem>
          <Divider dashed />
          {tagsData.map((tag) => (
            <CheckableTag
              key={tag.value}
              checked={selectedTags.indexOf(tag.value) > -1}
              onChange={(checked) => this.handleChange(tag.value, checked)}
            >
              {tag.text}
            </CheckableTag>
          ))}
          <Divider dashed />
          {tabsList.length ? (
            <Tabs type="card" style={{ minHeight: '260px' }}>
              {/* {tabsList.find((item) => item === 'option_sf_info') ? (
                <TabPane tab="shodan&fofa" key="1">
                  <FormItem name="option_fofa_search">
                    <Input placeholder="sf_info_search" />
                  </FormItem>
                </TabPane>
              ) : null} */}
              {tabsList.find((item) => item === 'option_port_scan') ? (
                <TabPane tab="端口扫描" key="2">
                  <FormItem label="端口类型" name="port_se">
                    <Select
                      onChange={this.handleFuzzChange}
                      style={{ width: 120 }}
                    >
                      {portItems}
                    </Select>
                  </FormItem>
                  <FormItem
                    name="option_ports"
                    label="端口"
                    rules={[{ required: true }]}
                  >
                    <TextArea placeholder="请输入要扫描的端口" rows={4} />
                  </FormItem>
                </TabPane>
              ) : null}
              {tabsList.find((item) => item === 'option_fuzz') ? (
                <TabPane tab="FUZZ" key="3">
                  <FormItem
                    name="option_fuzz_file"
                    label="fuzz"
                    rules={[{ required: true }]}
                  >
                    <Select placeholder="请选择fuzz" style={{ width: 120 }}>
                      {fuzzItems}
                    </Select>
                  </FormItem>
                </TabPane>
              ) : null}
              {tabsList.find((item) => item === 'option_poc_scan') ? (
                <TabPane tab="POC检测" key="4">
                  <Search
                    style={{ marginBottom: 8 }}
                    placeholder="Search"
                    onSearch={this.onTreeChange}
                  />
                  <Tree
                    checkable
                    defaultExpandedKeys={['root-0']}
                    onCheck={this.onCheck}
                    treeData={treeData}
                    height={160}
                  />
                </TabPane>
              ) : null}
              {tabsList.find((item) => item === 'option_brute') ? (
                <TabPane tab="服务爆破" key="5">
                  <Checkbox
                    indeterminate={indeterminate}
                    onChange={this.onCheckAllChange}
                    checked={checkAll}
                  >
                    Check all
                  </Checkbox>
                  <Divider />
                  <CheckboxGroup
                    options={plainOptions}
                    value={checkedList}
                    onChange={this.onCheckBoxChange}
                  />
                </TabPane>
              ) : null}
            </Tabs>
          ) : null}
        </Form>
      </Modal>
    )
  }
}

TaskModal.propTypes = {
  type: PropTypes.string,
  onOk: PropTypes.func,
  handleAddInfo: PropTypes.func,
}

export default TaskModal
