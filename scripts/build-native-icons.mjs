import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const logoDirectory = join(root, 'assets/logo')
const sources = [
  { name: 'app-icon', source: join(logoDirectory, 'app-icon.svg') },
  { name: 'app-icon-light', source: join(logoDirectory, 'app-icon-light.svg') },
]
const temporaryDirectory = await mkdtemp(join(tmpdir(), 'liapoldus-icon-'))

async function rasterize(source, size, output) {
  execFileSync('rsvg-convert', ['--width', String(size), '--height', String(size), '--output', output, source], { stdio: 'inherit' })
}

try {
  for (const item of sources) {
    await rasterize(item.source, 1024, join(logoDirectory, `${item.name}.png`))
  }
  const windowsPNG = join(temporaryDirectory, 'windows.png')
  await rasterize(sources[0].source, 256, windowsPNG)
  const png = await readFile(windowsPNG)

  assert.deepEqual([...png.subarray(0, 8)], [137, 80, 78, 71, 13, 10, 26, 10], 'rsvg-convert did not produce a PNG icon')
  const header = Buffer.alloc(22)
  header.writeUInt16LE(1, 2)
  header.writeUInt16LE(1, 4)
  header.writeUInt8(0, 6)
  header.writeUInt8(0, 7)
  header.writeUInt16LE(1, 10)
  header.writeUInt16LE(32, 12)
  header.writeUInt32LE(png.length, 14)
  header.writeUInt32LE(header.length, 18)
  await writeFile(join(logoDirectory, 'windows.ico'), Buffer.concat([header, png]))
} finally {
  await rm(temporaryDirectory, { recursive: true, force: true })
}

process.stdout.write('Generated light/dark 1024px app PNGs and 256px Windows ICO from SVG masters\n')
