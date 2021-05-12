// import { cloneDeep } from 'lodash'

/**
 *判断是否已经选择，选择了返回true(该元素)，未选择返回false(undefined)
 * @export
 * @param {object} item:表格中的某行
 * @param {array} array_right:右侧表格的数据
 * @param {string} key:唯一标识
 * @return {boolean} 布尔值
 */
export function hasSelected(item, array_right, key) {
  return array_right.find((p) => p[key] === item[key])
}

/**
 *添加一行或者多行
 * @export
 * @param {object} item:表格中的某行
 * @param {array} array_left:左侧表格的数据
 * @param {array} array_right:右侧表格的数据
 * @param {string} key:唯一标识
 * @return {array} 右侧表格数数据
 */
export function addItem(item, array_left, array_right, key) {
  // console.log(item, array_right)
  let arr = []
  if (item) {
    // 添加单个
    arr = [item, ...array_right]
  } else {
    // 添加多个
    arr = array_left.filter((p) => !hasSelected(p, array_right, key))
    arr.push(...array_right)
  }
  return arr
}

/**
 *删除一行或者多行
 * @export
 * @param {object} item:表格中的某行
 * @param {array} array_right:右侧表格的数据
 * @param {string} key:唯一标识
 * @return {array} 右侧表格数数据
 */
export function removeItem(item, array_right, key) {
  let arr = []
  if (item) {
    // 删除单个
    const index = array_right.findIndex((val) => val[key] === item[key])
    arr = [...array_right]
    arr.splice(index, 1)
  } else {
    // 删除多个
    arr = []
  }
  return arr
}
