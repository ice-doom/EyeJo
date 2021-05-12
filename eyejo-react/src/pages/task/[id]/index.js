import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'umi'
import { Tabs } from 'antd'
import { Page } from 'components'
import List from './components/List'
import DetailsFuzz from './components/DetailsFuzz'
const { pathToRegexp } = require('path-to-regexp')

const { TabPane } = Tabs

@connect(({ taskDetail, loading }) => ({ taskDetail, loading }))
class TaskDetail extends PureComponent {
  handleRefresh = (newQuery) => {
    const { dispatch, location } = this.props
    const { pathname } = location
    const match = pathToRegexp('/task/:id').exec(pathname)
    let obj = {}
    if (match) {
      obj = { id: match[1] }
    }
    dispatch({
      type: 'taskDetail/query',
      payload: {
        ...obj,
        ...newQuery,
      },
    })
  }

  handleTabChange = (activeKey) => {
    const { dispatch } = this.props
    dispatch({
      type: 'taskDetail/changeKey',
      payload: {
        activeKey: activeKey,
      },
    })
    this.handleRefresh()
  }
  get listProps() {
    const { taskDetail, loading, location, dispatch } = this.props
    const { list, pagination, activeKey } = taskDetail
    const { query } = location

    return {
      filter: {
        ...query,
      },
      activeKey: activeKey,
      pagination,
      dataSource: list,
      loading: loading.effects['taskDetail/query'],
      onChange: (page) => {
        this.handleRefresh({
          page: page.current,
          limit: page.pageSize,
        })
      },
      onFilterChange: (value) => {
        this.handleRefresh({
          ...value,
        })
      },
      onDetails(item) {
        // console.log(item, 'details')
        dispatch({
          type: 'taskDetail/changeState',
          payload: { currentItem: item, detailsVisible: true },
        })
      },
    }
  }

  get detailsProps() {
    const { dispatch, taskDetail, location } = this.props
    const { currentItem } = taskDetail
    const { pathname } = location
    // console.log(currentItem)
    const { detailsVisible, paginationDetails, listDetails } = taskDetail
    const taskId = pathToRegexp('/task/:id').exec(pathname)[1]

    return {
      pagination: paginationDetails,
      dataSource: listDetails,
      visible: detailsVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: 'FUZZ详情',
      width: 900,
      centered: true,
      handleDetailsInfo: () => {
        dispatch({
          type: 'taskDetail/details',
          payload: {
            url: currentItem.url,
            id: taskId,
          },
        })
      },
      onFilterChange: (value) => {
        dispatch({
          type: 'taskDetail/details',
          payload: {
            url: currentItem.url,
            id: taskId,
            ...value,
          },
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { taskFuzzDetailsFilterData: value },
        })
      },
      onChange: (page, filters, sorter) => {
        // console.log(page)
        let sortData = {}
        if (sorter.order) {
          sortData = {
            field: sorter.field,
            order: sorter.order === 'ascend' ? 'asc' : 'desc',
          }
        }
        dispatch({
          type: 'taskDetail/details',
          payload: {
            page: page.current,
            limit: page.pageSize,
            url: currentItem.url,
            id: taskId,
            ...sortData,
          },
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { taskFuzzDetailsSortData: sortData },
        })
      },
      onCancel() {
        dispatch({
          type: 'taskDetail/changeState',
          payload: { detailsVisible: false },
        })
      },
    }
  }

  render() {
    // console.log(this.props)
    const { activeKey, detailsVisible } = this.props.taskDetail
    return (
      <Page inner>
        <Tabs onChange={this.handleTabChange} type="card" activeKey={activeKey}>
          <TabPane tab="漏洞" key="1">
            <List {...this.listProps} />
          </TabPane>
          <TabPane tab="POC" key="2">
            <List {...this.listProps} />
          </TabPane>
          <TabPane tab="FUZZ" key="3">
            <List {...this.listProps} />
          </TabPane>
          <TabPane tab="服务爆破" key="4">
            <List {...this.listProps} />
          </TabPane>
        </Tabs>
        {detailsVisible ? <DetailsFuzz {...this.detailsProps} /> : <></>}
      </Page>
    )
  }
}

TaskDetail.propTypes = {
  taskDetail: PropTypes.object,
}

export default TaskDetail
