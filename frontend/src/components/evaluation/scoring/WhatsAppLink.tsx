import { ExternalLink } from 'lucide-react';
import { Button } from '../../ui/button';

interface WhatsAppLinkProps {
  link: string;
}

export const WhatsAppLink = ({ link }: WhatsAppLinkProps) => {
  return (
    <Button variant="outline" size="sm" asChild>
      <a href={link} target="_blank" rel="noopener noreferrer">
        <ExternalLink className="mr-1 size-3.5" aria-hidden="true" />
        Open WhatsApp
      </a>
    </Button>
  );
};
