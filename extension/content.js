// 内容脚本 - 处理页面选中文本的翻译
console.log("Content script loaded!");

let translationBox = null;
let isTranslating = false;

// 测试基础功能
console.log("Testing basic functionality...");

// 监听文本选择事件
document.addEventListener("mouseup", handleTextSelection);
document.addEventListener("keyup", handleTextSelection);

console.log("Event listeners added");

// 监听来自background script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "translate") {
    translateSelectedText(request.text);
  }
});

// 处理文本选择
function handleTextSelection() {
  const selectedText = window.getSelection().toString().trim();
  
  if (selectedText && selectedText.length > 0 && selectedText.length < 500) {
    // 防抖处理，避免频繁翻译
    clearTimeout(window.translationTimeout);
    window.translationTimeout = setTimeout(() => {
      // 检查是否为英文文本
      if (isEnglishText(selectedText)) {
        showTranslationBox(selectedText);
      }
    }, 300);
  } else {
    hideTranslationBox();
  }
}

// 检查是否为英文文本
function isEnglishText(text) {
  // 简单的英文检测：包含英文字母且英文字符占比超过50%
  const englishChars = text.match(/[a-zA-Z]/g) || [];
  const totalChars = text.replace(/\s/g, '').length;
  return englishChars.length / totalChars > 0.5;
}

// 显示翻译框
async function showTranslationBox(text) {
  if (isTranslating) return;
  
  hideTranslationBox();
  
  const selection = window.getSelection();
  if (selection.rangeCount === 0) return;
  
  const range = selection.getRangeAt(0);
  const rect = range.getBoundingClientRect();
  
  // 创建翻译框
  translationBox = document.createElement("div");
  translationBox.className = "translation-box";
  translationBox.innerHTML = `
    <div class="translation-header">
      <span class="translation-title">翻译中...</span>
      <button class="translation-close">×</button>
    </div>
    <div class="translation-content">
      <div class="translation-loading">正在翻译，请稍候...</div>
    </div>
  `;
  
  // 设置位置
  translationBox.style.position = "absolute";
  translationBox.style.left = `${rect.left + window.scrollX}px`;
  translationBox.style.top = `${rect.bottom + window.scrollY + 5}px`;
  translationBox.style.zIndex = "10000";
  
  document.body.appendChild(translationBox);
  
  // 绑定关闭事件
  const closeBtn = translationBox.querySelector(".translation-close");
  closeBtn.addEventListener("click", hideTranslationBox);
  
  // 执行翻译
  await translateSelectedText(text);
}

// 翻译选中的文本
// 翻译选中的文本
async function translateSelectedText(text) {
  if (isTranslating) return;
  
  isTranslating = true;
  
  try {
    console.log("Starting translation for:", text);
    
    // 检查Chrome运行环境
    if (!chrome.runtime || !chrome.runtime.id) {
      console.error("Chrome extension context is not valid");
      displayTranslationError("插件未正确加载，请刷新页面");
      return;
    }
    
    // 直接调用后端API进行测试
    console.log("Calling backend API directly for testing...");
    const apiResponse = await fetch("http://localhost:8000/translate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: text,
        source_lang: "en",
        target_lang: "zh-cn"
      })
    });
    
    if (!apiResponse.ok) {
      throw new Error(`API请求失败: ${apiResponse.status}`);
    }
    
    const result = await apiResponse.json();
    console.log("API response:", result);
    
    displayTranslationResult(text, result);
    
  } catch (error) {
    console.error("翻译失败:", error);
    if (error.message.includes("Failed to fetch")) {
      displayTranslationError("无法连接到翻译服务，请确保后端服务正在运行(端口8000)");
    } else if (error.message.includes("Extension context invalidated")) {
      displayTranslationError("插件已更新，请刷新页面(F5)后重试");
    } else {
      displayTranslationError("翻译失败: " + error.message);
    }
  } finally {
    isTranslating = false;
  }
}
  
  const title = translationBox.querySelector(".translation-title");
  const content = translationBox.querySelector(".translation-content");
  
  if (!title || !content) {
    console.error("Translation box elements not found!");
    return;
  }
  
  title.textContent = "翻译结果";
  content.innerHTML = `
    <div class="translation-original">
      <strong>原文：</strong>${originalText}
    </div>
    <div class="translation-result">
      <strong>译文：</strong>${result.translation || "无翻译结果"}
    </div>
    <div class="translation-info">
      ${result.source_lang || "unknown"} → ${result.target_lang || "unknown"}
    </div>
  `;
  console.log("Translation result displayed successfully");
}

// 显示翻译错误
function displayTranslationError(error) {
  if (!translationBox) return;
  
  const title = translationBox.querySelector(".translation-title");
  const content = translationBox.querySelector(".translation-content");
  
  title.textContent = "翻译失败";
  content.innerHTML = `
    <div class="translation-error">
      ${error || "翻译服务暂时不可用，请稍后重试"}
    </div>
  `;
}

// 隐藏翻译框
function hideTranslationBox() {
  if (translationBox) {
    translationBox.remove();
    translationBox = null;
  }
}

// 点击页面其他位置时隐藏翻译框
document.addEventListener("click", (event) => {
  if (translationBox && !translationBox.contains(event.target)) {
    hideTranslationBox();
  }
});

// 滚动时隐藏翻译框
window.addEventListener("scroll", hideTranslationBox);
