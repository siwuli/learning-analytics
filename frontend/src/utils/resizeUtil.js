/**
 * ResizeObserver 安全封装器
 * 用于减少或消除常见的ResizeObserver错误
 */

/**
 * 创建一个安全的ResizeObserver实例
 * @param {Function} callback 回调函数
 * @param {Object} options 配置选项
 * @returns {Object} 安全的ResizeObserver实例
 */
export function createSafeResizeObserver(callback, options = {}) {
  try {
    // 检查浏览器是否支持ResizeObserver
    if (!('ResizeObserver' in window)) {
      console.warn('ResizeObserver不受支持');
      return null;
    }
    
    // 设置防抖处理
    let timeout = null;
    const delay = options.delay || 100; // 默认防抖延迟100ms
    let isProcessing = false; // 防止重入标志
    
    // 封装回调函数，添加防抖逻辑
    const debouncedCallback = (entries, observer) => {
      if (isProcessing) return; // 防止回调重入
      
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      
      isProcessing = true;
      
      timeout = setTimeout(() => {
        try {
          // 过滤掉可能导致循环的条目
          const safeEntries = entries.filter(entry => {
            // 检查entry是否有效
            if (!entry || !entry.contentRect) return false;
            
            // 过滤掉宽度或高度为0的元素
            const { width, height } = entry.contentRect;
            return width > 0 && height > 0;
          });
          
          if (safeEntries.length > 0 && typeof callback === 'function') {
            callback(safeEntries, observer);
          }
        } catch (error) {
          console.warn('ResizeObserver回调执行错误:', error);
        } finally {
          isProcessing = false;
        }
      }, delay);
    };
    
    // 创建ResizeObserver实例
    const observer = new ResizeObserver(debouncedCallback);
    
    return {
      observe: (element, options = {}) => {
        if (element && element instanceof Element) {
          try {
            observer.observe(element, options);
          } catch (error) {
            console.warn('ResizeObserver观察失败:', error);
          }
        } else if (element) {
          console.warn('ResizeObserver: 无效的元素', element);
        }
      },
      unobserve: (element) => {
        if (element && element instanceof Element) {
          try {
            observer.unobserve(element);
          } catch (error) {
            console.warn('ResizeObserver取消观察失败:', error);
          }
        }
      },
      disconnect: () => {
        try {
          observer.disconnect();
          if (timeout) {
            clearTimeout(timeout);
            timeout = null;
          }
        } catch (error) {
          console.warn('ResizeObserver断开连接失败:', error);
        }
      }
    };
  } catch (error) {
    console.warn('创建ResizeObserver失败:', error);
    // 返回空方法对象，防止调用时发生错误
    return {
      observe: () => {},
      unobserve: () => {},
      disconnect: () => {}
    };
  }
}

/**
 * 为滚动容器设置监听器，避免ResizeObserver循环错误
 * @param {string} containerSelector 容器选择器
 * @param {string} tabsSelector 标签页内容选择器
 */
export function setupScrollContainer(containerSelector, tabsSelector = '.el-tabs__content') {
  try {
    // 延迟执行，确保DOM已加载
    setTimeout(() => {
      const container = document.querySelector(containerSelector);
      const tabsContent = document.querySelector(tabsSelector);
      
      if (!container) {
        console.warn(`setupScrollContainer: 未找到容器 "${containerSelector}"`);
        return;
      }
      
      // 设置固定高度和样式，减少布局变化
      if (container) {
        container.style.minHeight = '400px';
        container.style.overflow = 'auto';
        container.style.position = 'relative';
        
        // 添加CSS类，便于样式调试
        if (!container.classList.contains('safe-scroll-container')) {
          container.classList.add('safe-scroll-container');
        }
      }
      
      if (tabsContent) {
        tabsContent.style.minHeight = '500px';
        tabsContent.style.position = 'relative';
      }
      
      // 防止在滚动容器内部的元素触发ResizeObserver
      const observer = createSafeResizeObserver(() => {
        // 最小化处理逻辑，避免不必要的布局计算
      }, { delay: 200 });
      
      if (observer && container) {
        observer.observe(container);
        
        // 5秒后断开观察，减少长时间的ResizeObserver负担
        setTimeout(() => {
          observer.disconnect();
        }, 5000);
      }
    }, 100);
  } catch (error) {
    console.warn('设置滚动容器失败:', error);
  }
}

export default {
  createSafeResizeObserver,
  setupScrollContainer
}; 