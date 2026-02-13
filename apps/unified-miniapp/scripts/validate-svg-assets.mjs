import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const appRoot = path.resolve(scriptDir, '..')
const illustrationsRoot = path.join(appRoot, 'src', 'static', 'illustrations')

function walkSvgFiles(dir, output = []) {
  if (!fs.existsSync(dir)) return output

  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walkSvgFiles(fullPath, output)
      continue
    }
    if (path.extname(entry.name).toLowerCase() === '.svg') {
      output.push(fullPath)
    }
  }

  return output
}

function validateSvgContent(content, relativePath) {
  const errors = []

  if (!/\bviewBox\s*=\s*["'][^"']+["']/.test(content)) {
    errors.push(`${relativePath}: missing required viewBox attribute`)
  }

  if (/<style[\s>]/i.test(content)) {
    errors.push(`${relativePath}: forbidden <style> tag detected`)
  }

  if (/\b(width|height)\s*=\s*["'][^"']*%[^"']*["']/i.test(content)) {
    errors.push(`${relativePath}: percentage width/height is forbidden`)
  }

  return errors
}

if (!fs.existsSync(illustrationsRoot)) {
  console.error(`[svg-validate] missing illustrations directory: ${illustrationsRoot}`)
  process.exit(1)
}

const svgFiles = walkSvgFiles(illustrationsRoot)
if (svgFiles.length === 0) {
  console.error('[svg-validate] no svg files found under src/static/illustrations')
  process.exit(1)
}

const validationErrors = []

for (const svgFilePath of svgFiles) {
  const content = fs.readFileSync(svgFilePath, 'utf8')
  const relativePath = path.relative(appRoot, svgFilePath).replace(/\\/g, '/')
  validationErrors.push(...validateSvgContent(content, relativePath))
}

if (validationErrors.length > 0) {
  console.error(`[svg-validate] invalid svg assets (${validationErrors.length} errors):`)
  for (const error of validationErrors) {
    console.error(`  - ${error}`)
  }
  process.exit(1)
}

console.log(`[svg-validate] all svg assets valid (${svgFiles.length} files)`)
