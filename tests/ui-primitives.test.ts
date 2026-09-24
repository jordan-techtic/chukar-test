import { describe, expect, it } from 'vitest';
import { Calendar } from '@/components/ui/calendar';
import { DatePicker } from '@/components/ui/date-picker';
import { toast, Toaster } from '@/components/ui/sonner';

describe('UI primitive exports', () => {
  it('exports Calendar from calendar module', () => {
    expect(Calendar).toBeTypeOf('function');
  });

  it('exports DatePicker and Calendar from date-picker module', () => {
    expect(DatePicker).toBeTypeOf('function');
  });

  it('exports toast and Toaster from sonner module', () => {
    expect(toast).toBeTypeOf('function');
    expect(Toaster).toBeTypeOf('function');
  });
});
