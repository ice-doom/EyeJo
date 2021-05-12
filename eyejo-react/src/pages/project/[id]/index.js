import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'umi'
import { Tabs } from 'antd'
import { Page } from 'components'
import List from './components/List'
import AddGroup from './components/AddGroup'
import TagsSetting from './components/TagsSetting'
import AddTags from './components/AddTags'
import AddAssets from './components/AddAssets'
import DetailsGroup from './components/DetailsGroup'
import IpSide from './components/ipSide'
import IpC from './components/ipC'
const { pathToRegexp } = require('path-to-regexp')

const { TabPane } = Tabs

@connect(({ projecyDetail, loading }) => ({ projecyDetail, loading }))
class projecyDetail extends PureComponent {
  ListRefs = null

  componentDidMount() {
    this.getTagList()
  }

  getTagList = () => {
    const { dispatch, location } = this.props
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    let parameter = {
      project_id: match[1],
      page: 1,
      limit: 10000,
    }
    dispatch({
      type: 'projecyDetail/tagList',
      payload: parameter,
    })
  }

  handleRefresh = (newQuery) => {
    const { dispatch, location } = this.props
    const { pathname } = location
    const match = pathToRegexp('/project/:id').exec(pathname)
    let obj = {}
    if (match) {
      obj = { id: match[1] }
    }
    dispatch({
      type: 'projecyDetail/query',
      payload: {
        ...obj,
        ...newQuery,
      },
    })
  }

  handleTabChange = (activeKey) => {
    // console.log('handleTabChange', activeKey)

    // 切换tab触发子组件方法,导致切换tab显示异常待解决
    // this.ListRefs.resetColumns(activeKey)
    const { dispatch } = this.props
    dispatch({
      type: 'projecyDetail/changeKey',
      payload: {
        activeKey: activeKey,
      },
    })
    dispatch({
      type: 'projecyDetail/changeState',
      payload: {
        projectDetailsFilterData: {},
        projectDetailsSortData: {},
        selectedRowKeys: [],
      },
    })
    this.handleRefresh()
  }
  get listProps() {
    const { projecyDetail, loading, location, dispatch } = this.props
    const {
      list,
      pagination,
      activeKey,
      selectedRowKeys,
      tagsList,
    } = projecyDetail
    const { pathname } = location

    return {
      activeKey,
      tagsList,
      selectedRowKeys,
      pagination,
      dataSource: list,
      loading: loading.effects['projecyDetail/query'],

      rowSelection: {
        selectedRowKeys,
        onChange: (keys) => {
          dispatch({
            type: 'projecyDetail/updateState',
            payload: {
              selectedRowKeys: keys,
            },
          })
        },
      },
      onAdd() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { groupAddVisible: true },
        })
      },
      onTagsSetting() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { tagsSettingVisible: true },
        })
      },
      onAddTags() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { addTagsVisible: true },
        })
      },
      onExportUrl() {
        const match = pathToRegexp('/project/:id').exec(pathname)
        let obj = {}
        if (match) {
          obj = { id: match[1] }
        }
        dispatch({
          type: 'projecyDetail/exportUrl',
          payload: obj,
        }).then((res) => {
          // console.log(res)
          var elink = document.createElement('a')
          elink.download = res.fileName
          elink.style.display = 'none'
          var blob = new Blob([res.data], { type: 'application/vnd.ms-excel' })
          elink.href = URL.createObjectURL(blob)
          document.body.appendChild(elink)
          elink.click()
          document.body.removeChild(elink)
        })
      },
      onAddAssets(item) {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { currentItem: item, assetsAddVisible: true },
        })
      },
      onDetails(item) {
        // console.log(item, 'details')
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { currentItem: item, groupDetailsVisible: true },
        })
      },
      onIpSideDetails(item) {
        // console.log(item, 'details')
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { currentItem: item, ipSideVisible: true },
        })
      },
      onIpCDetails(item) {
        // console.log(item, 'details')
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { currentItem: item, ipCVisible: true },
        })
      },
      onDeleteList: () => {
        const { list, pagination, selectedRowKeys } = projecyDetail
        // console.log(selectedRowKeys, list)
        let arr = []
        selectedRowKeys.forEach((item) => {
          const v = list.find((val) => val.id === item)['id']
          arr.push(v)
        })
        dispatch({
          type: 'projecyDetail/multiDelete',
          payload: {
            id: arr,
          },
        }).then(() => {
          this.handleRefresh({
            page:
              list.length === selectedRowKeys.length && pagination.current > 1
                ? pagination.current - 1
                : pagination.current,
          })
        })
      },
      onDeleteItem: (id) => {
        dispatch({
          type: 'projecyDetail/delete',
          payload: id,
        }).then(() => {
          this.handleRefresh({
            page:
              list.length === 1 && pagination.current > 1
                ? pagination.current - 1
                : pagination.current,
          })
        })
      },
      onFilterChange: (value) => {
        // console.log(value)
        this.handleRefresh({
          page: 1,
          limit: 10,
          ...value,
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { projectDetailsFilterData: value },
        })
        dispatch({
          type: 'projecyDetail/querySuccess',
          payload: {
            list: [],
            pagination: {
              current: 1,
              pageSize: 10,
              total: 0,
            },
          },
        })
      },
      onSortChange: (value) => {
        this.handleRefresh({
          ...value,
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { projectDetailsSortData: value },
        })
      },
      onPaginaionChange: (value) => {
        this.handleRefresh({
          ...value,
        })
      },
    }
  }

  get tagsSettingProps() {
    const { dispatch, projecyDetail, loading, location } = this.props
    const { tagsSettingVisible, tagsSettingData } = projecyDetail
    const { pathname } = location

    return {
      location,
      tagsSettingData,
      visible: tagsSettingVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: 'tags管理',
      width: 850,
      centered: true,
      loading: loading.effects['projecyDetail/tagInfo'],
      getTagInfo: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'projecyDetail/tagInfo',
            payload: { resolve, reject, parameter },
          })
        })
      },
      onDeleteItem: (obj) => {
        dispatch({
          type: 'projecyDetail/deleteTags',
          payload: obj,
        }).then(() => {
          const match = pathToRegexp('/project/:id').exec(pathname)
          let parameter = {
            project_id: match[1],
            page: 1,
            limit: 10,
          }
          return new Promise((resolve, reject) => {
            dispatch({
              type: 'projecyDetail/tagInfo',
              payload: { resolve, reject, parameter },
            })
          })
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { tagsSettingVisible: false },
        })
      },
    }
  }

  get addTagsProps() {
    const { dispatch, projecyDetail, location } = this.props
    const { addTagsVisible, selectedRowKeys } = projecyDetail

    return {
      location,
      visible: addTagsVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: '添加到tags',
      width: 850,
      centered: true,
      selectedRowKeys: selectedRowKeys,
      getTagInfo: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'projecyDetail/tagInfo',
            payload: { resolve, reject, parameter },
          })
        })
      },
      onOk: (data) => {
        dispatch({
          type: 'projecyDetail/addTag',
          payload: data,
        }).then(() => {
          this.handleRefresh()
          this.getTagList()
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { addTagsVisible: false },
        })
      },
    }
  }

  get addProps() {
    const { dispatch, projecyDetail, loading, location } = this.props
    const { groupAddVisible } = projecyDetail

    return {
      location,
      visible: groupAddVisible,
      destroyOnClose: true,
      maskClosable: false,
      confirmLoading: loading.effects['projecyDetail/create'],
      title: '新增资产组',
      width: 850,
      centered: true,
      loading: loading.effects['projecyDetail/urlInfo'],
      getUrlInfo: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'projecyDetail/urlInfo',
            payload: { resolve, reject, parameter },
          })
        })
      },
      getTagInfo: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'projecyDetail/tagInfo',
            payload: { resolve, reject, parameter },
          })
        })
      },
      onOk: (data) => {
        dispatch({
          type: 'projecyDetail/create',
          payload: data,
        }).then(() => {
          this.handleRefresh()
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { groupAddVisible: false },
        })
      },
    }
  }

  get addAssetsProps() {
    const { dispatch, projecyDetail, loading, location } = this.props
    const { assetsAddVisible, currentItem } = projecyDetail

    return {
      location,
      currentItem,
      visible: assetsAddVisible,
      destroyOnClose: true,
      maskClosable: false,
      confirmLoading: loading.effects['projecyDetail/createAssets'],
      title: '新增资产',
      width: 900,
      centered: true,
      onOk: (data) => {
        // console.log(data)
        dispatch({
          type: 'projecyDetail/createAssets',
          payload: data,
        }).then(() => {
          this.handleRefresh()
        })
      },
      getTagInfo: (parameter) => {
        return new Promise((resolve, reject) => {
          dispatch({
            type: 'projecyDetail/tagInfo',
            payload: { resolve, reject, parameter },
          })
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { assetsAddVisible: false },
        })
      },
    }
  }

  get detailsProps() {
    const { dispatch, projecyDetail } = this.props
    const { currentItem } = projecyDetail
    // console.log(currentItem)
    const {
      groupDetailsVisible,
      paginationDetails,
      listDetails,
    } = projecyDetail

    return {
      currentItem: currentItem,
      pagination: paginationDetails,
      dataSource: listDetails,
      visible: groupDetailsVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: '资产组详情',
      width: 900,
      centered: true,
      handleDetailsInfo: () => {
        dispatch({
          type: 'projecyDetail/details',
          payload: {
            id: currentItem.id,
          },
        })
      },
      onFilterChange: (value) => {
        // console.log(value)
        dispatch({
          type: 'projecyDetail/details',
          payload: {
            id: currentItem.id,
            ...value,
          },
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { projectGroupDetailsFilterData: value },
        })
      },
      onDeleteItem: (id) => {
        dispatch({
          type: 'projecyDetail/deleteAssets',
          payload: id,
        }).then(() => {
          dispatch({
            type: 'projecyDetail/details',
            payload: {
              id: currentItem.id,
            },
          })
        })
      },
      onDeleteList: (id) => {
        dispatch({
          type: 'projecyDetail/multiDeleteAssets',
          payload: { id },
        }).then(() => {
          dispatch({
            type: 'projecyDetail/details',
            payload: {
              id: currentItem.id,
            },
          })
        })
      },
      onChange: (page, filters, sorter) => {
        let sortData = {}
        if (sorter.order) {
          sortData = {
            field: sorter.field,
            order: sorter.order === 'ascend' ? 'asc' : 'desc',
          }
        }
        dispatch({
          type: 'projecyDetail/details',
          payload: {
            page: page.current,
            limit: page.pageSize,
            id: currentItem.id,
            ...sortData,
          },
        })
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { projectGroupDetailsSortData: sortData },
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { groupDetailsVisible: false },
        })
      },
    }
  }

  get detailsIpSideProps() {
    const { dispatch, projecyDetail } = this.props
    const { currentItem } = projecyDetail
    // console.log(currentItem)
    const { ipSideVisible, paginationDetails, listDetails } = projecyDetail

    return {
      pagination: paginationDetails,
      dataSource: listDetails,
      visible: ipSideVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: '旁站',
      width: 900,
      centered: true,
      handleDetailsInfo: () => {
        dispatch({
          type: 'projecyDetail/detailsIpSide',
          payload: {
            ip: currentItem.ip_address,
          },
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
          type: 'projecyDetail/detailsIpSide',
          payload: {
            page: page.current,
            limit: page.pageSize,
            ip: currentItem.ip_address,
            ...sortData,
          },
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { ipSideVisible: false },
        })
      },
    }
  }
  get detailsIpCProps() {
    const { dispatch, projecyDetail, loading } = this.props
    const { currentItem } = projecyDetail
    // console.log(currentItem)
    const { ipCVisible, paginationDetails, listDetails } = projecyDetail

    return {
      pagination: paginationDetails,
      dataSource: listDetails,
      visible: ipCVisible,
      destroyOnClose: true,
      maskClosable: false,
      title: 'C段',
      width: 900,
      centered: true,
      loading: loading.effects['projecyDetail/detailsIpC'],
      handleDetailsInfo: () => {
        dispatch({
          type: 'projecyDetail/detailsIpC',
          payload: {
            ip: currentItem.ip_address,
          },
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
          type: 'projecyDetail/detailsIpC',
          payload: {
            page: page.current,
            limit: page.pageSize,
            ip: currentItem.ip_address,
            ...sortData,
          },
        })
      },
      onCancel() {
        dispatch({
          type: 'projecyDetail/changeState',
          payload: { ipCVisible: false },
        })
      },
    }
  }

  render() {
    // console.log(this.props)
    const {
      activeKey,
      groupAddVisible,
      tagsSettingVisible,
      addTagsVisible,
      assetsAddVisible,
      groupDetailsVisible,
      ipSideVisible,
      ipCVisible,
    } = this.props.projecyDetail
    let tabList = [
      {
        tab: '站点详情',
        key: '1',
      },
      {
        tab: '域名',
        key: '2',
      },
      {
        tab: 'IP',
        key: '3',
      },
      {
        tab: '登录接口识别',
        key: '4',
      },
      {
        tab: '资产组',
        key: '5',
      },
    ]
    return (
      <Page inner>
        <Tabs onChange={this.handleTabChange} type="card" activeKey={activeKey}>
          {tabList.map((item) => (
            <TabPane tab={item.tab} key={item.key}>
              <List
                {...this.listProps}
                onListRef={(ref) => (this.ListRefs = ref)}
              />
            </TabPane>
          ))}
        </Tabs>
        {groupAddVisible ? <AddGroup {...this.addProps} /> : <></>}
        {tagsSettingVisible ? (
          <TagsSetting {...this.tagsSettingProps} />
        ) : (
          <></>
        )}
        {addTagsVisible ? <AddTags {...this.addTagsProps} /> : <></>}
        {assetsAddVisible ? <AddAssets {...this.addAssetsProps} /> : <></>}
        {groupDetailsVisible ? <DetailsGroup {...this.detailsProps} /> : <></>}
        {ipSideVisible ? <IpSide {...this.detailsIpSideProps} /> : <></>}
        {ipCVisible ? <IpC {...this.detailsIpCProps} /> : <></>}
      </Page>
    )
  }
}

projecyDetail.propTypes = {
  projecyDetail: PropTypes.object,
  location: PropTypes.object,
}

export default projecyDetail
