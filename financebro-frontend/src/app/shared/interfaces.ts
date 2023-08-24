export type ProductKeys = '3months' | '6months'

export interface Product {
  id: string
  name: string
  price: number
}

export interface Environment {
  production: boolean
  appVersion: string
  products: Map<ProductKeys, Product>
  USERDATA_KEY: string
  apiUrl: string
  appThemeName: string
  sentryDns: string
  websiteUrl: string
}
