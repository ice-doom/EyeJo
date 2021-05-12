import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Menu, Layout, Avatar } from 'antd'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Trans, withI18n } from '@lingui/react'
import classnames from 'classnames'
import styles from './Header.less'

const { SubMenu } = Menu

@withI18n()
class Header extends PureComponent {
  handleClickMenu = (e) => {
    e.key === 'SignOut' && this.props.onSignOut()
  }
  render() {
    const { fixed, avatar, username, collapsed, onCollapseChange } = this.props

    const rightContent = [
      <Menu key="user" mode="horizontal" onClick={this.handleClickMenu}>
        <SubMenu
          title={
            <Fragment>
              <span style={{ color: '#999', marginRight: 4 }}>
                <Trans>Hi,</Trans>
              </span>
              <span>{username}</span>
              <Avatar
                style={{ marginLeft: 8 }}
                icon={<UserOutlined style={{ fontSize: '20px' }} />}
              />
            </Fragment>
          }
        >
          <Menu.Item key="SignOut">
            <Trans>Sign out</Trans>
          </Menu.Item>
        </SubMenu>
      </Menu>,
    ]

    return (
      <Layout.Header
        className={classnames(styles.header, {
          [styles.fixed]: fixed,
          [styles.collapsed]: collapsed,
        })}
        id="layoutHeader"
      >
        <div
          className={styles.button}
          onClick={onCollapseChange.bind(this, !collapsed)}
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </div>
        <div className={styles.rightContainer}>{rightContent}</div>
      </Layout.Header>
    )
  }
}

Header.propTypes = {
  fixed: PropTypes.bool,
  user: PropTypes.object,
  menus: PropTypes.array,
  collapsed: PropTypes.bool,
  onSignOut: PropTypes.func,
  notifications: PropTypes.array,
  onCollapseChange: PropTypes.func,
  onAllNotificationsRead: PropTypes.func,
}

export default Header
