import assert from "node:assert/strict";
import test from "node:test";
import worker from "../src/index.js";

test("bootstrap does not advertise working browser services", async () => {
  for (const path of ["/ext/", "/ext/proxy?url=https://example.com", "/com", "/ubo/assets.json", "/dict/en-us.bdic", "/bangs.json", "/connectivitycheck"]) {
    for (const protocol of ["http:", "https:"]) {
      const response = worker.fetch(new Request(`${protocol}//services.lune.computer${path}`));
      assert.equal(response.status, 503, path);
      assert.equal(response.headers.get("Cache-Control"), "no-store");
      assert.equal(response.headers.get("Location"), null);
    }
  }
});

test("root points to Lune without carrying request parameters", () => {
  const response = worker.fetch(new Request("https://services.lune.computer/?secret=test"));
  assert.equal(response.status, 302);
  assert.equal(response.headers.get("Location"), "https://lune.computer/");
});

test("HEAD responses have no body and POST is not redirected", async () => {
  const response = worker.fetch(new Request("https://services.lune.computer/bangs.json", { method: "HEAD" }));
  assert.equal(response.status, 503);
  assert.equal(await response.text(), "");
  assert.equal(worker.fetch(new Request("https://services.lune.computer/", { method: "POST" })).status, 503);
});
