'use client';

import { useMemo } from 'react';
import GithubSlugger from 'github-slugger';

const SKIPPED_HEADINGS = new Set(['overview', 'نظرة عامة', 'table of contents', 'الفهرس']);

interface NotesTableOfContentsProps {
  markdown: string;
  isRtl?: boolean;
}

export function NotesTableOfContents({ markdown, isRtl }: NotesTableOfContentsProps) {
  const items = useMemo(() => {
    const slugger = new GithubSlugger();
    const headingLines = markdown
      .split('\n')
      .map((line) => line.match(/^##\s+(.+)$/)?.[1]?.trim())
      .filter((title): title is string => Boolean(title));

    return headingLines
      .filter((title) => !SKIPPED_HEADINGS.has(title.toLowerCase()))
      .map((title) => ({ title, slug: slugger.slug(title) }));
  }, [markdown]);

  if (items.length === 0) return null;

  const handleClick = (slug: string) => {
    document.getElementById(slug)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <nav
      dir={isRtl ? 'rtl' : 'ltr'}
      className="flex flex-col gap-1.5 rounded-lg border border-border/60 bg-secondary/40 p-4"
    >
      {items.map((item) => (
        <button
          key={item.slug}
          type="button"
          onClick={() => handleClick(item.slug)}
          className="text-start text-sm text-muted-foreground hover:text-foreground transition-colors truncate"
        >
          {item.title}
        </button>
      ))}
    </nav>
  );
}
