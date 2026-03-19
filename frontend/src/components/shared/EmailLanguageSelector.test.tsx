import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { EmailLanguageSelector } from './EmailLanguageSelector';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const map: Record<string, string> = {
        'emailLanguageSelector.label': 'Email Language',
      };
      return map[key] ?? key;
    },
  }),
}));

describe('EmailLanguageSelector', () => {
  it('should render a dropdown with 3 language options', () => {
    render(<EmailLanguageSelector value="id" onChange={vi.fn()} />);

    const select = screen.getByTestId('email-language-select');
    expect(select).toBeInTheDocument();

    const options = select.querySelectorAll('option');
    expect(options).toHaveLength(3);
  });

  it('should display the label text', () => {
    render(<EmailLanguageSelector value="id" onChange={vi.fn()} />);

    expect(screen.getByText('Email Language')).toBeInTheDocument();
  });

  it('should display the current value as selected when value is id', () => {
    render(<EmailLanguageSelector value="id" onChange={vi.fn()} />);

    const select = screen.getByTestId('email-language-select') as HTMLSelectElement;
    expect(select.value).toBe('id');
  });

  it('should display the current value as selected when value is en', () => {
    render(<EmailLanguageSelector value="en" onChange={vi.fn()} />);

    const select = screen.getByTestId('email-language-select') as HTMLSelectElement;
    expect(select.value).toBe('en');
  });

  it('should display the current value as selected when value is th', () => {
    render(<EmailLanguageSelector value="th" onChange={vi.fn()} />);

    const select = screen.getByTestId('email-language-select') as HTMLSelectElement;
    expect(select.value).toBe('th');
  });

  it('should call onChange with the new language code when user selects a different option', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();

    render(<EmailLanguageSelector value="id" onChange={onChange} />);

    const select = screen.getByTestId('email-language-select');
    await user.selectOptions(select, 'th');

    expect(onChange).toHaveBeenCalledWith('th');
  });

  it('should render without errors for each valid language code', () => {
    const codes = ['id', 'en', 'th'] as const;

    for (const code of codes) {
      const { unmount } = render(
        <EmailLanguageSelector value={code} onChange={vi.fn()} />,
      );
      expect(screen.getByTestId('email-language-select')).toBeInTheDocument();
      unmount();
    }
  });

  it('should apply custom className', () => {
    const { container } = render(
      <EmailLanguageSelector value="id" onChange={vi.fn()} className="my-custom-class" />,
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('my-custom-class');
  });
});
