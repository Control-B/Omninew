const https = require("https");
const http = require("http");

async function proxy(event, path) {
  const baseUrl = process.env.OMNINEW_API_BASE_URL || "";
  const secret = process.env.OMNINEW_AGENT_ROUTE_SECRET || "";

  if (!baseUrl || !secret) {
    return {
      statusCode: 503,
      body: JSON.stringify({ error: "Proxy not configured" }),
    };
  }

  const url = new URL(`${baseUrl}/api/v1/agent/tools${path}`);
  const body = JSON.stringify(event.body || event);
  const lib = url.protocol === "https:" ? https : http;

  return new Promise((resolve) => {
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === "https:" ? 443 : 80),
      path: url.pathname + url.search,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
        "X-Agent-Route-Secret": secret,
      },
    };

    const req = lib.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          resolve({ statusCode: res.statusCode, body: JSON.parse(data) });
        } catch {
          resolve({ statusCode: res.statusCode, body: data });
        }
      });
    });

    req.on("error", (err) => {
      resolve({ statusCode: 502, body: JSON.stringify({ error: err.message }) });
    });

    req.write(body);
    req.end();
  });
}

exports.main = async (event) => proxy(event, "/lead-capture");
