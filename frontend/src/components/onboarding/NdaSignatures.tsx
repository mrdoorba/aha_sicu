import { Clock } from 'lucide-react';
import { AHA_SIGNER, type NdaRoute } from '../../mocks/nda';
import { cn } from '../../lib/utils';

/**
 * The two signature blocks at the foot of the NDA.
 *
 * Shared by the brand-facing NDA screen and the internal counter-signature
 * queue so both sides read the same document. A party is rendered one of three
 * ways, and the distinction is the point:
 *
 * - **signed digitally** — the generated script signature
 * - **paper** — a blank ruled line, because that space is for a pen. Printing a
 *   typed signature nobody made would defeat the point of signing by hand.
 * - **not yet signed** — says who it is waiting for, rather than looking blank
 *   in the same way a paper line does.
 */
interface PartyProps {
  caption: string;
  name: string;
  role: string;
  route: NdaRoute | null;
  signed: boolean;
}

const Party = ({ caption, name, role, route, signed }: PartyProps) => (
  <div className="min-w-0 flex-1 basis-36">
    <p className="mb-0.5 text-[11px] text-muted-foreground">{caption}</p>

    {signed && route === 'digital' && (
      <p className="text-3xl leading-tight text-foreground [font-family:'Caveat',cursive]">
        {name}
      </p>
    )}

    {signed && route === 'paper' && (
      <p
        className="h-9 border-b border-foreground/40"
        aria-label={`Tanda tangan ${caption} di atas kertas`}
      />
    )}

    {!signed && (
      <p
        className={cn(
          'flex h-9 items-end gap-1.5 border-b border-dashed border-border',
          'pb-1 text-[11px] font-semibold text-muted-foreground',
        )}
      >
        <Clock className="size-3.5" aria-hidden="true" />
        Menunggu tanda tangan
      </p>
    )}

    <p className="mt-0.5 text-[11px] font-bold text-foreground">{name}</p>
    <p className="text-[11px] text-muted-foreground">{role}</p>
  </div>
);

interface NdaSignaturesProps {
  pic: string;
  picRole: string;
  brandRoute: NdaRoute | null;
  brandSigned: boolean;
  ahaRoute: NdaRoute | null;
  ahaSigned: boolean;
}

export const NdaSignatures = ({
  pic,
  picRole,
  brandRoute,
  brandSigned,
  ahaRoute,
  ahaSigned,
}: NdaSignaturesProps) => (
  <div className="flex flex-wrap gap-6 border-t border-border pt-3">
    <Party
      caption="Pihak Kedua"
      name={pic}
      role={picRole}
      route={brandRoute}
      signed={brandSigned}
    />
    <Party
      caption="Pihak Pertama"
      name={AHA_SIGNER.name}
      role={AHA_SIGNER.role}
      route={ahaRoute}
      signed={ahaSigned}
    />
  </div>
);
