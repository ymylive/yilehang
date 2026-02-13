const childProcess = require('child_process')

function quoteArg(value) {
  const text = String(value)
  if (text.length === 0) {
    return '""'
  }
  if (/^[A-Za-z0-9_./:-]+$/.test(text)) {
    return text
  }
  return `"${text.replace(/"/g, '\\"')}"`
}

// Node 24 on Windows can throw EINVAL when spawning *.cmd directly.
if (process.platform === 'win32' && !childProcess.__uniAutomatorCmdSpawnPatched) {
  const originalSpawn = childProcess.spawn

  childProcess.spawn = function patchedSpawn(command, args = [], options) {
    if (typeof command === 'string' && command.toLowerCase().endsWith('.cmd')) {
      const cmdLine = [quoteArg(command), ...args.map(quoteArg)].join(' ')
      return originalSpawn.call(this, 'cmd.exe', ['/d', '/s', '/c', cmdLine], options)
    }

    return originalSpawn.call(this, command, args, options)
  }

  childProcess.__uniAutomatorCmdSpawnPatched = true
}

module.exports = require('@dcloudio/uni-automator/dist/environment.js')
