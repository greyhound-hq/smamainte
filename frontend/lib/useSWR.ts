// Compatibility wrapper for SWR default vs named export differences across environments
import * as swr from 'swr'

const _useSWR: any = (swr as any).default ?? (swr as any)

export default _useSWR
