import React from 'react';

interface OrderPreviewProps {
  order: {
    drinkType?: string;
    size?: string;
    milk?: string;
    extras?: string[];
    name?: string;
  };
}

export default function OrderPreview({ order }: OrderPreviewProps) {
  return (
    <div className="order-preview-card coffee-card p-6">
      <h2 className="text-2xl font-bold mb-4 coffee-accent">Order Preview</h2>
      <div className="space-y-2">
        <p><strong className="coffee-accent">Customer:</strong> {order.name ?? '—'}</p>
        <p><strong className="coffee-accent">Item:</strong> {order.size ?? '—'} {order.drinkType ?? '—'}</p>
        <p><strong className="coffee-accent">Milk:</strong> {order.milk ?? 'None'}</p>
        <p><strong className="coffee-accent">Extras:</strong> {order.extras && order.extras.length > 0 ? order.extras.join(', ') : 'None'}</p>
      </div>
    </div>
  );
}
