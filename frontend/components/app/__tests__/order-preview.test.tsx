import React from 'react';
import { render, screen } from '@testing-library/react';
import OrderPreview from '../order-preview';

// Mock the CSS module or just ignore it since we use global css / tailwind
// But we might need to mock matchMedia if used, but here it's simple.

describe('OrderPreview', () => {
  const mockOrder = {
    name: 'Alice',
    drinkType: 'Latte',
    size: 'Large',
    milk: 'Oat',
    extras: ['Sugar', 'Cinnamon'],
  };

  it('renders order details correctly', () => {
    render(<OrderPreview order={mockOrder} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Large Latte')).toBeInTheDocument();
    expect(screen.getByText('Oat')).toBeInTheDocument();
    expect(screen.getByText('Sugar, Cinnamon')).toBeInTheDocument();
  });

  it('renders empty state correctly', () => {
    render(<OrderPreview order={{}} />);
    
    // Check for placeholders
    const dashes = screen.getAllByText('—');
    expect(dashes.length).toBeGreaterThan(0);
    expect(screen.getAllByText('None').length).toBeGreaterThan(0);
  });
});
