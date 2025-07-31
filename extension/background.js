// 后台脚本 - 处理右键菜单和消息传递
console.log("Background script loaded!");

// 创建右键菜单
chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension installed, creating context menu...");
  chrome.contextMenus.create({
    id: "translateText",
    title: "翻译选中文本",
    contexts: ["selection"]
  });
});

// 处理右键菜单点击事件
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "translateText" && info.selectionText) {
    // 向content script发送翻译请求
    chrome.tabs.sendMessage(tab.id, {
      action: "translate",
      text: info.selectionText
    });
  }
});

// 处理来自content script和popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Background script received message:", request);
  
  if (request.action === "translate") {
    translateText(request.text, request.sourceLang || "en", request.targetLang || "zh-cn")
      .then(result => {
        console.log("Translation result:", result);
        sendResponse({success: true, data: result});
      })
      .catch(error => {
        console.error("Translation error:", error);
        sendResponse({success: false, error: error.message});
      });
    return true; // 保持消息通道开放以进行异步响应
  }
  
  // 对于其他消息，发送默认响应
  sendResponse({success: false, error: "Unknown action"});
});

// 翻译函数
async function translateText(text, sourceLang = "en", targetLang = "zh-cn") {
  try {
    // 首先检查缓存
    const cacheKey = `translate_${text}_${sourceLang}_${targetLang}`;
    const cached = await getCachedTranslation(cacheKey);
    if (cached) {
      return cached;
    }

    // 调用后端翻译API
    const response = await fetch("http://localhost:8000/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: text,
        source_lang: sourceLang,
        target_lang: targetLang
      })
    });

    if (!response.ok) {
      throw new Error(`翻译服务错误: ${response.status}`);
    }

    const result = await response.json();
    
    // 缓存翻译结果
    await cacheTranslation(cacheKey, result);
    
    return result;
  } catch (error) {
    console.error("翻译失败:", error);
    throw error;
  }
}

// 获取缓存的翻译结果
async function getCachedTranslation(key) {
  try {
    const result = await chrome.storage.local.get(key);
    const cached = result[key];
    if (cached && Date.now() - cached.timestamp < 24 * 60 * 60 * 1000) { // 24小时缓存
      return cached.data;
    }
    return null;
  } catch (error) {
    console.error("获取缓存失败:", error);
    return null;
  }
}

// 缓存翻译结果
async function cacheTranslation(key, data) {
  try {
    await chrome.storage.local.set({
      [key]: {
        data: data,
        timestamp: Date.now()
      }
    });
  } catch (error) {
    console.error("缓存翻译结果失败:", error);
  }
}