# Lune website

The source for [lune.computer](https://lune.computer/): an interactive introduction to Lune, downloads, and legal pages.

## Work locally

From this directory:

```sh
npm ci
npm run dev
```

Open the local URL printed by Wrangler. Run `npm run check` to build, test, and validate the deployment without publishing.

Edit the homepage in `public/index.html`, `public/styles.css`, and `public/main.js`. It uses plain HTML, CSS, and JavaScript. Edit legal pages in [legal/](../legal/); `npm run build` generates them into `dist/`. Rebuild after edits while the dev server is running.

Agents maintain the [website specification](spec/README.md), including behavior, asset credits, and deployment instructions.

## License

Lune’s original work uses [GPL-3.0-or-later](../LICENSE). Fonts and third-party artwork retain their own licenses; see [asset credits](spec/assets.md) and [NOTICE](../NOTICE).
