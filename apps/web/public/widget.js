(() => {
  const config = window.OmniNewWidget || {};
  const appUrl = (config.appUrl || window.location.origin || "").replace(/\/$/, "");
  const tenantId = encodeURIComponent(config.tenantId || "");
  const storeId = encodeURIComponent(config.storeId || "");
  const apiBaseUrl = encodeURIComponent(config.apiBaseUrl || "");
  const livekitWsUrl = encodeURIComponent(config.livekitWsUrl || "");

  const existing = document.getElementById("omninew-widget-frame");
  if (existing || !appUrl) {
    return;
  }

  const iframe = document.createElement("iframe");
  iframe.id = "omninew-widget-frame";
  iframe.title = "OmniNew AI Assistant";
  iframe.src = `${appUrl}/embed/widget?tenantId=${tenantId}&storeId=${storeId}&apiBaseUrl=${apiBaseUrl}&livekitWsUrl=${livekitWsUrl}`;
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
