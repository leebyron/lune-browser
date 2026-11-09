// The hostname is provisioned before its Helium backend is activated.
// In particular, never return a successful connectivity check during bootstrap.
export default {
  fetch(request) {
    const url = new URL(request.url);
    const headers = {
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=utf-8",
      "X-Content-Type-Options": "nosniff",
    };
    if (url.pathname === "/" && ["GET", "HEAD"].includes(request.method)) {
      return new Response(null, {
        status: 302,
        headers: { ...headers, Location: "https://lune.computer/" },
      });
    }
    if (url.pathname === "/robots.txt" && ["GET", "HEAD"].includes(request.method)) {
      return new Response(request.method === "HEAD" ? null : "User-agent: *\nDisallow: /\n", {
        headers,
      });
    }
    return new Response(request.method === "HEAD" ? null : "Lune services are not yet available.\n", {
      status: 503,
      headers: { ...headers, "Retry-After": "3600" },
    });
  },
};
