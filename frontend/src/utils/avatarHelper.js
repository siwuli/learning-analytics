/**
 * 头像URL处理辅助工具
 * 
 * 用于统一处理用户头像URL的格式和显示
 */

/**
 * 获取格式化的头像URL
 * @param {string} avatarUrl 原始头像URL
 * @returns {string} 处理后可直接使用的头像URL
 */
export function getFormattedAvatarUrl(avatarUrl) {
  // 检查是否有有效的头像URL
  if (avatarUrl) {
    // 如果是以http开头的完整URL，直接使用
    if (avatarUrl.startsWith('http')) {
      return avatarUrl;
    }
    
    // 处理相对路径
    if (avatarUrl.startsWith('/')) {
      // 从环境变量获取API基础URL，如果没有则使用默认
      const baseUrl = import.meta.env?.VITE_APP_API_URL || 
                     process.env.VUE_APP_API_URL || 
                     'http://localhost:5000';
      return baseUrl + avatarUrl;
    }
    
    // 如果只是文件名，添加完整路径
    return `http://localhost:5000/api/static/uploads/avatars/${avatarUrl}`;
  }
  
  // 无头像时使用默认头像
  return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
}

/**
 * 检测用户是否有自定义头像
 * @param {object} user 用户对象
 * @returns {boolean} 是否有自定义头像
 */
export function hasCustomAvatar(user) {
  return !!(user && user.avatar);
} 