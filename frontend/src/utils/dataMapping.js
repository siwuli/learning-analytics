/**
 * 数据映射工具
 * 提供各种数据映射和转换函数
 */

// 活动类型英文到中文的映射
export const activityTypeMap = {
  'assignment': '作业',
  'discussion': '讨论',
  'document_read': '阅读文档',
  'quiz': '测验',
  'video_watch': '观看视频'
};

// 活动类型对应的颜色
export const activityTypeColors = {
  'assignment': '#6366F1', // 紫色
  'discussion': '#84CC16', // 绿色
  'document_read': '#FACC15', // 黄色
  'quiz': '#EF4444', // 红色
  'video_watch': '#38BDF8' // 蓝色
};

/**
 * 将活动类型从英文转换为中文
 * @param {string} type 活动类型英文名称
 * @returns {string} 活动类型中文名称
 */
export function translateActivityType(type) {
  return activityTypeMap[type] || type;
}

/**
 * 获取活动类型对应的颜色
 * @param {string} type 活动类型英文名称
 * @returns {string} 颜色代码
 */
export function getActivityTypeColor(type) {
  return activityTypeColors[type] || '#909399'; // 默认灰色
}

/**
 * 将包含活动类型统计的对象转换为中文键名
 * @param {Object} typeDistribution 活动类型分布对象
 * @returns {Object} 转换后的对象
 */
export function translateActivityTypeDistribution(typeDistribution) {
  if (!typeDistribution) return {};
  
  const result = {};
  Object.entries(typeDistribution).forEach(([key, value]) => {
    result[translateActivityType(key)] = value;
  });
  
  return result;
} 