#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { constants } from 'node:fs';
import { access, cp, mkdir, readFile, realpath } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

const usage = `Usage: node scripts/preview-setup.mjs SOURCE [--copy-to DIRECTORY] [--port PORT]

SOURCE is a prepared Chromium tree or its components/helium_onboarding directory.
--copy-to creates a new standalone copy for editing. Pass that copy as SOURCE to resume.
The preview listens on 127.0.0.1, port 5173 by default.`;

const bootstrapId = 'virtual:lune-setup-preview';

async function projectDirectory(source) {
    for (const candidate of [source, join(source, 'components/helium_onboarding')]) {
        try {
            await access(join(candidate, 'util/generate-i18n.mts'));
            return realpath(candidate);
        } catch (error) {
            if (error.code !== 'ENOENT') throw error;
        }
    }
    throw new Error(`No prepared setup project found at ${source}`);
}

async function copyProject(project, target) {
    const absoluteTarget = resolve(target);
    const destination = join(await realpath(dirname(absoluteTarget)), basename(absoluteTarget));
    if (destination === project || destination.startsWith(project + sep)) {
        throw new Error('Choose a copy directory outside the setup source.');
    }
    // Create a fresh destination so existing edits stay intact.
    await mkdir(destination);
    await cp(project, destination, {
        recursive: true,
        verbatimSymlinks: true,
        mode: constants.COPYFILE_FICLONE,
        filter: (file) => {
            const path = relative(project, file);
            return !['.git', 'dist', 'node_modules/.vite', 'node_modules/.vite-temp']
                .some((excluded) => path === excluded || path.startsWith(excluded + sep));
        },
    });
    return realpath(destination);
}

async function main() {
    const { positionals, values } = parseArgs({
        allowPositionals: true,
        options: {
            'copy-to': { type: 'string' },
            port: { type: 'string', default: '5173' },
            help: { type: 'boolean', short: 'h' },
        },
    });
    if (values.help) {
        console.log(usage);
        return;
    }
    if (positionals.length !== 1) throw new Error(usage);
    const port = Number(values.port);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
        throw new Error('--port must be an integer from 1 to 65535.');
    }

    let project = await projectDirectory(resolve(positionals[0]));
    try {
        await access(join(project, 'node_modules/vite/package.json'));
    } catch (error) {
        if (error.code !== 'ENOENT') throw error;
        throw new Error(`Setup dependencies are missing in ${project}. Use a prepared tree with node_modules.`);
    }
    if (values['copy-to']) project = await copyProject(project, values['copy-to']);

    const requireFromPreview = createRequire(join(project, 'package.json'));
    const { createServer } = await import(pathToFileURL(requireFromPreview.resolve('vite')));
    const bootstrap = await readFile(new URL('./fixtures/setup-preview.js', import.meta.url), 'utf8');

    execFileSync(process.execPath, ['util/generate-i18n.mts'], { cwd: project, stdio: 'inherit' });
    const server = await createServer({
        root: project,
        configFile: join(project, 'vite.config.ts'),
        server: { host: '127.0.0.1', port, strictPort: true, fs: { allow: [project] } },
        plugins: [{
            name: 'lune-setup-preview',
            apply: 'serve',
            resolveId: (id) => id === bootstrapId ? `\0${id}` : null,
            load: (id) => id === `\0${bootstrapId}` ? bootstrap : null,
            transform(code, id) {
                if (id === join(project, 'src/main.ts')) return `import '${bootstrapId}';\n${code}`;
            },
            hotUpdate({ file, server }) {
                const publicDir = server.config.publicDir;
                if (this.environment.name === 'client' && publicDir && file.startsWith(publicDir + sep)) {
                    // Direct URLs in public/ sit outside the module graph.
                    this.environment.hot.send({ type: 'full-reload', path: '*' });
                    return [];
                }
            },
        }],
    });
    try {
        await server.listen();
    } catch (error) {
        await server.close();
        throw error;
    }
    console.log(`Editing ${project}`);
    server.printUrls();
    console.log(`  Import fixture: http://127.0.0.1:${port}/?step=DataImport&scenario=import-empty`);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
