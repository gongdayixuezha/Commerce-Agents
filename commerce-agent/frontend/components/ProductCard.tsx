interface Product {
  id: string;
  name: string;
  price: number;
  brand: string;
  rating: number;
  sales_count: number;
  stock: number;
  image_url: string;
  description?: string;
}

export default function ProductCard({ product, index }: { product: Product; index?: number }) {
  return (
    <div className="border rounded-xl p-3 bg-white hover:shadow-md transition-shadow w-full">
      {index && (
        <span className="text-xs text-gray-400 font-mono">#{index}</span>
      )}
      <div className="aspect-square bg-gray-100 rounded-lg mb-2 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      </div>
      <h3 className="font-semibold text-sm truncate" title={product.name}>
        {product.name}
      </h3>
      <div className="flex justify-between items-center mt-1">
        <span className="text-lg font-bold text-red-600">¥{product.price.toFixed(2)}</span>
        <span className="text-yellow-500 text-sm">★ {product.rating}</span>
      </div>
      <p className="text-xs text-gray-400 mt-0.5">
        {product.brand} | 已售 {product.sales_count}
      </p>
    </div>
  );
}
