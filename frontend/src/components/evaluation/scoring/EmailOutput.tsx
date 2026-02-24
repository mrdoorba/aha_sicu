import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../../ui/button';
import { Card, CardContent } from '../../ui/card';
import { Copy, Check } from 'lucide-react';

interface EmailOutputProps {
  subject: string;
  body: string;
}

export const EmailOutput = ({ subject, body }: EmailOutputProps) => {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const fullText = `Subject: ${subject}\n\n${body}`;
    await navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-sm font-semibold">{t('emailOutput.title')}</p>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? (
              <Check className="mr-1 size-3.5" aria-hidden="true" />
            ) : (
              <Copy className="mr-1 size-3.5" aria-hidden="true" />
            )}
            {copied ? t('emailOutput.copied') : t('emailOutput.copy')}
          </Button>
        </div>
        <p className="mb-2 text-xs text-muted-foreground">{subject}</p>
        <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">
          {body}
        </pre>
      </CardContent>
    </Card>
  );
};
