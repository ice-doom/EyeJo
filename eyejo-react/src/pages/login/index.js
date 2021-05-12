import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'umi'
import { Button, Row, Input, Form } from 'antd'
import { GlobalFooter } from 'components'
import { Trans, withI18n } from '@lingui/react'
import config from 'utils/config'

import styles from './index.less'

const FormItem = Form.Item

@withI18n()
@connect(({ loading, dispatch }) => ({ loading, dispatch }))
class Login extends PureComponent {
  render() {
    const { dispatch, loading, i18n } = this.props

    const handleOk = (values) => {
      dispatch({ type: 'login/login', payload: values })
    }
    let footerLinks = []

    return (
      <Fragment>
        <div className={styles.form}>
          <div className={styles.logo}>
            <img alt="logo" src={config.logoPath} />
            <span>{config.siteName}</span>
          </div>
          <Form onFinish={handleOk}>
            <FormItem name="username" rules={[{ required: true }]} hasFeedback>
              <Input placeholder={i18n.t`Username`} />
            </FormItem>
            <FormItem name="password" rules={[{ required: true }]} hasFeedback>
              <Input type="password" placeholder={i18n.t`Password`} />
            </FormItem>
            <Row>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading.effects.login}
              >
                <Trans>Sign in</Trans>
              </Button>
            </Row>
          </Form>
        </div>
        <div className={styles.footer}>
          <GlobalFooter links={footerLinks} copyright={config.copyright} />
        </div>
      </Fragment>
    )
  }
}

Login.propTypes = {
  form: PropTypes.object,
  dispatch: PropTypes.func,
  loading: PropTypes.object,
}

export default Login
