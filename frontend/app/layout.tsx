import './globals.css';
import { Outfit } from 'next/font/google';

const outfit = Outfit({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-outfit'
});

export const metadata = {
  title: 'AI Doubt Resolution Hub',
  description: 'Sequential Multi-Agent Doubt Resolution System for modern students.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${outfit.variable} dark`}>
      <body className="font-sans antialiased bg-[#080b11] text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
