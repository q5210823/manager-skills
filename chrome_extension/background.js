chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({
    url: chrome.runtime.getURL("chrome_extension/popup.html?mode=tab"),
  });
});
