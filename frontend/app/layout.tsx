import type { ReactNode } from 'react';

export const metadata = {
  title: 'Pokemon Cardmarket Valuator',
  description: 'Open-source MVP scaffold'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
