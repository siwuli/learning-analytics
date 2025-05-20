/**
 * 忽略非关键UI警告
 * 用于过滤掉不影响应用功能的常见警告信息
 */
export const setupErrorHandler = () => {
  // 保存原始console方法
  const originalConsoleError = window.console.error;
  const originalConsoleWarn = window.console.warn;
  
  // 要忽略的错误信息模式
  const ignoredErrorPatterns = [
    'ResizeObserver loop',
    'ResizeObserver loop completed with undelivered notifications',
    '[Violation]', // 性能违规警告
    'Unable to preventDefault'
  ];
  
  // 重写console.error方法
  window.console.error = (...args) => {
    if (args[0] && typeof args[0] === 'string' && 
        ignoredErrorPatterns.some(pattern => args[0].includes(pattern))) {
      return;
    }
    originalConsoleError(...args);
  };
  
  // 重写console.warn方法
  window.console.warn = (...args) => {
    if (args[0] && typeof args[0] === 'string' && 
        ignoredErrorPatterns.some(pattern => args[0].includes(pattern))) {
      return;
    }
    originalConsoleWarn(...args);
  };
  
  // 全局错误处理
  window.addEventListener('error', (event) => {
    if (event.message && 
        ignoredErrorPatterns.some(pattern => event.message.includes(pattern))) {
      event.preventDefault();
      event.stopPropagation();
      return true;
    }
    return false;
  }, true);
  
  // 应用ResizeObserver补丁
  patchResizeObserver();
};

/**
 * 防止ResizeObserver循环错误的补丁
 * 可以单独调用来修复特定问题
 */
export const patchResizeObserver = () => {
  // 保存原始ResizeObserver
  if (window.ResizeObserver) {
    const OriginalResizeObserver = window.ResizeObserver;
    
    // 重写ResizeObserver
    window.ResizeObserver = function(callback) {
      let timeoutId = null;
      
      // 创建安全的回调函数，添加防抖和错误捕获
      const safeCallback = (entries, observer) => {
        if (timeoutId) {
          cancelAnimationFrame(timeoutId);
        }
        
        // 使用requestAnimationFrame来避免同步布局变化
        timeoutId = requestAnimationFrame(() => {
          try {
            callback(entries, observer);
          } catch (error) {
            console.warn('ResizeObserver回调错误被安全捕获:', error);
          }
        });
      };
      
      // 使用安全的回调创建原始的ResizeObserver
      return new OriginalResizeObserver(safeCallback);
    };
    
    // 复制原型和静态成员
    window.ResizeObserver.prototype = OriginalResizeObserver.prototype;
    Object.keys(OriginalResizeObserver).forEach(key => {
      window.ResizeObserver[key] = OriginalResizeObserver[key];
    });
  }
};

export default {
  setupErrorHandler
}; 