import '@testing-library/jest-dom/vitest'
import { beforeAll, afterAll, vi } from 'vitest'

const shouldIgnoreConsoleWarn = (args) => {
    const message = args.map((arg) => String(arg)).join(' ')
    return message.includes('React Router Future Flag Warning')
}

const originalWarn = console.warn

beforeAll(() => {
    vi.spyOn(console, 'warn').mockImplementation((...args) => {
        if (shouldIgnoreConsoleWarn(args)) {
            return
        }
        originalWarn(...args)
    })
})

afterAll(() => {
    vi.restoreAllMocks()
})
