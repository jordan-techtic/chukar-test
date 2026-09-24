import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Spinner } from '@/components/ui/spinner';

describe('Spinner', () => {
  it('renders with accessible label', () => {
    render(<Spinner label="Loading session" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading session')).toBeInTheDocument();
  });
});
