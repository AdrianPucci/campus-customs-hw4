// Matches what the backend's /api/products returns for each catalogue row.
export interface SizeStock {
  size: string
  quantity: number
}

export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_file_path: string // from the database, e.g. "products/yale-mom-hoodie.jpg"
  image_url: string // what the browser loads, e.g. "/media/products/yale-mom-hoodie.jpg"
  price: number
  inventory: SizeStock[]
  total_stock: number
}
