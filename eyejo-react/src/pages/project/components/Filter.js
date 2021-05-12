import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Trans } from '@lingui/react'
import { Button, Row, Col, Form, Input } from 'antd'

const { Search } = Input

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

  handleSubmit = () => {
    const { onFilterChange } = this.props
    const values = this.formRef.current.getFieldsValue()
    onFilterChange(values)
  }

  render() {
    const { onAdd, filter } = this.props
    const { query } = filter

    return (
      <Form ref={this.formRef} name="control-ref" initialValues={{ query }}>
        <Row gutter={24}>
          <Col {...ColProps} xl={{ span: 4 }} md={{ span: 8 }}>
            <Form.Item name="query">
              <Search
                placeholder="请输入项目名称"
                onSearch={this.handleSubmit}
              />
            </Form.Item>
          </Col>
          <Col
            {...TwoColProps}
            xl={{ span: 10 }}
            md={{ span: 24 }}
            sm={{ span: 24 }}
          >
            <Row type="flex" align="middle" justify="space-between">
              <div>
                <Button type="primary" shape="round" onClick={onAdd}>
                  <Trans>新增项目</Trans>
                </Button>
              </div>
            </Row>
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
