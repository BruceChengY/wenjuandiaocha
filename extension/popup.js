// 弹窗脚本 - 处理插件弹窗的交互逻辑

document.addEventListener("DOMContentLoaded", initializePopup);

let isTranslating = false;

function initializePopup() {
  // 获取DOM元素
  const inputText = document.getElementById("inputText");
  const translateBtn = document.getElementById("translateBtn");
  const clearBtn = document.getElementById("clearBtn");
  const copyBtn = document.getElementById("copyBtn");
  const speakBtn = document.getElementById("speakBtn");
  const swapLang = document.getElementById("swapLang");
  const sourceLang = document.getElementById("sourceLang");
  const targetLang = document.getElementById("targetLang");
  const charCount = document.getElementById("charCount");
  const resultSection = document.getElementById("resultSection");
  const errorSection = document.getElementById("errorSection");
  const translationResult = document.getElementById("translationResult");
  const errorMessage = document.getElementById("errorMessage");
  const settingsBtn = document.getElementById("settingsBtn");
  const aboutBtn = document.getElementById("aboutBtn");

  // 绑定事件监听器
  inputText.addEventListener("input", updateCharCount);
  inputText.addEventListener("keydown", handleKeyDown);
  translateBtn.addEventListener("click", handleTranslate);
  clearBtn.addEventListener("click", handleClear);
  copyBtn.addEventListener("click", handleCopy);
  speakBtn.addEventListener("click", handleSpeak);
  swapLang.addEventListener("click", handleSwapLanguages);
  settingsBtn.addEventListener("click", handleSettings);
  aboutBtn.addEventListener("click", handleAbout);

  // 加载保存的设置
  loadSettings();
  
  // 自动获取页面选中文本
  getSelectedTextFromPage();
}

// 更新字符计数
function updateCharCount() {
  const inputText = document.getElementById("inputText");
  const charCount = document.getElementById("charCount");
  const count = inputText.value.length;
  charCount.textContent = count;
  
  // 字符数接近限制时变色提醒
  if (count > 4500) {
    charCount.style.color = "#ff4444";
  } else if (count > 4000) {
    charCount.style.color = "#ff8800";
  } else {
    charCount.style.color = "#666";
  }
}

// 处理键盘事件
function handleKeyDown(event) {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    handleTranslate();
  }
}

// 处理翻译
async function handleTranslate() {
  if (isTranslating) return;
  
  const inputText = document.getElementById("inputText").value.trim();
  if (!inputText) {
    showError("请输入要翻译的文本");
    return;
  }
  
  const sourceLang = document.getElementById("sourceLang").value;
  const targetLang = document.getElementById("targetLang").value;
  
  if (sourceLang === targetLang && sourceLang !== "auto") {
    showError("源语言和目标语言不能相同");
    return;
  }
  
  setTranslatingState(true);
  hideError();
  hideResult();
  
  try {
    // 发送翻译请求到background script
    const response = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage({
        action: "translate",
        text: inputText,
        sourceLang: sourceLang,
        targetLang: targetLang
      }, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
    
    if (response.success) {
      showResult(response.data);
      saveSettings(); // 保存语言设置
    } else {
      showError(response.error || "翻译失败，请重试");
    }
  } catch (error) {
    console.error("翻译失败:", error);
    showError("翻译服务连接失败，请检查网络连接或稍后重试");
  } finally {
    setTranslatingState(false);
  }
}

// 设置翻译状态
function setTranslatingState(translating) {
  isTranslating = translating;
  const translateBtn = document.getElementById("translateBtn");
  const buttonText = translateBtn.querySelector(".button-text");
  const buttonLoading = translateBtn.querySelector(".button-loading");
  
  if (translating) {
    translateBtn.disabled = true;
    buttonText.style.display = "none";
    buttonLoading.style.display = "inline";
  } else {
    translateBtn.disabled = false;
    buttonText.style.display = "inline";
    buttonLoading.style.display = "none";
  }
}

// 显示翻译结果
function showResult(result) {
  const resultSection = document.getElementById("resultSection");
  const translationResult = document.getElementById("translationResult");
  
  translationResult.innerHTML = `
    <div class="result-text">${result.translation}</div>
    <div class="result-info">
      <span class="language-info">${result.source_lang} → ${result.target_lang}</span>
    </div>
  `;
  
  resultSection.style.display = "block";
}

// 隐藏翻译结果
function hideResult() {
  const resultSection = document.getElementById("resultSection");
  resultSection.style.display = "none";
}

// 显示错误信息
function showError(message) {
  const errorSection = document.getElementById("errorSection");
  const errorMessage = document.getElementById("errorMessage");
  
  errorMessage.textContent = message;
  errorSection.style.display = "block";
  
  // 3秒后自动隐藏错误信息
  setTimeout(hideError, 3000);
}

// 隐藏错误信息
function hideError() {
  const errorSection = document.getElementById("errorSection");
  errorSection.style.display = "none";
}

// 处理清空
function handleClear() {
  document.getElementById("inputText").value = "";
  updateCharCount();
  hideResult();
  hideError();
}

// 处理复制
async function handleCopy() {
  const resultText = document.querySelector(".result-text");
  if (!resultText) return;
  
  try {
    await navigator.clipboard.writeText(resultText.textContent);
    
    // 显示复制成功提示
    const copyBtn = document.getElementById("copyBtn");
    const originalText = copyBtn.textContent;
    copyBtn.textContent = "✅ 已复制";
    copyBtn.style.color = "#4CAF50";
    
    setTimeout(() => {
      copyBtn.textContent = originalText;
      copyBtn.style.color = "";
    }, 1500);
  } catch (error) {
    console.error("复制失败:", error);
    showError("复制失败，请手动选择文本复制");
  }
}

// 处理朗读
function handleSpeak() {
  const resultText = document.querySelector(".result-text");
  if (!resultText) return;
  
  try {
    // 停止当前朗读
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(resultText.textContent);
    const targetLang = document.getElementById("targetLang").value;
    
    // 设置朗读语言
    utterance.lang = getLangCode(targetLang);
    utterance.rate = 0.8;
    utterance.pitch = 1;
    
    speechSynthesis.speak(utterance);
    
    // 更新按钮状态
    const speakBtn = document.getElementById("speakBtn");
    const originalText = speakBtn.textContent;
    speakBtn.textContent = "🔇 停止";
    
    utterance.onend = () => {
      speakBtn.textContent = originalText;
    };
    
    utterance.onerror = () => {
      speakBtn.textContent = originalText;
      showError("朗读功能暂时不可用");
    };
  } catch (error) {
    console.error("朗读失败:", error);
    showError("朗读功能暂时不可用");
  }
}

// 获取朗读语言代码
function getLangCode(lang) {
  const langMap = {
    "zh-cn": "zh-CN",
    "en": "en-US",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "fr": "fr-FR",
    "de": "de-DE",
    "es": "es-ES",
    "ru": "ru-RU"
  };
  return langMap[lang] || "zh-CN";
}

// 处理语言交换
function handleSwapLanguages() {
  const sourceLang = document.getElementById("sourceLang");
  const targetLang = document.getElementById("targetLang");
  
  if (sourceLang.value === "auto") {
    showError("自动检测语言无法交换");
    return;
  }
  
  const temp = sourceLang.value;
  sourceLang.value = targetLang.value;
  targetLang.value = temp;
}

// 获取页面选中文本
async function getSelectedTextFromPage() {
  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    
    chrome.scripting.executeScript({
      target: {tabId: tab.id},
      function: () => window.getSelection().toString().trim()
    }, (results) => {
      if (results && results[0] && results[0].result) {
        const selectedText = results[0].result;
        if (selectedText.length > 0 && selectedText.length < 1000) {
          document.getElementById("inputText").value = selectedText;
          updateCharCount();
        }
      }
    });
  } catch (error) {
    // 忽略错误，用户可以手动输入
    console.log("无法获取页面选中文本:", error);
  }
}

// 保存设置
function saveSettings() {
  const settings = {
    sourceLang: document.getElementById("sourceLang").value,
    targetLang: document.getElementById("targetLang").value
  };
  
  chrome.storage.sync.set({settings}, () => {
    console.log("设置已保存");
  });
}

// 加载设置
function loadSettings() {
  chrome.storage.sync.get(["settings"], (result) => {
    if (result.settings) {
      const sourceLang = document.getElementById("sourceLang");
      const targetLang = document.getElementById("targetLang");
      
      if (result.settings.sourceLang) {
        sourceLang.value = result.settings.sourceLang;
      }
      if (result.settings.targetLang) {
        targetLang.value = result.settings.targetLang;
      }
    }
  });
}

// 处理设置按钮
function handleSettings() {
  // 这里可以打开设置页面或显示设置面板
  showError("设置功能开发中...");
}

// 处理关于按钮
function handleAbout() {
  const aboutInfo = `
智能翻译助手 v1.0.0

🚀 快速翻译网页选中文本
🖱️ 支持右键菜单翻译
🎯 插件弹窗手动翻译
💾 智能缓存机制

技术支持：FastAPI + Chrome Extension
翻译引擎：Google Translate

使用愉快！
  `;
  
  alert(aboutInfo);
}