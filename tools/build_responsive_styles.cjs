/* Rebuild book and reader utilities with the Writing STD 1 toolbar runtime.
 * Uses the sibling ADT Studio's installed Tailwind dependencies; override
 * ADT_RUNTIME_DIR when that checkout is elsewhere.
 */
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

const root = path.resolve(__dirname, '..');
const runtimeDir = process.env.ADT_RUNTIME_DIR ||
  path.resolve(root, '../../../adt-studio/apps/adt-runtime');
const runtimeRequire = createRequire(path.join(runtimeDir, 'package.json'));
const postcss = runtimeRequire('postcss');
const tailwind = runtimeRequire('@tailwindcss/postcss');
const pluginRequire = createRequire(runtimeRequire.resolve('@tailwindcss/postcss'));
const tailwindDir = path.dirname(pluginRequire.resolve('tailwindcss/package.json'));
const animationDir = fs.realpathSync(path.join(runtimeDir, 'node_modules/tw-animate-css'));
const cssPath = value => value.replaceAll('\\', '/');
const input = path.join(root, 'assets/tailwind_css.css');
const output = path.join(root, 'content/tailwind_output.css');

const source = fs.readFileSync(input, 'utf8')
  .replace('@import "tailwindcss";',
    `@import "${cssPath(path.join(tailwindDir, 'index.css'))}" source(none);`)
  .replace('@import "tw-animate-css";',
    `@import "${cssPath(path.join(animationDir, 'dist/tw-animate.css'))}";`) + `
@source "../*.html";
@source "./base.bundle.local.js";
@source "./matrix-accessibility.js";
@source "./mobile-sheet-drag.js";
`;

postcss([tailwind({ base: root, optimize: { minify: true } })])
  .process(source, { from: input, to: output, map: false })
  .then(result => {
    fs.writeFileSync(output, result.css);
    console.log(`Built ${path.relative(root, output)} (${result.css.length} characters)`);
  })
  .catch(error => {
    console.error(error);
    process.exitCode = 1;
  });
