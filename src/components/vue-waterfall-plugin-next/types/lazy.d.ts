/*
 * @Author: Yaowen Liu
 * @Date: 2022-03-18 14:11:45
 * @LastEditors: Yaowen Liu
 * @LastEditTime: 2023-04-10 12:37:21
 */
import type Lazy from '../utils/Lazy'

export type CallbackFunction = (value: boolean) => void

export interface LazyOptions {
    error?: string
    loading?: string
    observerOptions?: IntersectionObserverInit
    log?: boolean
    ratioCalculator?: (width: number, height: number) => number
}

export interface ValueFormatterObject {
    src: string
    error?: string
    loading?: string
}

export type LazyType = InstanceType<typeof Lazy>
