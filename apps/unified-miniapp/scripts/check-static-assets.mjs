import fs from 'node:fs'
import path from 'node:path'

const projectRoot = process.cwd()
const srcRoot = path.join(projectRoot, 'src')
const staticRoot = path.join(srcRoot, 'static')

const SCAN_EXTENSIONS = new Set([
  '.vue',
  '.ts',
  '.js',
  '.json',
  '.scss',
  '.css',
  '.wxml',
  '.wxss',
])

const STATIC_REF_RE = /\/static\/[A-Za-z0-9_./-]+/g

function walkFiles(dir, output = []) {
  if (!fs.existsSync(dir)) return output
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walkFiles(fullPath, output)
      continue
    }
    if (SCAN_EXTENSIONS.has(path.extname(entry.name))) {
      output.push(fullPath)
    }
  }
  return output
}

if (!fs.existsSync(staticRoot)) {
  console.error(`[static-check] missing directory: ${staticRoot}`)
  process.exit(1)
}

const files = walkFiles(srcRoot)
const refs = new Set()

for (const filePath of files) {
  const content = fs.readFileSync(filePath, 'utf8')
  const matches = content.match(STATIC_REF_RE)
  if (!matches) continue
  for (const match of matches) refs.add(match)
}

const missing = []
for (const ref of refs) {
  const relativePath = ref.slice(1).replace(/\//g, path.sep)
  const fullPath = path.join(srcRoot, relativePath)
  if (!fs.existsSync(fullPath)) {
    missing.push({ ref, fullPath })
  }
}

if (missing.length > 0) {
  console.error('[static-check] missing static assets:')
  for (const item of missing) {
    console.error(`  - ${item.ref} -> ${item.fullPath}`)
  }
  process.exit(1)
}

console.log(`[static-check] ok (${refs.size} static refs)`)
