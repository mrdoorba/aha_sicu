import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card, CardContent } from './card';

describe('Card', () => {
  it('clips overflow so wide content scrolls instead of overflowing', () => {
    render(
      <Card data-testid="card">
        <CardContent>
          <div className="overflow-x-auto">
            <table>
              <tbody>
                <tr>
                  <td className="whitespace-nowrap">
                    {'Very long content that should cause overflow '.repeat(20)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    );

    const card = screen.getByTestId('card');
    expect(card.className).toContain('overflow-hidden');
  });

  it('renders normal-width content without overflow-related issues', () => {
    render(
      <Card data-testid="card">
        <CardContent>
          <p>Short content</p>
        </CardContent>
      </Card>
    );

    const card = screen.getByTestId('card');
    expect(card.className).toContain('overflow-hidden');
    expect(card.textContent).toBe('Short content');
  });
});
