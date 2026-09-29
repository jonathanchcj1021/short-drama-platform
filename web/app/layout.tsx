import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import AuthBootstrap from '@/components/AuthBootstrap';
import './globals.css';

export const metadata: Metadata = {
  title: '短劇平台',
  description: '線上短劇串流平台',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-Hant">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AuthBootstrap />
        <Navbar />
        {children}
        <footer className="appFooter">
          短劇平台 · v{process.env.NEXT_PUBLIC_APP_VERSION ?? '1.0.0'}
        </footer>
      </body>
    </html>
  );
}
