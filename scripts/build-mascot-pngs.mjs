import { execFileSync } from 'node:child_process'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const mascots = join(root, 'assets/mascots')
for (const name of ['cat-yarn', 'cat-server']) {
  execFileSync('rsvg-convert', [
    '--width', '512', '--height', '512',
    join(mascots, `${name}.svg`),
    '--output', join(mascots, `${name}.png`),
  ], { stdio: 'inherit' })
}
process.stdout.write('Generated compatibility mascot PNGs from SVG masters.\n')
