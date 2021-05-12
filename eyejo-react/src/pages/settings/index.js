import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Page } from 'components'
import { connect } from 'umi'
import { Button, Form, Input, InputNumber, Select, message } from 'antd'
import { withI18n } from '@lingui/react'
import { transform, isEqual, isObject, isEmpty } from 'lodash'

const { Option } = Select
const FormItem = Form.Item

@withI18n()
@connect(({ loading, settings }) => ({ loading, settings }))
class Setting extends PureComponent {
  formRef = React.createRef()

  difference = (object, base) => {
    function changes(object, base) {
      return transform(object, function (result, value, key) {
        if (!isEqual(value, base[key])) {
          // console.log(key, value)
          result[key] =
            isObject(value) && isObject(base[key])
              ? changes(value, base[key])
              : value
        }
      })
    }
    return changes(object, base)
  }

  render() {
    const { settings, dispatch, loading } = this.props
    const { settingFormData, initialFormData } = settings
    // console.log('render', settingFormData)

    const handleOk = () => {
      this.formRef.current.validateFields().then((values) => {
        // console.log(values, initialFormData)
        let diff = this.difference(values, initialFormData)
        for (let item in diff) {
          // console.log(item, isEmpty(diff[item]))
          if (isEmpty(diff[item])) {
            delete diff.item
          }
        }
        // console.log(diff)
        dispatch({
          type: 'settings/edit',
          payload: {
            diff,
            values,
          },
        }).then((res) => {
          if (res.success) {
            message.success('修改成功')
          }
        })
      })
    }

    return (
      <Page inner>
        <Form
          labelCol={{ xxl: { span: 3 }, xl: { span: 4 } }}
          wrapperCol={{ span: 8 }}
          style={{ paddingLeft: 50 }}
          initialValues={settingFormData}
          ref={this.formRef}
          name="nest-messages"
        >
          <h3>爬虫</h3>
          <FormItem name={['crawl', 'to_poc']} label="目录结果交给POC检测">
            <Select style={{ width: 130 }}>
              <Option key={true} value={true}>
                true
              </Option>
              <Option key={false} value={false}>
                false
              </Option>
            </Select>
          </FormItem>

          <h3>fofa_api</h3>
          <FormItem
            name={['fofa_api', 'email']}
            label="邮箱"
            // rules={[
            //   {
            //     type: 'email',
            //   },
            // ]}
          >
            <Input />
          </FormItem>
          <FormItem name={['fofa_api', 'key']} label="key">
            <Input />
          </FormItem>

          <h3>IP信息收集方式</h3>
          <FormItem name={['get_ip_info', 'action']} label="action">
            <Select style={{ width: 130 }}>
              <Option key="getlite2" value="getlite2">
                getlite2
              </Option>
              <Option key="ip-api" value="ip-api">
                ip-api
              </Option>
            </Select>
          </FormItem>

          <h3>请求站点</h3>
          <FormItem
            name={['request_site', 'concurrent']}
            rules={[
              {
                type: 'number',
              },
            ]}
            label="并发数量"
          >
            <InputNumber min={1} max={200} />
          </FormItem>
          <FormItem name={['request_site', 'max_tries']} label="失败尝试次数">
            <Select style={{ width: 130 }}>
              <Option key={1} value={1}>
                {1}
              </Option>
              <Option key={0} value={0}>
                {0}
              </Option>
            </Select>
          </FormItem>

          <h3>截图</h3>
          <FormItem
            name={['screen', 'concurrent']}
            rules={[
              {
                type: 'number',
              },
            ]}
            label="并发数量"
          >
            <InputNumber min={1} max={40} />
          </FormItem>
          <FormItem name={['screen', 'max_tries']} label="最大尝试次数">
            <Select style={{ width: 130 }}>
              <Option key={1} value={1}>
                {1}
              </Option>
              <Option key={0} value={0}>
                {0}
              </Option>
            </Select>
          </FormItem>
          <FormItem name={['screen', 'speed_type']} label="速度类型">
            <Select style={{ width: 130 }}>
              <Option key="normal" value="normal">
                normal
              </Option>
              <Option key="fast" value="fast">
                fast
              </Option>
            </Select>
          </FormItem>

          <h3>shodan api</h3>
          <FormItem name={['shodan_api', 'key']} label="key">
            <Input />
          </FormItem>

          <FormItem>
            <Button type="primary" shape="round" onClick={handleOk}>
              提交
            </Button>
          </FormItem>
        </Form>
      </Page>
    )
  }
}

Setting.propTypes = {
  form: PropTypes.object,
  dispatch: PropTypes.func,
  loading: PropTypes.object,
}

export default Setting
