import { useState } from 'react';
import { Play } from 'lucide-react';
import { SUBACCOUNT_VIDEOS } from '../../mocks/onboarding';
import { cn } from '../../lib/utils';

/**
 * Marwah's sub-account walkthrough, in Indonesian or English.
 *
 * The iframe is only mounted once the viewer presses play: two auto-loaded
 * YouTube embeds would otherwise cost every brand a couple of megabytes and a
 * set of third-party cookies to look at a page most of them will read instead.
 * `youtube-nocookie` for the same reason.
 */
export const TutorialVideo = () => {
  const [lang, setLang] = useState(SUBACCOUNT_VIDEOS[0]);
  const [playing, setPlaying] = useState(false);

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-4">
        <div>
          <h2 className="text-[15px] font-extrabold text-foreground">Video panduan</h2>
          <p className="text-[13px] text-muted-foreground">
            Langkah yang sama, dijelaskan dari awal sampai selesai.
          </p>
        </div>

        <div
          className="inline-flex gap-1 rounded-full bg-secondary p-1"
          role="group"
          aria-label="Bahasa video"
        >
          {SUBACCOUNT_VIDEOS.map((video) => (
            <button
              key={video.code}
              type="button"
              aria-pressed={video.code === lang.code}
              onClick={() => {
                setLang(video);
                // Switching language swaps the source, so drop back to the
                // poster rather than silently restarting a different video.
                setPlaying(false);
              }}
              className={cn(
                'rounded-full px-3.5 py-1.5 text-[13px] font-bold transition-colors',
                video.code === lang.code
                  ? 'bg-card text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              <span aria-hidden="true">{video.flag}</span> {video.label}
            </button>
          ))}
        </div>
      </div>

      <div className="relative aspect-video bg-secondary">
        {playing ? (
          <iframe
            key={lang.youtubeId}
            src={`https://www.youtube-nocookie.com/embed/${lang.youtubeId}?autoplay=1`}
            title={`Tutorial sub akun — ${lang.label}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture"
            allowFullScreen
            className="absolute inset-0 size-full border-0"
          />
        ) : (
          <button
            type="button"
            onClick={() => setPlaying(true)}
            className="group absolute inset-0 grid place-items-center"
            aria-label={`Putar tutorial sub akun dalam ${lang.label}`}
          >
            <img
              src={`https://i.ytimg.com/vi/${lang.youtubeId}/hqdefault.jpg`}
              alt=""
              aria-hidden="true"
              loading="lazy"
              className="absolute inset-0 size-full object-cover"
            />
            <span className="relative grid size-16 place-items-center rounded-full bg-primary shadow-lg transition-transform group-hover:scale-105">
              <Play className="size-7 fill-current text-primary-foreground" aria-hidden="true" />
            </span>
          </button>
        )}
      </div>
    </div>
  );
};
