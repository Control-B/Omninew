(() => {
  const config = window.OmniwebWidget || {};
  const appUrl = (config.appUrl || window.location.origin || "").replace(/\/$/, "");
  const widgetKey = encodeURIComponent(config.widgetKey || "");

  const existing = document.getElementById("omniweb-widget-frame");
  if (existing || !appUrl) {
    return;
  }

  const iframe = document.createElement("iframe");
  iframe.id = "omniweb-widget-frame";
  iframe.title = "Omniweb AI Assistant";
  iframe.src = `${appUrl}/embed/widget?widgetKey=${widgetKey}`;
  iframe.style.position = "fixed";
  iframe.style.right = "0";
  iframe.style.bottom = "0";
  iframe.style.width = "420px";
  iframe.style.maxWidth = "100vw";
  iframe.style.height = "760px";
  iframe.style.maxHeight = "100vh";
  iframe.style.border = "0";
  iframe.style.background = "transparent";
  iframe.style.zIndex = "2147483647";
  iframe.allow = "microphone; clipboard-write";

  document.body.appendChild(iframe);
})();
