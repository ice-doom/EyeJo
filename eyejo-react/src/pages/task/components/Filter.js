import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Trans } from '@lingui/react'
import { Button, Row, Col, Form, Input, Select } from 'antd'

const { Search } = Input
const { Option } = Select

const ColProps = {
  xs: 24,
  sm: 12,
  style: {
    marginBottom: 16,
  },
}

const TwoColProps = {
  ...ColProps,
  xl: 96,
}

class Filter extends Component {
  formRef = React.createRef()

  state = {
    projectList: [],
  }

  componentDidMount() {
    const { getProjectData, project_id } = this.props
    // console.log(project_id)
    getProjectData().then((data) => {
      // console.log(data)
      this.setState({ projectList: data })

      this.formRef.current.setFieldsValue({
        project_id,
      })
    })
  }

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    onFilterChange(values)
  }

  render() {
    const { onAdd, filter } = this.props
    const { projectList } = this.state
    const { query } = filter
    // console.log(projectList)
    let portItems = []
    if (projectList.length) {
      portItems = projectList.map((item) => (
        <Option key={item.id} value={item.id}>
          {item.name}
        </Option>
      ))
    }

    return (
      <Form ref={this.formRef} name="control-ref" initialValues={{ query }}>
        <Row gutter={24}>
          <Col {...ColProps} xl={{ span: 4 }} md={{ span: 8 }}>
            <Form.Item name="query">
              <Search
                placeholder="请输入任务名称"
                onSearch={this.handleSubmit}
              />
            </Form.Item>
          </Col>
          <Col {...ColProps} xl={{ span: 4 }} md={{ span: 8 }}>
            <Form.Item name="project_id">
              <Select
                showSearch
                placeholder="请选择项目名称"
                allowClear
                onChange={this.handleSubmit}
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >=
                  0
                }
              >
                {portItems}
              </Select>
            </Form.Item>
          </Col>
          <Col {...TwoColProps} xl={{ span: 4 }} md={{ span: 8 }}>
            <div>
              <Button type="primary" shape="round" onClick={onAdd}>
                <Trans>新增任务</Trans>
              </Button>
            </div>
          </Col>
        </Row>
      </Form>
    )
  }
}

Filter.propTypes = {
  onAdd: PropTypes.func,
  filter: PropTypes.object,
  onFilterChange: PropTypes.func,
}

export default Filter
